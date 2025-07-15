"""
AI Vision Agent for intelligent web element detection using Groq LLM.
Analyzes page content to find login buttons, forms, and clickable elements.
"""

import os
import json
import base64
import asyncio
from typing import Dict, List, Optional, Tuple
from groq import Groq
import typer

class AIVisionAgent:
    def __init__(self):
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama3-70b-8192"  # Fast and capable model
    
    async def analyze_page_for_login(self, page, screenshot_path: Optional[str] = None) -> Dict:
        """
        Analyze page content using AI to find login elements intelligently
        """
        try:
            # Get page content and structure
            page_data = await self._extract_page_data(page)
            
            # Take screenshot for visual context
            if screenshot_path:
                await page.screenshot(path=screenshot_path, full_page=True)
            
            # Analyze with Groq LLM
            analysis = await self._analyze_with_groq(page_data)
            
            return analysis
            
        except Exception as e:
            typer.echo(f"❌ AI analysis failed: {str(e)}")
            return {"error": str(e)}
    
    async def _extract_page_data(self, page) -> Dict:
        """Extract comprehensive page data for AI analysis"""
        
        # Get basic page info
        title = await page.title()
        url = page.url
        
        # Get all text content
        body_text = await page.text_content('body')
        
        # Get HTML structure of interactive elements
        interactive_elements = await page.evaluate("""
            () => {
                const elements = [];
                const selectors = ['button', 'a', '[onclick]', '[role="button"]', 'input[type="submit"]'];
                
                selectors.forEach(selector => {
                    document.querySelectorAll(selector).forEach((el, index) => {
                        const rect = el.getBoundingClientRect();
                        const styles = window.getComputedStyle(el);
                        
                        if (rect.width > 0 && rect.height > 0 && styles.visibility !== 'hidden') {
                            elements.push({
                                tag: el.tagName.toLowerCase(),
                                text: el.textContent.trim(),
                                id: el.id || '',
                                className: el.className || '',
                                href: el.href || '',
                                type: el.type || '',
                                x: Math.round(rect.x),
                                y: Math.round(rect.y),
                                width: Math.round(rect.width),
                                height: Math.round(rect.height),
                                selector: selector,
                                index: index
                            });
                        }
                    });
                });
                
                return elements;
            }
        """)
        
        # Get form elements
        form_elements = await page.evaluate("""
            () => {
                const forms = [];
                document.querySelectorAll('form').forEach((form, index) => {
                    const inputs = [];
                    form.querySelectorAll('input, select, textarea').forEach(input => {
                        inputs.push({
                            tag: input.tagName.toLowerCase(),
                            type: input.type || '',
                            name: input.name || '',
                            placeholder: input.placeholder || '',
                            id: input.id || ''
                        });
                    });
                    
                    forms.push({
                        index: index,
                        action: form.action || '',
                        method: form.method || '',
                        inputs: inputs
                    });
                });
                
                return forms;
            }
        """)
        
        # Get header/navigation area specifically
        header_content = await page.evaluate("""
            () => {
                const headerSelectors = ['header', '.header', 'nav', '.nav', '.navigation', '.top-bar'];
                let headerText = '';
                
                for (const selector of headerSelectors) {
                    const element = document.querySelector(selector);
                    if (element) {
                        headerText += element.textContent + ' ';
                    }
                }
                
                return headerText.trim();
            }
        """)
        
        return {
            'title': title,
            'url': url,
            'body_text': body_text[:3000],  # Limit text length
            'interactive_elements': interactive_elements,
            'form_elements': form_elements,
            'header_content': header_content
        }
    
    async def _analyze_with_groq(self, page_data: Dict) -> Dict:
        """Use Groq LLM to analyze page data and find login elements"""
        
        prompt = f"""
Analyze this web page data to find login-related elements. The page is from an e-commerce website (Ajio.com).

PAGE INFORMATION:
Title: {page_data['title']}
URL: {page_data['url']}

HEADER/NAVIGATION CONTENT:
{page_data['header_content']}

INTERACTIVE ELEMENTS:
{json.dumps(page_data['interactive_elements'], indent=2)}

FORMS:
{json.dumps(page_data['form_elements'], indent=2)}

TASK: Find the most likely login button or link on this page.

Look for elements that:
1. Have text like "Sign In", "Login", "Log In", "Account", "My Account"
2. Are buttons or links in the header/navigation area
3. Point to login-related URLs
4. Are associated with login forms

Respond with JSON in this exact format:
{{
    "login_found": true/false,
    "login_element": {{
        "text": "exact text of login element",
        "tag": "button/a/etc",
        "selector_strategy": "text/class/id/position",
        "recommended_selector": "CSS selector to use",
        "coordinates": {{"x": number, "y": number}},
        "confidence": "high/medium/low"
    }},
    "reasoning": "explain why this element was chosen",
    "alternatives": [
        {{
            "text": "alternative element text",
            "selector": "alternative selector",
            "confidence": "medium/low"
        }}
    ]
}}

If no login element is found, set login_found to false and explain why.
"""

        try:
            response = self.groq_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert web scraping assistant that analyzes web pages to find login elements. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Try to extract JSON from response
            try:
                # Remove any markdown formatting
                if '```json' in response_text:
                    response_text = response_text.split('```json')[1].split('```')[0]
                elif '```' in response_text:
                    response_text = response_text.split('```')[1]
                
                analysis = json.loads(response_text)
                return analysis
                
            except json.JSONDecodeError:
                typer.echo(f"⚠️ Failed to parse AI response as JSON: {response_text}")
                return {"error": "Invalid JSON response from AI", "raw_response": response_text}
                
        except Exception as e:
            typer.echo(f"❌ Groq API error: {str(e)}")
            return {"error": str(e)}
    
    async def find_and_click_login(self, page) -> bool:
        """
        Main method to find and click login element using AI analysis
        """
        typer.echo("🤖 Starting AI-powered login detection...")
        
        # Analyze page with AI
        analysis = await self.analyze_page_for_login(page)
        
        if "error" in analysis:
            typer.echo(f"❌ AI analysis failed: {analysis['error']}")
            return False
        
        if not analysis.get("login_found", False):
            typer.echo("❌ AI could not find login element")
            typer.echo(f"💡 Reasoning: {analysis.get('reasoning', 'No reasoning provided')}")
            return False
        
        login_element = analysis.get("login_element", {})
        typer.echo(f"🎯 AI found login element: '{login_element.get('text', 'N/A')}'")
        typer.echo(f"📍 Confidence: {login_element.get('confidence', 'unknown')}")
        typer.echo(f"💭 Reasoning: {analysis.get('reasoning', 'No reasoning provided')}")
        
        # Try to click the identified element
        success = await self._click_ai_identified_element(page, login_element)
        
        if not success and analysis.get("alternatives"):
            typer.echo("🔄 Primary element failed, trying alternatives...")
            for alt in analysis["alternatives"]:
                typer.echo(f"🔄 Trying alternative: '{alt.get('text', 'N/A')}'")
                alt_element = {
                    "recommended_selector": alt.get("selector", ""),
                    "text": alt.get("text", ""),
                    "confidence": alt.get("confidence", "low")
                }
                success = await self._click_ai_identified_element(page, alt_element)
                if success:
                    break
        
        return success
    
    async def _click_ai_identified_element(self, page, element_info: Dict) -> bool:
        """Click the element identified by AI"""
        
        selector = element_info.get("recommended_selector", "")
        text = element_info.get("text", "")
        coordinates = element_info.get("coordinates", {})
        
        if not selector and not coordinates:
            typer.echo("❌ No selector or coordinates provided by AI")
            return False
        
        try:
            # Strategy 1: Use AI-recommended selector
            if selector:
                typer.echo(f"🎯 Trying AI selector: {selector}")
                try:
                    element = await page.wait_for_selector(selector, timeout=5000)
                    if element:
                        is_visible = await element.is_visible()
                        is_enabled = await element.is_enabled()
                        
                        if is_visible and is_enabled:
                            await element.scroll_into_view_if_needed()
                            await asyncio.sleep(0.5)
                            await element.click()
                            typer.echo("✅ Successfully clicked AI-identified login element")
                            return True
                        else:
                            typer.echo(f"⚠️ Element not clickable (visible: {is_visible}, enabled: {is_enabled})")
                            
                except Exception as e:
                    typer.echo(f"❌ Selector failed: {str(e)}")
            
            # Strategy 2: Use coordinates if provided
            if coordinates and coordinates.get('x') and coordinates.get('y'):
                typer.echo(f"🎯 Trying coordinates: ({coordinates['x']}, {coordinates['y']})")
                try:
                    await page.mouse.click(coordinates['x'], coordinates['y'])
                    typer.echo("✅ Successfully clicked using AI-provided coordinates")
                    return True
                except Exception as e:
                    typer.echo(f"❌ Coordinate click failed: {str(e)}")
            
            # Strategy 3: Text-based fallback
            if text:
                text_selectors = [
                    f'text="{text}"',
                    f'button:has-text("{text}")',
                    f'a:has-text("{text}")',
                    f'[role="button"]:has-text("{text}")'
                ]
                
                for text_selector in text_selectors:
                    try:
                        typer.echo(f"🎯 Trying text selector: {text_selector}")
                        element = await page.wait_for_selector(text_selector, timeout=3000)
                        if element and await element.is_visible():
                            await element.click()
                            typer.echo("✅ Successfully clicked using text-based selector")
                            return True
                    except:
                        continue
            
            return False
            
        except Exception as e:
            typer.echo(f"❌ Failed to click AI-identified element: {str(e)}")
            return False
    
    async def analyze_login_form(self, page) -> Dict:
        """Analyze login form fields after login button is clicked"""
        
        typer.echo("🔍 Analyzing login form with AI...")
        
        # Wait for form to appear
        await asyncio.sleep(2)
        
        form_data = await page.evaluate("""
            () => {
                const forms = [];
                document.querySelectorAll('form').forEach(form => {
                    const inputs = [];
                    form.querySelectorAll('input').forEach(input => {
                        inputs.push({
                            type: input.type,
                            name: input.name,
                            placeholder: input.placeholder,
                            id: input.id,
                            className: input.className
                        });
                    });
                    
                    if (inputs.length > 0) {
                        forms.push({
                            inputs: inputs,
                            action: form.action
                        });
                    }
                });
                
                return forms;
            }
        """)
        
        if not form_data:
            return {"error": "No forms found"}
        
        # Use AI to identify phone/email and password fields
        prompt = f"""
Analyze these login form inputs to identify phone number, email, and password fields:

FORMS:
{json.dumps(form_data, indent=2)}

Return JSON with:
{{
    "phone_field": {{"selector": "CSS selector", "confidence": "high/medium/low"}},
    "email_field": {{"selector": "CSS selector", "confidence": "high/medium/low"}},
    "password_field": {{"selector": "CSS selector", "confidence": "high/medium/low"}},
    "submit_button": {{"selector": "CSS selector", "confidence": "high/medium/low"}}
}}
"""
        
        try:
            response = self.groq_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing web forms. Return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            return result
            
        except Exception as e:
            typer.echo(f"❌ Form analysis failed: {str(e)}")
            return {"error": str(e)}