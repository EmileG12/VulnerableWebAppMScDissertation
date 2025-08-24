#!/bin/bash

# Vulnerable Web Application Launch Script for Linux/Unix
# This script sets up the environment and launches the Flask application

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${RED}🚨 VULNERABLE WEB APPLICATION LAUNCHER${NC}"
echo "=========================================="
echo -e "${YELLOW}⚠️  WARNING: This application contains intentional security vulnerabilities!${NC}"
echo "   - CSRF vulnerabilities"
echo "   - SQL injection vulnerabilities" 
echo "   - Session hijacking vulnerabilities"
echo -e "${YELLOW}   - Only use for educational purposes!${NC}"
echo "=========================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo -e "${RED}❌ Error: Python is not installed or not in PATH${NC}"
        echo "Please install Python 3.7+ and try again"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo -e "${BLUE}🐍 Using Python: $($PYTHON_CMD --version)${NC}"

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    if ! command -v pip &> /dev/null; then
        echo -e "${RED}❌ Error: pip is not installed${NC}"
        echo "Please install pip and try again"
        exit 1
    else
        PIP_CMD="pip"
    fi
else
    PIP_CMD="pip3"
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
    $PYTHON_CMD -m venv .venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to create virtual environment${NC}"
        exit 1
    fi
fi

# Activate virtual environment
echo -e "${YELLOW}🔧 Activating virtual environment...${NC}"
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
else
    echo -e "${RED}❌ Error: Virtual environment activation script not found${NC}"
    echo "Expected: .venv/bin/activate"
    echo "Please ensure the virtual environment was created successfully"
    exit 1
fi

# Check if pip needs upgrading
echo -e "${YELLOW}📦 Checking pip version...${NC}"
CURRENT_PIP=$(pip --version | awk '{print $2}')
if command -v curl &> /dev/null; then
    LATEST_PIP=$(curl -s https://pypi.org/pypi/pip/json | grep -o '"version":"[^"]*"' | head -1 | cut -d'"' -f4 2>/dev/null || echo "$CURRENT_PIP")
elif command -v wget &> /dev/null; then
    LATEST_PIP=$(wget -qO- https://pypi.org/pypi/pip/json | grep -o '"version":"[^"]*"' | head -1 | cut -d'"' -f4 2>/dev/null || echo "$CURRENT_PIP")
else
    LATEST_PIP="$CURRENT_PIP"  # Skip check if no curl/wget
fi

if [ "$CURRENT_PIP" != "$LATEST_PIP" ] && [ "$LATEST_PIP" != "$CURRENT_PIP" ]; then
    echo -e "${YELLOW}📦 Upgrading pip from $CURRENT_PIP to $LATEST_PIP...${NC}"
    pip install --upgrade pip
else
    echo -e "${GREEN}✅ Pip is already up to date ($CURRENT_PIP)${NC}"
fi

# Install requirements with smart checking
if [ -f "requirements.txt" ]; then
    echo -e "${YELLOW}📦 Checking requirements...${NC}"
    
    # Check if all packages are already satisfied
    if pip check >/dev/null 2>&1; then
        # Double-check by trying to import key packages
        if python -c "import flask, flask_sqlalchemy, flask_login, requests" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ All requirements already satisfied${NC}"
        else
            echo -e "${YELLOW}📦 Installing missing requirements...${NC}"
            pip install -r requirements.txt --quiet
            if [ $? -ne 0 ]; then
                echo -e "${RED}❌ Failed to install requirements${NC}"
                exit 1
            fi
        fi
    else
        echo -e "${YELLOW}📦 Installing/updating requirements...${NC}"
        pip install -r requirements.txt --quiet
        if [ $? -ne 0 ]; then
            echo -e "${RED}❌ Failed to install requirements${NC}"
            exit 1
        fi
    fi
else
    echo -e "${YELLOW}📦 Checking Flask installation...${NC}"
    if python -c "import flask; print('Flask version:', flask.__version__)" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Flask is already installed${NC}"
    else
        echo -e "${YELLOW}📦 Installing Flask manually...${NC}"
        pip install Flask==2.3.3 Werkzeug==2.3.7
        if [ $? -ne 0 ]; then
            echo -e "${RED}❌ Failed to install Flask${NC}"
            exit 1
        fi
    fi
fi

# Create instance directory
mkdir -p instance

# Set Flask environment variables
export FLASK_APP=VulnerableApp
export FLASK_ENV=development
export FLASK_DEBUG=1

echo -e "${GREEN}✅ Environment setup complete!${NC}"
echo ""
echo -e "${GREEN}🚀 Starting Vulnerable Web Application...${NC}"
echo -e "${BLUE}🌐 Server will be available at: http://localhost:5000${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Launch the application using flask run
flask run --host=0.0.0.0 --port=5000

# Deactivate virtual environment when done
deactivate
