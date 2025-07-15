#!/usr/bin/env python3
"""
Test script for AI Vision Agent to demonstrate intelligent login detection
"""

import asyncio
from agents.ai_vision_agent import AIVisionAgent
from playwright.async_api import async_playwright

async def test_ai_vision():
    """Test AI vision capabilities on a sample webpage"""
    print("🤖 Testing AI Vision Agent with Groq...")
    
    ai_vision = AIVisionAgent()
    
    # Start playwright for testing
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)
    page = await browser.new_page()
    
    try:
        # Test with a simple login page
        print("📄 Loading test page...")
        await page.goto("https://example.com", wait_until='domcontentloaded')
        
        # Test AI analysis
        print("🧠 Running AI analysis...")
        analysis = await ai_vision.analyze_page_for_login(page)
        
        print("\n📊 AI Analysis Results:")
        print("=" * 50)
        
        if "error" in analysis:
            print(f"❌ Error: {analysis['error']}")
        else:
            print(f"🎯 Login found: {analysis.get('login_found', False)}")
            
            if analysis.get('login_found'):
                login_element = analysis.get('login_element', {})
                print(f"📝 Element text: '{login_element.get('text', 'N/A')}'")
                print(f"🏷️ Element tag: {login_element.get('tag', 'N/A')}")
                print(f"🎯 Confidence: {login_element.get('confidence', 'N/A')}")
                print(f"📍 Selector: {login_element.get('recommended_selector', 'N/A')}")
                print(f"💭 Reasoning: {analysis.get('reasoning', 'N/A')}")
                
                alternatives = analysis.get('alternatives', [])
                if alternatives:
                    print(f"\n🔄 Found {len(alternatives)} alternatives:")
                    for i, alt in enumerate(alternatives, 1):
                        print(f"  {i}. '{alt.get('text', 'N/A')}' (confidence: {alt.get('confidence', 'N/A')})")
            else:
                print(f"💡 Reasoning: {analysis.get('reasoning', 'No reasoning provided')}")
        
        print("\n✅ AI Vision test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
    finally:
        await browser.close()
        await playwright.stop()

if __name__ == "__main__":
    asyncio.run(test_ai_vision())