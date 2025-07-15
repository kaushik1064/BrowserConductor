"""
Smart Login Agent that combines stealth capabilities with AI vision.
Uses Groq LLM to intelligently identify login elements on any website.
"""

import asyncio
import random
import typer
from playwright.async_api import async_playwright, Page, Browser
from typing import Optional, Dict, Any
import time

from utils.popup_handler import PopupHandler
from config import Config
from agents.ai_vision_agent import AIVisionAgent

class SmartLoginAgent:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.popup_handler = PopupHandler()
        self.ai_vision = AIVisionAgent()
        
    async def start_browser(self):
        """Initialize Playwright browser with stealth configurations"""
        self.playwright = await async_playwright().start()
        
        # Random user agent selection
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebLib/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebLib/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebLib/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
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
        """)
        
        self.page = await context.new_page()
        
        # Set additional headers
        await self.page.set_extra_http_headers({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        typer.echo("🤖 Smart browser with AI vision started successfully")
    
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
    
    async def smart_login_detection(self):
        """Use AI to intelligently find and click login button"""
        typer.echo("🤖 Starting AI-powered login detection...")
        
        # Simulate looking around the page first
        await self._simulate_human_behavior()
        
        # Use AI vision to find login element
        success = await self.ai_vision.find_and_click_login(self.page)
        
        if success:
            typer.echo("✅ AI successfully found and clicked login button")
            return True
        else:
            typer.echo("❌ AI could not find login button")
            return False
    
    async def smart_form_filling(self, phone_number: Optional[str] = None):
        """Use AI to intelligently fill login form"""
        if not phone_number:
            phone_number = typer.prompt("📱 Enter your phone number")
        
        typer.echo("🤖 Using AI to analyze login form...")
        
        # Wait for form to load
        await asyncio.sleep(random.uniform(2, 4))
        
        # Analyze form with AI
        form_analysis = await self.ai_vision.analyze_login_form(self.page)
        
        if "error" in form_analysis:
            typer.echo(f"❌ Form analysis failed: {form_analysis['error']}")
            return await self._fallback_form_filling(phone_number)
        
        # Fill phone number field
        phone_field = form_analysis.get("phone_field", {})
        if phone_field.get("selector"):
            try:
                typer.echo(f"📱 AI found phone field: {phone_field['selector']}")
                element = await self.page.wait_for_selector(phone_field["selector"], timeout=10000)
                if element:
                    await element.clear()
                    await element.type(phone_number, delay=random.randint(100, 300))
                    typer.echo("✅ Phone number entered using AI detection")
                    
                    # Click send OTP button
                    submit_button = form_analysis.get("submit_button", {})
                    if submit_button.get("selector"):
                        await asyncio.sleep(random.uniform(1, 2))
                        submit_element = await self.page.wait_for_selector(submit_button["selector"], timeout=5000)
                        if submit_element:
                            await submit_element.click()
                            typer.echo("✅ Send OTP clicked using AI detection")
                            return True
                    
            except Exception as e:
                typer.echo(f"❌ AI form filling failed: {str(e)}")
                return await self._fallback_form_filling(phone_number)
        
        return await self._fallback_form_filling(phone_number)
    
    async def _fallback_form_filling(self, phone_number: str):
        """Fallback method for form filling"""
        typer.echo("🔄 Using fallback form filling method...")
        
        phone_selectors = [
            'input[name="username"]',
            'input[placeholder*="phone"]',
            'input[placeholder*="mobile"]',
            'input[type="tel"]',
            'input[name="phone"]',
            'input[name="mobile"]',
            '#username',
            '#phone',
            '#mobile'
        ]
        
        for selector in phone_selectors:
            try:
                element = await self.page.wait_for_selector(selector, timeout=5000)
                if element and await element.is_visible():
                    await element.clear()
                    await element.type(phone_number, delay=random.randint(100, 300))
                    typer.echo("✅ Phone number entered with fallback method")
                    
                    # Try to find and click OTP button
                    otp_selectors = [
                        'text="Send OTP"',
                        'text="Get OTP"',
                        'button[type="submit"]',
                        '.otp-btn',
                        'button:has-text("OTP")'
                    ]
                    
                    for otp_selector in otp_selectors:
                        try:
                            otp_element = await self.page.wait_for_selector(otp_selector, timeout=3000)
                            if otp_element and await otp_element.is_visible():
                                await asyncio.sleep(random.uniform(1, 2))
                                await otp_element.click()
                                typer.echo("✅ Send OTP clicked with fallback method")
                                return True
                        except:
                            continue
                    
                    return True
                    
            except:
                continue
        
        typer.echo("❌ Could not find phone input field")
        return False
    
    async def enter_otp(self):
        """Handle OTP entry"""
        typer.echo("⏳ Waiting for OTP to be sent...")
        await asyncio.sleep(random.uniform(3, 7))
        
        otp = typer.prompt("🔢 Enter the OTP you received")
        
        otp_selectors = [
            'input[name="otp"]',
            'input[placeholder*="OTP"]',
            'input[placeholder*="code"]',
            '.otp-input',
            '#otp'
        ]
        
        for selector in otp_selectors:
            try:
                element = await self.page.wait_for_selector(selector, timeout=10000)
                if element and await element.is_visible():
                    await element.clear()
                    await element.type(otp, delay=random.randint(100, 300))
                    typer.echo("✅ OTP entered")
                    
                    # Try to find verify button
                    verify_selectors = [
                        'text="Verify"',
                        'text="Login"',
                        'text="Submit"',
                        'button[type="submit"]',
                        '.verify-btn'
                    ]
                    
                    for verify_selector in verify_selectors:
                        try:
                            verify_element = await self.page.wait_for_selector(verify_selector, timeout=3000)
                            if verify_element and await verify_element.is_visible():
                                await asyncio.sleep(random.uniform(1, 2))
                                await verify_element.click()
                                typer.echo("✅ Verify button clicked")
                                return True
                        except:
                            continue
                    
                    return True
                    
            except:
                continue
        
        typer.echo("❌ Could not find OTP input field")
        return False
    
    async def verify_login(self):
        """Check if login was successful"""
        typer.echo("✅ Verifying login...")
        
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
        """Complete smart login flow with AI assistance"""
        try:
            # Navigate to Ajio
            if not await self.navigate_to_ajio():
                return False
            
            # Use AI to find and click login button
            if not await self.smart_login_detection():
                return False
            
            # Use AI to fill form
            if not await self.smart_form_filling(phone_number):
                return False
            
            # Handle OTP
            if not await self.enter_otp():
                return False
            
            # Verify login
            return await self.verify_login()
            
        except Exception as e:
            typer.echo(f"❌ Smart login failed: {str(e)}")
            return False
    
    async def close_browser(self):
        """Clean up browser resources"""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
        typer.echo("🔒 Browser closed")