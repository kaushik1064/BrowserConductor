# Local Setup for Browser Automation

Since Replit has limitations for browser automation (missing system dependencies), here's how to run this project locally with full Playwright browser automation:

## Prerequisites

1. **Python 3.7+** installed on your system
2. **Git** to clone the repository
3. **Chrome/Chromium browser** (Playwright will install if needed)

## Installation Steps

### 1. Clone or Download the Project
```bash
# If using git
git clone <your-repo-url>
cd ajio-automation

# Or download the files from Replit and extract them
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Install system dependencies (Linux only)
# Ubuntu/Debian:
sudo apt-get update
sudo apt-get install -y \
    libnss3 \
    libnspr4 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libgtk-3-0 \
    libxss1
```

### 4. Create requirements.txt (if needed)
```bash
# Create this file with the following content:
flask==3.0.0
flask-sqlalchemy==3.1.1
playwright==1.40.0
beautifulsoup4==4.12.2
typer==0.9.0
aiohttp==3.9.1
psycopg2-binary==2.9.9
pytest==7.4.3
pytest-asyncio==0.21.1
trafilatura==1.6.4
email-validator==2.1.0
gunicorn==21.2.0
```

### 5. Set Environment Variables (Optional)
```bash
# For PostgreSQL (if you want to use PostgreSQL instead of SQLite)
export DATABASE_URL="postgresql://user:password@localhost/ajio_db"

# For Groq API (natural language processing)
export GROQ_API_KEY="your_groq_api_key_here"

# Session secret for Flask
export SESSION_SECRET="your-secret-key-here"
```

## Running the Application

### Option 1: Web Interface (Recommended)
```bash
# Start the web application
python web_interface.py

# Open browser and go to: http://localhost:5000
```

### Option 2: Command Line Interface
```bash
# Login and scrape orders
python -m typer main.py run login-and-scrape --phone "+91XXXXXXXXXX"

# Login with headed browser (visible)
python -m typer main.py run login-and-scrape --phone "+91XXXXXXXXXX" --no-headless

# Check reminders
python -m typer main.py run check-reminders

# List saved orders
python -m typer main.py run list-orders

# Execute return/replace with natural language
python -m typer main.py run login-and-scrape --phone "+91XXXXXXXXXX" --command "return the blue shirt from last week"
```

## Usage Instructions

### 1. First Run
- When you first run the automation, it will create a SQLite database (`orders.db`) automatically
- The browser will open and navigate to Ajio.com
- You'll need to manually enter the OTP when prompted

### 2. Phone Number Format
- Use international format: `+91XXXXXXXXXX`
- Or you can enter it when prompted

### 3. Browser Modes
- **Headless mode**: Browser runs in background (default)
- **Headed mode**: Browser window is visible (use `--no-headless`)

### 4. Natural Language Commands
If you have set up the Groq API key, you can use natural language commands like:
- "return the red dress from order 123"
- "exchange the shoes for a larger size"
- "cancel the recent shirt order"

## Features Available Locally

✅ **Full Browser Automation**: Real Playwright browser automation
✅ **Popup Handling**: Automatic dismissal of cookie banners and modals
✅ **Order Scraping**: Extract complete order information
✅ **Return Management**: Automate return/replace requests
✅ **Deadline Tracking**: Monitor return deadlines
✅ **Natural Language Processing**: Process commands in plain English
✅ **Database Storage**: SQLite/PostgreSQL support
✅ **Web Dashboard**: Beautiful web interface
✅ **Headless/Headed Modes**: Choose visible or background operation

## Troubleshooting

### Browser Issues
```bash
# Reinstall Playwright browsers
playwright install --force chromium

# Check system dependencies
playwright install-deps
```

### Database Issues
```bash
# Reset database
rm orders.db
# The database will be recreated on next run
```

### Permission Issues (Linux/macOS)
```bash
# Make sure Python has execution permissions
chmod +x main.py
chmod +x web_interface.py
```

## Security Notes

- The application only stores order information locally
- No credentials are saved (you enter OTP manually each time)
- All browser automation mimics human behavior
- Rate limiting and delays are built-in to avoid detection

## Performance Tips

- Use headless mode for faster execution
- Close other browser instances to free up resources
- Run during off-peak hours for better performance
- Use SSD storage for faster database operations

This local setup gives you full browser automation capabilities that aren't available in the Replit environment!