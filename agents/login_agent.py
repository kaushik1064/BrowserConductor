"""
Login Agent for Ajio.com automation.
Handles browser initialization, popup dismissal, and authentication flow.
"""

import asyncio
import typer
from playwright.async_api import async_playwright, Page, Browser
from typing import Optional

from utils.popup_handler import PopupHandler
from config import Config

class LoginAgent:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.popup_handler = PopupHandler()
        
    async def start_browser(self):
        """Initialize Playwright browser and page"""
        self.playwright = await async_playwright().start()
        
        # Launch browser with appropriate options
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
        # Create new page with realistic viewport
        self.page = await self.browser.new_page(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        
        typer.echo("🌐 Browser started successfully")
    
    async def navigate_to_ajio(self):
        """Navigate to Ajio.com homepage"""
        typer.echo("🔗 Navigating to Ajio.com...")
        await self.page.goto(Config.AJIO_BASE_URL, wait_until='networkidle')
        
        # Handle initial popups
        await self.popup_handler.dismiss_popups(self.page)
        
        typer.echo("✅ Successfully loaded Ajio.com")
    
    async def click_login_button(self):
        """Find and click the login button"""
        typer.echo("🔐 Looking for login button...")
        
        # Multiple selectors for login button (Ajio might change these)
        login_selectors = [
            '[data-testid="login-button"]',
            'text="Sign In"',
            'text="Login"',
            '.login-btn',
            '[title="Login"]',
            'a[href*="login"]'
        ]
        
        for selector in login_selectors:
            try:
                await self.page.wait_for_selector(selector, timeout=5000)
                await self.page.click(selector)
                typer.echo("✅ Login button clicked")
                return True
            except:
                continue
        
        typer.echo("❌ Could not find login button")
        return False
    
    async def enter_phone_number(self, phone_number: Optional[str] = None):
        """Enter phone number in login form"""
        if not phone_number:
            phone_number = typer.prompt("📱 Enter your phone number")
        
        # Wait for phone input field
        phone_selectors = [
            'input[name="username"]',
            'input[placeholder*="phone"]',
            'input[placeholder*="mobile"]',
            'input[type="tel"]',
            '#username'
        ]
        
        for selector in phone_selectors:
            try:
                await self.page.wait_for_selector(selector, timeout=5000)
                await self.page.fill(selector, phone_number)
                typer.echo(f"✅ Phone number entered: {phone_number}")
                return True
            except:
                continue
        
        typer.echo("❌ Could not find phone number input field")
        return False
    
    async def click_send_otp(self):
        """Click Send OTP button"""
        otp_selectors = [
            'text="Send OTP"',
            'text="Get OTP"',
            'button[type="submit"]',
            '.otp-btn',
            '[data-testid="send-otp"]'
        ]
        
        for selector in otp_selectors:
            try:
                await self.page.wait_for_selector(selector, timeout=5000)
                await self.page.click(selector)
                typer.echo("✅ Send OTP button clicked")
                return True
            except:
                continue
        
        typer.echo("❌ Could not find Send OTP button")
        return False
    
    async def enter_otp(self):
        """Wait for user to enter OTP"""
        typer.echo("📲 OTP has been sent to your phone")
        otp = typer.prompt("🔢 Enter the OTP you received")
        
        # Find OTP input fields (might be multiple inputs or single input)
        otp_selectors = [
            'input[name="otp"]',
            'input[placeholder*="OTP"]',
            'input[placeholder*="code"]',
            '.otp-input',
            '[data-testid="otp-input"]'
        ]
        
        # Try single OTP input first
        for selector in otp_selectors:
            try:
                await self.page.wait_for_selector(selector, timeout=5000)
                await self.page.fill(selector, otp)
                typer.echo("✅ OTP entered")
                return True
            except:
                continue
        
        # Try multiple OTP inputs (digit by digit)
        try:
            otp_inputs = await self.page.query_selector_all('input[maxlength="1"]')
            if len(otp_inputs) == len(otp):
                for i, digit in enumerate(otp):
                    await otp_inputs[i].fill(digit)
                typer.echo("✅ OTP entered (digit by digit)")
                return True
        except:
            pass
        
        typer.echo("❌ Could not find OTP input field")
        return False
    
    async def verify_login(self):
        """Click verify/login button and wait for successful login"""
        verify_selectors = [
            'text="Verify"',
            'text="Login"',
            'text="Submit"',
            'button[type="submit"]',
            '.verify-btn',
            '[data-testid="verify-otp"]'
        ]
        
        for selector in verify_selectors:
            try:
                await self.page.wait_for_selector(selector, timeout=5000)
                await self.page.click(selector)
                break
            except:
                continue
        
        # Wait for login success indicators
        try:
            # Wait for either account menu or profile icon to appear
            await self.page.wait_for_selector('text="My Account"', timeout=15000)
            typer.echo("✅ Login successful!")
            return True
        except:
            try:
                # Alternative success indicator
                await self.page.wait_for_selector('.user-profile', timeout=5000)
                typer.echo("✅ Login successful!")
                return True
            except:
                typer.echo("❌ Login verification failed")
                return False
    
    async def login(self, phone_number: Optional[str] = None):
        """Complete login flow"""
        try:
            await self.navigate_to_ajio()
            
            if not await self.click_login_button():
                return False
            
            # Wait for login modal to appear
            await asyncio.sleep(2)
            
            if not await self.enter_phone_number(phone_number):
                return False
            
            if not await self.click_send_otp():
                return False
            
            if not await self.enter_otp():
                return False
            
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
