# 🧠 AI-Powered Ajio.com Automation - Local Setup Guide

## Overview

This guide helps you set up the AI-powered Ajio.com automation system on your local machine. The system now features intelligent login detection using Groq LLM, making it much more robust and adaptable to website changes.

## Prerequisites

- **Python 3.7+** (Python 3.11 recommended)
- **Git** (to clone the repository)
- **Internet connection** (for Groq API and browser automation)
- **Groq API Key** (free account available at https://console.groq.com)

## Quick Start (5 minutes)

### 1. Clone and Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd ajio-automation

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install browser (required for automation)
playwright install chromium
```

### 2. Get Groq API Key
1. Visit https://console.groq.com
2. Create a free account
3. Generate an API key
4. Set the environment variable:

```bash
# Linux/Mac
export GROQ_API_KEY="your_groq_api_key_here"

# Windows
set GROQ_API_KEY=your_groq_api_key_here
```

### 3. Run AI-Powered Automation
```bash
# AI-powered mode (recommended)
python run_smart.py

# Alternative modes
python run_stealth.py  # Stealth mode with anti-detection
python run_local.py    # Standard mode
```

## 🧠 AI Features Explained

### Smart Login Detection
- **What it does**: Analyzes web pages using Groq LLM to find login buttons intelligently
- **Why it's better**: Adapts to website changes automatically, no hardcoded selectors
- **How it works**: Takes page screenshot, extracts elements, analyzes with AI, generates selectors

### Stealth Browser Automation
- **Anti-detection measures**: Random user agents, human-like mouse movements, realistic delays
- **Access denied bypass**: Multiple strategies to avoid being blocked
- **Popup handling**: Intelligent popup detection and dismissal

### Adaptive Form Filling
- **Smart field detection**: AI identifies phone/email/password fields automatically
- **Multiple fallback strategies**: If one method fails, tries alternatives
- **Natural language understanding**: Understands form context and structure

## Detailed Setup Steps

### 1. System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv git
```

**macOS:**
```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python git
```

**Windows:**
1. Download Python from https://python.org/downloads/
2. Install Git from https://git-scm.com/downloads
3. Add Python to PATH during installation

### 2. Project Setup

```bash
# Clone the project
git clone <your-repo-url>
cd ajio-automation

# Create virtual environment
python -m venv ajio-env
source ajio-env/bin/activate  # Linux/Mac
# ajio-env\Scripts\activate  # Windows

# Verify Python version
python --version  # Should be 3.7 or higher
```

### 3. Install Dependencies

```bash
# Install Python packages
pip install --upgrade pip
pip install -r requirements.txt

# Install browser for automation
playwright install chromium

# Verify installation
python -c "from playwright.sync_api import sync_playwright; print('Playwright installed successfully')"
python -c "from groq import Groq; print('Groq library installed successfully')"
```

### 4. Environment Configuration

Create a `.env` file in the project root:
```bash
# .env file
GROQ_API_KEY=your_groq_api_key_here
HEADLESS=false  # Set to true for headless mode
DEBUG=true
```

Or set environment variables directly:
```bash
# Linux/Mac
export GROQ_API_KEY="your_groq_api_key_here"
export HEADLESS=false
export DEBUG=true

# Windows
set GROQ_API_KEY=your_groq_api_key_here
set HEADLESS=false
set DEBUG=true
```

## Usage Examples

### 1. AI-Powered Smart Mode (Recommended)
```bash
python run_smart.py
```
**Features:**
- Groq LLM for intelligent element detection
- Adaptive page analysis
- Smart form filling
- Human-like behavior simulation

### 2. Stealth Mode
```bash
python run_stealth.py
```
**Features:**
- Enhanced anti-detection measures
- Multiple user agent rotation
- Access denied bypass
- Realistic browsing patterns

### 3. Standard Mode
```bash
python run_local.py
```
**Features:**
- Traditional selector-based automation
- Faster execution
- Reliable for stable websites

### 4. Command Line Options
```bash
# AI mode with specific phone number
python run_smart.py

# Check saved orders
python run_smart.py --list-orders

# Check return reminders
python run_smart.py --check-reminders

# View help
python run_smart.py --help
```

## Step-by-Step Workflow

### What Happens When You Run the Automation:

1. **Browser Launch** 🌐
   - Opens Chrome/Chromium browser
   - Applies stealth configurations
   - Sets realistic user agent

2. **Navigate to Ajio** 🔗
   - Goes to ajio.com
   - Handles popups automatically
   - Simulates human browsing behavior

3. **AI Login Detection** 🧠
   - Takes page screenshot
   - Analyzes page structure with Groq LLM
   - Identifies login button intelligently
   - Provides reasoning for decisions

4. **Smart Login Process** 📱
   - Clicks login button using AI analysis
   - Detects login form fields automatically
   - Enters your phone number
   - Waits for OTP input from you

5. **Order Scraping** 📦
   - Navigates to orders page
   - Extracts order information
   - Saves to local database
   - Shows summary of found orders

6. **Return Management** 🔄
   - Processes return/replace commands
   - Uses natural language understanding
   - Executes browser actions automatically

## Troubleshooting

### Common Issues and Solutions

**1. Groq API Key Issues**
```bash
# Verify API key is set
echo $GROQ_API_KEY  # Linux/Mac
echo %GROQ_API_KEY%  # Windows

# Test API connectivity
python -c "
import os
from groq import Groq
client = Groq(api_key=os.getenv('GROQ_API_KEY'))
response = client.chat.completions.create(
    model='llama3-70b-8192',
    messages=[{'role': 'user', 'content': 'Hello'}],
    max_tokens=10
)
print('API working:', response.choices[0].message.content)
"
```

**2. Browser Installation Issues**
```bash
# Reinstall browser
playwright uninstall chromium
playwright install chromium

# Install system dependencies (Linux)
sudo playwright install-deps
```

**3. Access Denied Errors**
- Try stealth mode: `python run_stealth.py`
- Use different user agent
- Wait longer between requests
- Check your IP isn't blocked

**4. Element Not Found**
- AI provides reasoning in output
- Try running with visible browser (HEADLESS=false)
- Check if website layout changed
- Review AI analysis logs

**5. Import Errors**
```bash
# Reinstall dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# Check virtual environment
which python  # Should point to venv
```

### Debug Mode

Run with debug information:
```bash
# Enable debug logging
export DEBUG=true
python run_smart.py

# Run with visible browser
export HEADLESS=false
python run_smart.py
```

## AI Analysis Examples

### Example 1: Successful Login Detection
```
🤖 Starting AI-powered login detection...
🎯 AI found login element: 'Sign In'
📍 Confidence: high
💭 Reasoning: Found button with 'Sign In' text in navigation area, positioned top-right, commonly used for login
✅ Successfully clicked AI-identified login element
```

### Example 2: Form Analysis
```
🤖 Using AI to analyze login form...
📱 AI found phone field: input[name="username"]
✅ Phone number entered using AI detection
✅ Send OTP clicked using AI detection
```

## Performance Tips

1. **Use Virtual Environment** - Isolates dependencies
2. **Set HEADLESS=true** - Faster execution in production
3. **Cache Browser** - Browser stays installed between runs
4. **Monitor API Usage** - Groq has rate limits
5. **Use SSD Storage** - Faster database operations

## Security Best Practices

1. **Environment Variables** - Never hardcode API keys
2. **Virtual Environment** - Isolate project dependencies
3. **Firewall Rules** - Allow only necessary network access
4. **Regular Updates** - Keep dependencies updated
5. **API Key Rotation** - Rotate Groq API keys periodically

## Folder Structure After Setup

```
ajio-automation/
├── agents/                 # AI agents
│   ├── ai_vision_agent.py  # Groq LLM integration
│   ├── smart_login_agent.py # AI-powered login
│   └── ...
├── run_smart.py           # AI-powered entry point
├── run_stealth.py         # Stealth mode entry point
├── requirements.txt       # Dependencies
├── orders.db             # Local database (auto-created)
├── .env                  # Environment variables
└── ajio-env/             # Virtual environment
```

## Next Steps

After successful setup:

1. **Test AI Features**: `python test_ai_vision.py`
2. **Run Demo Mode**: Start with demo to see workflow
3. **Check Documentation**: Review `ai_vision_guide.md`
4. **Monitor Logs**: Watch AI decision-making process
5. **Customize Settings**: Modify `config.py` as needed

## Support

- **AI Issues**: Check Groq API status and quota
- **Browser Issues**: Reinstall with `playwright install chromium`
- **General Issues**: Enable debug mode for detailed logs
- **Documentation**: Review `ai_vision_guide.md` for advanced features

---

**Ready to start?** Run `python run_smart.py` and experience AI-powered automation! 🚀