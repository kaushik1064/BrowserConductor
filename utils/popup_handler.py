"""
Popup Handler for dismissing various types of popups and modals on Ajio.com.
Uses intelligent detection and dismissal strategies.
"""

import asyncio
from typing import List, Dict
from playwright.async_api import Page
import typer

class PopupHandler:
    def __init__(self):
        # Common popup selectors and their dismissal strategies
        self.popup_strategies = [
            {
                'name': 'Cookie Consent',
                'selectors': [
                    'button:has-text("Accept")',
                    'button:has-text("Accept All")',
                    'button:has-text("I Accept")',
                    '[data-testid="cookie-accept"]',
                    '.cookie-accept',
                    '#cookie-accept'
                ]
            },
            {
                'name': 'Newsletter Popup',
                'selectors': [
                    'button:has-text("No Thanks")',
                    'button:has-text("Later")',
                    'button:has-text("Skip")',
                    'button:has-text("Close")',
                    '[aria-label="Close"]',
                    '.close-btn',
                    '.popup-close'
                ]
            },
            {
                'name': 'App Download Popup',
                'selectors': [
                    'button:has-text("Maybe Later")',
                    'button:has-text("Not Now")',
                    'button:has-text("Continue on Web")',
                    '.app-banner-close',
                    '[data-testid="app-banner-close"]'
                ]
            },
            {
                'name': 'Location Popup',
                'selectors': [
                    'button:has-text("Skip")',
                    'button:has-text("Not Now")',
                    'button:has-text("Continue Without Location")',
                    '.location-skip',
                    '[data-testid="location-skip"]'
                ]
            },
            {
                'name': 'Generic Close Button',
                'selectors': [
                    'button[aria-label="Close"]',
                    'button[title="Close"]',
                    '.close',
                    '.close-button',
                    '.modal-close',
                    'svg[class*="close"]',
                    '[role="button"]:has-text("×")',
                    '[role="button"]:has-text("✕")'
                ]
            }
        ]
    
    async def dismiss_popups(self, page: Page, max_attempts: int = 3) -> List[str]:
        """Main method to dismiss all detected popups"""
        dismissed_popups = []
        
        for attempt in range(max_attempts):
            typer.echo(f"🔍 Checking for popups (attempt {attempt + 1}/{max_attempts})...")
            
            # Wait a moment for popups to appear
            await asyncio.sleep(2)
            
            popups_found = False
            
            # Try each popup strategy
            for strategy in self.popup_strategies:
                if await self.try_dismiss_popup(page, strategy):
                    dismissed_popups.append(strategy['name'])
                    popups_found = True
                    typer.echo(f"✅ Dismissed: {strategy['name']}")
                    await asyncio.sleep(1)  # Wait between dismissals
            
            # If no popups found in this attempt, we're likely done
            if not popups_found:
                break
        
        if dismissed_popups:
            typer.echo(f"🎯 Total popups dismissed: {len(dismissed_popups)}")
        else:
            typer.echo("👌 No popups detected")
        
        return dismissed_popups
    
    async def try_dismiss_popup(self, page: Page, strategy: Dict) -> bool:
        """Try to dismiss a popup using the given strategy"""
        for selector in strategy['selectors']:
            try:
                # Check if element exists and is visible
                element = await page.query_selector(selector)
                if element:
                    # Check if element is visible
                    is_visible = await element.is_visible()
                    if is_visible:
                        # Try to click the element
                        await element.click()
                        await asyncio.sleep(0.5)  # Wait for animation
                        return True
                        
            except Exception as e:
                # Continue trying other selectors
                continue
        
        return False
    
    async def handle_overlay_popups(self, page: Page) -> bool:
        """Handle overlay popups that might block interactions"""
        try:
            # Look for modal overlays
            overlay_selectors = [
                '.modal-overlay',
                '.popup-overlay',
                '.overlay',
                '[role="dialog"]',
                '.modal',
                '.popup'
            ]
            
            for selector in overlay_selectors:
                overlays = await page.query_selector_all(selector)
                
                for overlay in overlays:
                    is_visible = await overlay.is_visible()
                    if is_visible:
                        # Try to find close button within overlay
                        close_button = await overlay.query_selector('button[aria-label="Close"], .close, .close-btn')
                        if close_button:
                            await close_button.click()
                            await asyncio.sleep(0.5)
                            typer.echo("✅ Dismissed overlay popup")
                            return True
                        
                        # Try pressing Escape key
                        await page.keyboard.press('Escape')
                        await asyncio.sleep(0.5)
                        
                        # Check if overlay is still visible
                        still_visible = await overlay.is_visible()
                        if not still_visible:
                            typer.echo("✅ Dismissed overlay with Escape key")
                            return True
            
            return False
            
        except Exception as e:
            typer.echo(f"⚠️ Error handling overlay popups: {str(e)}")
            return False
    
    async def handle_notification_popups(self, page: Page) -> bool:
        """Handle browser notification permission popups"""
        try:
            # Set notification permission to denied to prevent popups
            context = page.context
            await context.grant_permissions([], origin=page.url)
            
            # Also try to dismiss any existing notification popups
            notification_selectors = [
                'button:has-text("Block")',
                'button:has-text("Don\'t Allow")',
                'button:has-text("Not Now")',
                '[data-testid="notification-deny"]'
            ]
            
            for selector in notification_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element and await element.is_visible():
                        await element.click()
                        typer.echo("✅ Blocked notification popup")
                        return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            typer.echo(f"⚠️ Error handling notification popups: {str(e)}")
            return False
    
    async def wait_for_page_stability(self, page: Page, timeout: int = 10000):
        """Wait for page to stabilize (no more popups appearing)"""
        try:
            # Wait for network to be idle
            await page.wait_for_load_state('networkidle', timeout=timeout)
            
            # Additional wait for any delayed popups
            await asyncio.sleep(2)
            
            typer.echo("✅ Page stabilized")
            
        except Exception as e:
            typer.echo(f"⚠️ Page stability timeout: {str(e)}")
    
    async def dismiss_all_popups_continuously(self, page: Page, duration: int = 30):
        """Continuously dismiss popups for a specified duration"""
        typer.echo(f"🔄 Monitoring for popups for {duration} seconds...")
        
        start_time = asyncio.get_event_loop().time()
        dismissed_count = 0
        
        while (asyncio.get_event_loop().time() - start_time) < duration:
            try:
                # Quick popup check
                for strategy in self.popup_strategies[:3]:  # Check most common popups
                    if await self.try_dismiss_popup(page, strategy):
                        dismissed_count += 1
                        typer.echo(f"✅ Auto-dismissed: {strategy['name']}")
                
                await asyncio.sleep(3)  # Check every 3 seconds
                
            except Exception as e:
                typer.echo(f"⚠️ Error in continuous monitoring: {str(e)}")
                await asyncio.sleep(5)
        
        typer.echo(f"🏁 Popup monitoring completed. Dismissed {dismissed_count} popups.")
        return dismissed_count
    
    async def smart_popup_detection(self, page: Page) -> List[Dict]:
        """Intelligently detect popups based on DOM characteristics"""
        detected_popups = []
        
        try:
            # Look for elements with popup-like characteristics
            popup_indicators = [
                # High z-index elements
                '*[style*="z-index: 999"]',
                '*[style*="z-index: 9999"]',
                # Fixed positioned elements
                '*[style*="position: fixed"]',
                # Elements with modal-related classes
                '[class*="modal"]',
                '[class*="popup"]',
                '[class*="overlay"]',
                '[class*="dialog"]',
                # ARIA roles
                '[role="dialog"]',
                '[role="alertdialog"]'
            ]
            
            for selector in popup_indicators:
                elements = await page.query_selector_all(selector)
                
                for element in elements:
                    is_visible = await element.is_visible()
                    if is_visible:
                        # Get element info
                        tag_name = await element.evaluate('el => el.tagName')
                        class_name = await element.get_attribute('class') or ''
                        
                        popup_info = {
                            'selector': selector,
                            'tag_name': tag_name,
                            'class_name': class_name,
                            'element': element
                        }
                        
                        detected_popups.append(popup_info)
            
            if detected_popups:
                typer.echo(f"🔍 Detected {len(detected_popups)} potential popups")
            
            return detected_popups
            
        except Exception as e:
            typer.echo(f"❌ Error in smart popup detection: {str(e)}")
            return []
