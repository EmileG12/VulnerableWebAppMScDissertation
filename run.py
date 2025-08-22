#!/usr/bin/env python3
"""
Main entry point for the Vulnerable Web Application
Run this script to start the Flask development server
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

from VulnerableApp import create_app

def main():
    """Main function to run the Flask application"""
    app = create_app()
    
    # Ensure instance directory exists
    instance_dir = current_dir / 'instance'
    instance_dir.mkdir(exist_ok=True)
    
    print("🚨 VULNERABLE WEB APPLICATION")
    print("=" * 40)
    print("⚠️  WARNING: This application contains intentional security vulnerabilities!")
    print("   - CSRF vulnerabilities")
    print("   - SQL injection vulnerabilities")
    print("   - Session hijacking vulnerabilities")
    print("   - Only use for educational purposes!")
    print("=" * 40)
    print(f"🌐 Starting server on http://localhost:5000")
    print(f"📁 Database location: {instance_dir / 'db.sqlite'}")
    print("🔑 Default credentials:")
    print("   Username: Jacksparrow, Password: princess")
    print("   Username: Barbossa, Password: Blackpearl")
    print("   Username: Johnnydepp, Password: Pirates")
    print("=" * 40)
    print("Press Ctrl+C to stop the server")
    print()
    
    try:
        app.run(
            host='0.0.0.0',  # Accept connections from any IP
            port=5000,
            debug=True,      # Enable debug mode for development
            use_reloader=False  # Disable reloader to avoid double startup messages
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
