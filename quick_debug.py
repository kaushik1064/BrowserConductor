#!/usr/bin/env python3
"""
Quick debug script to identify current Ajio.com login elements
"""

import asyncio
from playwright.async_api import async_playwright

async def quick_ajio_check():
    playwright = await async_playwright().start()
    
    browser = await playwright.chromium.launch(headless=False)
    page = await browser.new_page()
    
    try:
        print("📍 Navigating to Ajio.com...")
        await page.goto('https://www.ajio.com', timeout=30000)
        await asyncio.sleep(3)
        
        # Check page title and URL
        title = await page.title()
        url = page.url
        print(f"📄 Page: {title}")
        print(f"🔗 URL: {url}")
        
        # Quick check for access denied
        content = await page.content()
        if "Access Denied" in content or "Reference #" in content:
            print("🚫 ACCESS DENIED - Page is blocked")
            print("💡 Try using a VPN or different network")
            return False
        
        # Look for any text containing "sign" or "login"
        print("\n🔍 Looking for login-related text on page...")
        
        # Check all text on page
        all_text = await page.text_content('body')
        login_keywords = ['sign in', 'login', 'log in', 'account', 'sign up']
        
        found_keywords = []
        for keyword in login_keywords:
            if keyword.lower() in all_text.lower():
                found_keywords.append(keyword)
        
        if found_keywords:
            print(f"✅ Found login keywords: {', '.join(found_keywords)}")
        else:
            print("❌ No login keywords found on page")
        
        # Try to find specific elements
        print("\n🎯 Checking specific elements...")
        
        # Check for header/navigation
        header_exists = await page.query_selector('header') is not None
        nav_exists = await page.query_selector('nav') is not None
        print(f"📱 Header element: {'✅' if header_exists else '❌'}")
        print(f"📱 Nav element: {'✅' if nav_exists else '❌'}")
        
        # Try to find login button with simple text search
        simple_selectors = [
            'text="Sign In"',
            'text="Login"',
            'text="LOG IN"',
            'text="SIGN IN"',
        ]
        
        for selector in simple_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    is_visible = await element.is_visible()
                    print(f"🎯 Found '{selector}': visible={is_visible}")
                    if is_visible:
                        print("✅ This looks promising!")
                        return True
            except:
                pass
        
        print("\n💡 Manual inspection needed:")
        print("1. Look at the browser window that opened")
        print("2. Find the login/sign in button manually")  
        print("3. Right-click and 'Inspect Element'")
        print("4. Note the exact text and HTML structure")
        
        print("\n⏸️ Press Enter to close browser...")
        input()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        await browser.close()
        await playwright.stop()

if __name__ == "__main__":
    success = asyncio.run(quick_ajio_check())
    if success:
        print("\n✅ Page loaded successfully")
        print("💡 Try running the stealth automation again with the updated selectors")
    else:
        print("\n❌ Page access failed")
        print("💡 Consider using VPN or different network")