#!/usr/bin/env python3
"""
Deployment script for MedPro Flask application
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"  Error: {e.stderr}")
        sys.exit(1)

def main():
    print("🚀 Starting MedPro deployment...")
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("✗ Error: app.py not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Install dependencies
    run_command("pip install -r requirements.txt", "Installing Python dependencies")
    
    # Create database tables
    print("📊 Setting up database...")
    try:
        import app
        app.create_tables()
        print("✓ Database setup completed")
    except Exception as e:
        print(f"⚠ Database setup warning: {e}")
    
    # Test the application
    print("🧪 Testing application...")
    try:
        import app
        print("✓ Application imports successfully")
    except Exception as e:
        print(f"✗ Application test failed: {e}")
        sys.exit(1)
    
    print("\n🎉 Deployment preparation completed successfully!")
    print("\nNext steps:")
    print("1. Commit your changes to git")
    print("2. Push to your repository")
    print("3. Connect your repository to Netlify")
    print("4. Deploy!")
    
    print("\nFor local testing, run:")
    print("  python app.py")

if __name__ == "__main__":
    main()

