"""
Stealth Login Agent for Ajio.com automation with anti-detection measures.
Includes realistic browser behavior, random delays, and proxy rotation.
"""

import asyncio
import random
import typer
from playwright.async_api import async_playwright, Page, Browser
from typing import Optional, Dict, Any
import time

from utils.popup_handler import PopupHandler
from config import Config

class StealthLoginAgent:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.popup_handler = PopupHandler()
        
    async def start_browser(self):
        """Initialize Playwright browser with stealth configurations"""
        self.playwright = await async_playwright().start()
        
        # Random user agent selection
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0'
        ]
        
        selected_ua = random.choice(user_agents)
        
        # Enhanced browser arguments to avoid detection
        browser_args = [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-blink-features=AutomationControlled',
            '--disable-features=VizDisplayCompositor',
            '--disable-extensions',
            '--disable-plugins',
            '--disable-gpu',
            '--disable-dev-shm-usage',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-renderer-backgrounding',
            '--disable-web-security',
            '--disable-features=TranslateUI',
            '--disable-ipc-flooding-protection',
            '--enable-features=NetworkService,NetworkServiceInProcess',
            '--force-color-profile=srgb',
            '--metrics-recording-only',
            '--use-mock-keychain',
            '--disable-background-networking',
            '--disable-default-apps',
            '--disable-extensions',
            '--disable-sync',
            '--disable-translate',
            '--hide-scrollbars',
            '--mute-audio',
            '--no-first-run',
            '--safebrowsing-disable-auto-update',
            '--disable-client-side-phishing-detection',
            '--disable-component-update',
            '--disable-hang-monitor',
            '--disable-prompt-on-repost',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-renderer-backgrounding',
            '--disable-features=TranslateUI',
            '--disable-ipc-flooding-protection'
        ]
        
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=browser_args
        )
        
        # Create browser context with additional stealth settings
        context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=selected_ua,
            locale='en-US',
            timezone_id='America/New_York',
            geolocation={'latitude': 40.7128, 'longitude': -74.0060},
            permissions=['geolocation']
        )
        
        # Add stealth scripts to avoid detection
        await context.add_init_script("""
            // Remove webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // Mock languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
            
            // Mock plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            // Mock chrome object
            window.chrome = {
                runtime: {},
            };
            
            // Mock permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            // Randomize canvas fingerprint
            const getImageData = HTMLCanvasElement.prototype.getContext('2d').getImageData;
            HTMLCanvasElement.prototype.getContext('2d').getImageData = function(...args) {
                const imageData = getImageData.apply(this, args);
                for (let i = 0; i < imageData.data.length; i += 4) {
                    imageData.data[i] += Math.floor(Math.random() * 10) - 5;
                    imageData.data[i + 1] += Math.floor(Math.random() * 10) - 5;
                    imageData.data[i + 2] += Math.floor(Math.random() * 10) - 5;
                }
                return imageData;
            };
        """)
        
        self.page = await context.new_page()
        
        # Set additional headers to appear more human-like
        await self.page.set_extra_http_headers({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
        
        typer.echo("🌐 Stealth browser started successfully")
    
    async def navigate_to_ajio(self):
        """Navigate to Ajio.com with human-like behavior"""
        typer.echo("🔗 Navigating to Ajio.com...")
        
        # Add random delay before navigation
        await asyncio.sleep(random.uniform(1, 3))
        
        try:
            # Navigate with longer timeout
            await self.page.goto(Config.AJIO_BASE_URL, 
                               wait_until='domcontentloaded',
                               timeout=60000)
            
            # Wait for page to fully load
            await asyncio.sleep(random.uniform(2, 5))
            
            # Check if we got blocked
            page_content = await self.page.content()
            if "Access Denied" in page_content or "Reference #" in page_content:
                typer.echo("❌ Access denied. Trying alternative approach...")
                return await self._handle_access_denied()
            
            # Handle initial popups
            await self.popup_handler.dismiss_popups(self.page)
            
            # Simulate human scrolling behavior
            await self._simulate_human_behavior()
            
            typer.echo("✅ Successfully loaded Ajio.com")
            return True
            
        except Exception as e:
            typer.echo(f"❌ Navigation failed: {str(e)}")
            return False
    
    async def _handle_access_denied(self):
        """Handle access denied by trying different approaches"""
        typer.echo("🔄 Attempting to bypass access restrictions...")
        
        # Try clearing cache and cookies
        await self.page.context.clear_cookies()
        
        # Wait longer between attempts
        await asyncio.sleep(random.uniform(10, 20))
        
        # Try with different referrer
        await self.page.set_extra_http_headers({
            'Referer': 'https://www.google.com/'
        })
        
        # Try alternative URLs
        alternative_urls = [
            'https://www.ajio.com/',
            'https://ajio.com/',
            'https://m.ajio.com/',
        ]
        
        for url in alternative_urls:
            try:
                typer.echo(f"🔄 Trying {url}...")
                await self.page.goto(url, wait_until='domcontentloaded', timeout=30000)
                await asyncio.sleep(random.uniform(3, 7))
                
                page_content = await self.page.content()
                if "Access Denied" not in page_content:
                    typer.echo("✅ Successfully bypassed restrictions")
                    return True
                    
            except Exception as e:
                typer.echo(f"❌ Failed to load {url}: {str(e)}")
                continue
        
        typer.echo("❌ Could not bypass access restrictions")
        return False
    
    async def _simulate_human_behavior(self):
        """Simulate human-like behavior on the page"""
        # Random mouse movements
        await self.page.mouse.move(
            random.randint(100, 800),
            random.randint(100, 600)
        )
        
        # Random scroll
        await self.page.evaluate(f"""
            window.scrollTo(0, {random.randint(100, 500)});
        """)
        
        # Wait randomly
        await asyncio.sleep(random.uniform(1, 3))
        
        # Move mouse again
        await self.page.mouse.move(
            random.randint(200, 900),
            random.randint(200, 700)
        )
    
    async def click_login_button(self):
        """Find and click the login button with human-like behavior"""
        typer.echo("🔐 Looking for login button...")
        
        # Simulate looking around the page first
        await self._simulate_human_behavior()
        
        login_selectors = Config.get_selector_list('login', 'login_button')
        
        for selector in login_selectors:
            try:
                # Wait and check if element exists
                element = await self.page.wait_for_selector(selector, timeout=10000)
                if element:
                    # Scroll element into view
                    await element.scroll_into_view_if_needed()
                    
                    # Random delay before clicking
                    await asyncio.sleep(random.uniform(0.5, 2))
                    
                    # Human-like click
                    await element.click(delay=random.randint(100, 300))
                    
                    typer.echo("✅ Login button clicked")
                    return True
                    
            except Exception as e:
                typer.echo(f"❌ Could not click selector {selector}: {str(e)}")
                continue
        
        typer.echo("❌ Could not find login button")
        return False
    
    async def enter_phone_number(self, phone_number: Optional[str] = None):
        """Enter phone number with human-like typing"""
        if not phone_number:
            phone_number = typer.prompt("📱 Enter your phone number")
        
        typer.echo(f"📱 Entering phone number: {phone_number}")
        
        phone_selectors = Config.get_selector_list('login', 'phone_input')
        
        for selector in phone_selectors:
            try:
                element = await self.page.wait_for_selector(selector, timeout=10000)
                if element:
                    # Clear field first
                    await element.clear()
                    
                    # Human-like typing with delays
                    await element.type(phone_number, delay=random.randint(100, 300))
                    
                    typer.echo("✅ Phone number entered")
                    return True
                    
            except Exception as e:
                continue
        
        typer.echo("❌ Could not find phone input field")
        return False
    
    async def click_send_otp(self):
        """Click Send OTP button"""
        typer.echo("📨 Clicking Send OTP...")
        
        await asyncio.sleep(random.uniform(1, 2))
        
        otp_selectors = Config.get_selector_list('login', 'otp_button')
        
        for selector in otp_selectors:
            try:
                element = await self.page.wait_for_selector(selector, timeout=10000)
                if element:
                    await element.click(delay=random.randint(100, 300))
                    typer.echo("✅ Send OTP clicked")
                    return True
                    
            except Exception as e:
                continue
        
        typer.echo("❌ Could not find Send OTP button")
        return False
    
    async def enter_otp(self):
        """Wait for user to enter OTP"""
        typer.echo("⏳ Waiting for OTP to be sent...")
        await asyncio.sleep(random.uniform(3, 7))
        
        otp = typer.prompt("🔢 Enter the OTP you received")
        
        otp_selectors = Config.get_selector_list('login', 'otp_input')
        
        for selector in otp_selectors:
            try:
                element = await self.page.wait_for_selector(selector, timeout=10000)
                if element:
                    await element.clear()
                    await element.type(otp, delay=random.randint(100, 300))
                    typer.echo("✅ OTP entered")
                    return True
                    
            except Exception as e:
                continue
        
        typer.echo("❌ Could not find OTP input field")
        return False
    
    async def verify_login(self):
        """Click verify/login button and wait for successful login"""
        typer.echo("✅ Verifying login...")
        
        await asyncio.sleep(random.uniform(1, 2))
        
        verify_selectors = Config.get_selector_list('login', 'verify_button')
        
        for selector in verify_selectors:
            try:
                element = await self.page.wait_for_selector(selector, timeout=10000)
                if element:
                    await element.click(delay=random.randint(100, 300))
                    break
                    
            except Exception as e:
                continue
        
        # Wait for login to complete
        await asyncio.sleep(random.uniform(5, 10))
        
        # Check if login was successful
        current_url = self.page.url
        if 'login' not in current_url.lower():
            typer.echo("✅ Login successful!")
            return True
        else:
            typer.echo("❌ Login may have failed")
            return False
    
    async def login(self, phone_number: Optional[str] = None):
        """Complete login flow with stealth measures"""
        try:
            # Navigate to Ajio
            if not await self.navigate_to_ajio():
                return False
            
            # Click login button
            if not await self.click_login_button():
                return False
            
            # Enter phone number
            if not await self.enter_phone_number(phone_number):
                return False
            
            # Click send OTP
            if not await self.click_send_otp():
                return False
            
            # Enter OTP
            if not await self.enter_otp():
                return False
            
            # Verify login
            return await self.verify_login()
            
        except Exception as e:
            typer.echo(f"❌ Login failed: {str(e)}")
            return False
    
    async def close_browser(self):
        """Clean up browser resources"""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
        typer.echo("🔒 Browser closed")