#!/usr/bin/env python3
"""
Quick setup script for local AI-powered Ajio automation
"""

import os
import sys
import subprocess
import platform

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print(f"❌ Python {version.major}.{version.minor} is not supported. Please install Python 3.7 or higher.")
        return False
    print(f"✅ Python {version.major}.{version.minor} is compatible")
    return True

def check_groq_api_key():
    """Check if Groq API key is set"""
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("⚠️ GROQ_API_KEY not found in environment variables")
        print("📝 To get a free API key:")
        print("   1. Visit https://console.groq.com")
        print("   2. Create an account")
        print("   3. Generate an API key")
        print("   4. Set it in your environment:")
        if platform.system() == "Windows":
            print("      set GROQ_API_KEY=your_key_here")
        else:
            print("      export GROQ_API_KEY=your_key_here")
        return False
    print("✅ GROQ_API_KEY found in environment")
    return True

def install_dependencies():
    """Install required Python packages"""
    packages = [
        "playwright>=1.40.0",
        "groq>=0.4.0",
        "flask>=3.0.0",
        "flask-sqlalchemy>=3.1.0",
        "aiohttp>=3.9.0",
        "beautifulsoup4>=4.12.0",
        "typer>=0.9.0",
        "sqlalchemy>=2.0.0",
        "email-validator>=2.1.0",
        "pytest>=7.4.0",
        "pytest-asyncio>=0.21.0"
    ]
    
    for package in packages:
        if not run_command(f"pip install {package}", f"Installing {package.split('>=')[0]}"):
            return False
    return True

def install_browser():
    """Install Playwright browser"""
    return run_command("playwright install chromium", "Installing Chromium browser")

def test_installation():
    """Test if everything is working"""
    print("\n🧪 Testing installation...")
    
    # Test imports
    test_commands = [
        ("python -c 'import playwright; print(\"Playwright: OK\")'", "Testing Playwright"),
        ("python -c 'import groq; print(\"Groq: OK\")'", "Testing Groq library"),
        ("python -c 'import flask; print(\"Flask: OK\")'", "Testing Flask"),
        ("python -c 'from agents.ai_vision_agent import AIVisionAgent; print(\"AI Agent: OK\")'", "Testing AI Vision Agent")
    ]
    
    all_passed = True
    for command, description in test_commands:
        if not run_command(command, description):
            all_passed = False
    
    return all_passed

def main():
    """Main setup function"""
    print("🤖 AI-Powered Ajio Automation - Local Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check if pip is available
    if not run_command("pip --version", "Checking pip availability"):
        print("💡 Try installing pip: python -m ensurepip --upgrade")
        sys.exit(1)
    
    # Install dependencies
    print("\n📦 Installing Python dependencies...")
    if not install_dependencies():
        print("❌ Failed to install some dependencies")
        sys.exit(1)
    
    # Install browser
    print("\n🌐 Installing browser for automation...")
    if not install_browser():
        print("❌ Failed to install browser")
        print("💡 Try running manually: playwright install chromium")
        sys.exit(1)
    
    # Test installation
    if not test_installation():
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)
    
    # Check API key
    print("\n🔑 Checking API configuration...")
    has_api_key = check_groq_api_key()
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    
    if not has_api_key:
        print("1. ⚠️ Set up your Groq API key (see instructions above)")
        print("2. 🚀 Run: python run_smart.py")
    else:
        print("1. 🚀 Run: python run_smart.py")
        print("2. 📖 Check LOCAL_SETUP_AI.md for detailed usage")
    
    print("\n🧠 Available modes:")
    print("   • python run_smart.py    (AI-powered with Groq)")
    print("   • python run_stealth.py  (Stealth mode)")
    print("   • python run_local.py    (Standard mode)")
    
    print("\n💡 Tips:")
    print("   • Use HEADLESS=false to see the browser")
    print("   • Check logs for AI decision-making process")
    print("   • Run python test_ai_vision.py to test AI features")

if __name__ == "__main__":
    main()