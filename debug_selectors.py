#!/usr/bin/env python3
"""
Debug script to find the correct selectors for Ajio.com
"""

import asyncio
from playwright.async_api import async_playwright

async def debug_ajio_selectors():
    """Debug script to find current Ajio.com selectors"""
    
    playwright = await async_playwright().start()
    
    # Launch browser in headed mode for debugging
    browser = await playwright.chromium.launch(
        headless=False,
        args=['--no-sandbox', '--disable-setuid-sandbox']
    )
    
    context = await browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    
    page = await context.new_page()
    
    try:
        print("🔗 Navigating to Ajio.com...")
        await page.goto('https://www.ajio.com', wait_until='domcontentloaded', timeout=30000)
        
        print("⏳ Waiting for page to load...")
        await asyncio.sleep(5)
        
        # Check if we can access the page
        title = await page.title()
        print(f"📄 Page title: {title}")
        
        # Look for login-related elements
        print("\n🔍 Searching for login elements...")
        
        # Common login button patterns
        login_patterns = [
            'button:has-text("Sign In")',
            'button:has-text("Login")',
            'a:has-text("Sign In")',
            'a:has-text("Login")',
            '[data-testid*="login"]',
            '[data-testid*="signin"]',
            '.header-login',
            '.login-button',
            '.signin-button',
            '[class*="login"]',
            '[class*="signin"]',
            'button[title*="login" i]',
            'a[title*="login" i]',
            'span:has-text("Sign In")',
            'div:has-text("Sign In")',
        ]
        
        found_elements = []
        
        for pattern in login_patterns:
            try:
                elements = await page.query_selector_all(pattern)
                if elements:
                    for i, element in enumerate(elements):
                        text_content = await element.text_content()
                        is_visible = await element.is_visible()
                        tag_name = await element.evaluate('el => el.tagName')
                        class_name = await element.get_attribute('class') or ''
                        id_attr = await element.get_attribute('id') or ''
                        
                        if text_content and is_visible:
                            found_elements.append({
                                'pattern': pattern,
                                'text': text_content.strip(),
                                'tag': tag_name,
                                'class': class_name,
                                'id': id_attr,
                                'visible': is_visible
                            })
                            print(f"✅ Found: {pattern} -> '{text_content.strip()}' ({tag_name}) visible={is_visible}")
                        
            except Exception as e:
                continue
        
        if not found_elements:
            print("❌ No login elements found with common patterns")
            print("\n🔍 Let's check the page source for any login-related content...")
            
            # Get page content and search for login keywords
            content = await page.content()
            login_keywords = ['login', 'signin', 'sign in', 'account', 'user']
            
            for keyword in login_keywords:
                if keyword.lower() in content.lower():
                    print(f"📝 Found '{keyword}' in page content")
        
        # Check navigation/header area specifically
        print("\n🔍 Checking header/navigation area...")
        header_selectors = [
            'header',
            '.header',
            '.nav',
            '.navigation',
            '.top-bar',
            '.main-header',
            '[role="banner"]'
        ]
        
        for selector in header_selectors:
            try:
                header = await page.query_selector(selector)
                if header:
                    header_text = await header.text_content()
                    if header_text and any(word in header_text.lower() for word in ['login', 'sign', 'account']):
                        print(f"🎯 Header content with login: {selector}")
                        print(f"   Text: {header_text[:200]}...")
                        
                        # Find clickable elements in header
                        clickable = await header.query_selector_all('a, button, [onclick], [role="button"]')
                        for element in clickable:
                            text = await element.text_content()
                            if text and any(word in text.lower() for word in ['login', 'sign', 'account']):
                                tag = await element.evaluate('el => el.tagName')
                                class_attr = await element.get_attribute('class') or ''
                                print(f"   🎯 Clickable: {tag}.{class_attr} -> '{text.strip()}'")
                        
            except Exception as e:
                continue
        
        print(f"\n📊 Summary: Found {len(found_elements)} potential login elements")
        
        # Wait for user to manually inspect
        print("\n👀 Browser window is open. Please manually check the page and identify the login button.")
        print("🔍 Look for Sign In, Login, or Account buttons/links in the header")
        print("📝 Note down the exact selector or text content")
        print("\n⏸️ Press Enter when you're ready to close the browser...")
        input()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        
        # Check if it's an access denied error
        page_content = await page.content()
        if "Access Denied" in page_content:
            print("🚫 Access denied detected. The IP might be blocked.")
            print("💡 Try using a VPN or different network")
        
    finally:
        await browser.close()
        await playwright.stop()

if __name__ == "__main__":
    asyncio.run(debug_ajio_selectors())