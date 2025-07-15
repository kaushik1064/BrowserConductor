# Bypass Detection Guide for Ajio.com Automation

## Understanding the Access Denied Error

The "Access Denied" error with reference `#18.a5e23017.1752567707.2e8c21c1` indicates that Ajio.com's security system (likely CloudFlare or similar) has detected and blocked your automated access.

## Detection Methods Used by Ajio.com

1. **IP-based Detection**: Repeated requests from same IP
2. **Browser Fingerprinting**: Detecting headless browsers
3. **Behavioral Analysis**: Non-human interaction patterns
4. **Rate Limiting**: Too many requests too quickly
5. **Header Analysis**: Missing or suspicious HTTP headers

## Solutions Implemented

### 1. Enhanced Stealth Agent

I've created `StealthLoginAgent` with the following anti-detection measures:

#### Browser Stealth Features:
- **Random User Agents**: Rotates between real browser user agents
- **Webdriver Property Removal**: Removes `navigator.webdriver` property
- **Canvas Fingerprinting**: Randomizes canvas fingerprints
- **Plugin Mocking**: Simulates real browser plugins
- **Chrome Object Mocking**: Adds fake chrome runtime object

#### Human-like Behavior:
- **Random Delays**: Adds realistic pauses between actions
- **Mouse Movements**: Simulates random mouse movements
- **Scrolling**: Natural scrolling behavior
- **Typing Delays**: Human-like typing with random delays

#### Network Stealth:
- **Realistic Headers**: Proper HTTP headers like real browsers
- **Referrer Spoofing**: Uses Google as referrer
- **Cookie Management**: Proper cookie handling
- **DNS Over HTTPS**: Uses secure DNS resolution

### 2. Rotation and Retry Logic

```python
# Try multiple approaches if blocked
alternative_urls = [
    'https://www.ajio.com/',
    'https://ajio.com/',
    'https://m.ajio.com/',
]

# Different user agents for each session
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36...',
    # More realistic UAs
]
```

## Usage Instructions

### 1. Use the Stealth Agent

Replace the regular `LoginAgent` with `StealthLoginAgent`:

```python
from agents.stealth_login_agent import StealthLoginAgent

# In your automation script
login_agent = StealthLoginAgent(headless=True)  # or False for visible browser
```

### 2. Enhanced Local Setup

```bash
# Install additional dependencies for stealth mode
pip install fake-useragent
pip install undetected-chromedriver

# Use residential proxy (recommended)
# Set these environment variables:
export PROXY_HOST="your-proxy-host.com"
export PROXY_PORT="8080"
export PROXY_USER="username"
export PROXY_PASS="password"
```

### 3. Advanced Bypass Techniques

#### Option A: VPN/Proxy Rotation
```bash
# Use different IP addresses
# Install a VPN client or proxy service
# Rotate IP every few sessions
```

#### Option B: Browser Profile Persistence
```python
# Save browser profile between sessions
browser_context = await browser.new_context(
    user_data_dir="./browser_profile",
    viewport={'width': 1920, 'height': 1080}
)
```

#### Option C: Timing-based Approach
```python
# Spread automation across different times
import random
import time

# Wait between sessions
session_delay = random.randint(3600, 7200)  # 1-2 hours
time.sleep(session_delay)
```

## Updated Run Script

Create `run_stealth.py`:

```python
#!/usr/bin/env python3
"""
Stealth automation runner for Ajio.com
"""

import asyncio
import typer
from agents.stealth_login_agent import StealthLoginAgent
from agents.order_agent import OrderAgent
from agents.return_agent import ReturnAgent
from agents.reminder_agent import ReminderAgent

async def stealth_automation(phone_number: str, headless: bool = False):
    """Run automation with stealth measures"""
    
    # Use non-headless mode for better success rate
    login_agent = StealthLoginAgent(headless=headless)
    order_agent = OrderAgent()
    
    try:
        await login_agent.start_browser()
        
        # Login with stealth measures
        success = await login_agent.login(phone_number)
        if success:
            # Continue with order scraping
            orders = await order_agent.scrape_orders(login_agent.page)
            print(f"Found {len(orders)} orders")
            
        return success
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        await login_agent.close_browser()

if __name__ == "__main__":
    phone = input("Enter phone number: ")
    asyncio.run(stealth_automation(phone, headless=False))
```

## Additional Recommendations

### 1. Time-based Strategy
- Run automation during off-peak hours (late night/early morning)
- Space out sessions by several hours
- Don't run multiple sessions simultaneously

### 2. Network-based Strategy
- Use residential proxies (not datacenter proxies)
- Rotate IP addresses between sessions
- Use VPN services with Indian IP addresses

### 3. Browser-based Strategy
- Use headed mode (visible browser) for better success
- Keep browser profile persistent between sessions
- Use real Chrome browser instead of Chromium

### 4. Behavioral Strategy
- Add longer delays between actions
- Simulate browsing other pages first
- Use random mouse movements and scrolling

## Testing the Bypass

1. **Test with Headed Browser First**:
   ```bash
   python run_stealth.py --no-headless
   ```

2. **Monitor Success Rate**:
   - Try at different times of day
   - Note which user agents work best
   - Track IP blocking patterns

3. **Gradual Approach**:
   - Start with manual browsing to establish session
   - Then switch to automation
   - Use session persistence

## Emergency Fallback

If all automated methods fail:

1. **Manual Hybrid Approach**:
   - Manually navigate to Ajio.com
   - Complete login manually
   - Then use automation for order scraping

2. **API Alternative**:
   - Look for unofficial Ajio API endpoints
   - Use mobile app API if available
   - Reverse engineer network calls

3. **Scheduled Automation**:
   - Run automation less frequently
   - Use different devices/networks
   - Implement circuit breaker pattern

The stealth agent should significantly improve your success rate in bypassing Ajio's detection systems!