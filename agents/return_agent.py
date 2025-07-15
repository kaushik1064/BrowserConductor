"""
Return Agent for handling return/replace actions on Ajio.com.
Processes natural language commands and executes browser automation.
"""

import asyncio
import re
from typing import Optional, Dict, Any
from playwright.async_api import Page
import typer
import os

class ReturnAgent:
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY", "")
    
    async def process_command(self, page: Page, command: str) -> bool:
        """Process natural language command and execute return/replace action"""
        typer.echo(f"🤖 Processing command: {command}")
        
        # Parse command to extract intent and product details
        intent = self.parse_command(command)
        
        if not intent:
            typer.echo("❌ Could not understand the command")
            return False
        
        typer.echo(f"📝 Parsed intent: {intent}")
        
        # Find matching order on the page
        order_element = await self.find_matching_order(page, intent)
        
        if not order_element:
            typer.echo("❌ Could not find matching order")
            return False
        
        # Execute the action
        if intent['action'] == 'return':
            return await self.execute_return(page, order_element)
        elif intent['action'] == 'replace':
            return await self.execute_replace(page, order_element)
        else:
            typer.echo("❌ Unknown action")
            return False
    
    def parse_command(self, command: str) -> Optional[Dict[str, Any]]:
        """Parse natural language command to extract intent"""
        command_lower = command.lower()
        
        # Simple rule-based parsing (can be enhanced with Groq API)
        intent = {}
        
        # Determine action
        if 'return' in command_lower:
            intent['action'] = 'return'
        elif 'replace' in command_lower or 'exchange' in command_lower:
            intent['action'] = 'replace'
        else:
            return None
        
        # Extract product keywords
        # Common patterns: "return my red shoes", "replace blue shirt", etc.
        color_pattern = r'\b(red|blue|green|yellow|black|white|brown|gray|grey|pink|orange|purple)\b'
        product_pattern = r'\b(shirt|pants|shoes|dress|jacket|top|bottom|jeans|tshirt|t-shirt|kurta|saree)\b'
        
        colors = re.findall(color_pattern, command_lower)
        products = re.findall(product_pattern, command_lower)
        
        intent['colors'] = colors
        intent['products'] = products
        intent['keywords'] = command_lower.split()
        
        return intent
    
    async def find_matching_order(self, page: Page, intent: Dict[str, Any]) -> Optional[Any]:
        """Find order element that matches the parsed intent"""
        try:
            # Get all order elements
            order_elements = await page.query_selector_all('.order-card, .order-item, [data-testid="order"]')
            
            if not order_elements:
                order_elements = await page.query_selector_all('div[class*="order"]')
            
            typer.echo(f"🔍 Searching through {len(order_elements)} orders for match...")
            
            best_match = None
            max_score = 0
            
            for order_element in order_elements:
                score = await self.calculate_match_score(order_element, intent)
                typer.echo(f"📊 Order match score: {score}")
                
                if score > max_score:
                    max_score = score
                    best_match = order_element
            
            if max_score > 0:
                typer.echo(f"✅ Found matching order with score: {max_score}")
                return best_match
            else:
                typer.echo("❌ No matching order found")
                return None
                
        except Exception as e:
            typer.echo(f"❌ Error finding matching order: {str(e)}")
            return None
    
    async def calculate_match_score(self, order_element, intent: Dict[str, Any]) -> float:
        """Calculate how well an order matches the intent"""
        score = 0.0
        
        try:
            # Get order text content
            order_text = await order_element.inner_text()
            order_text_lower = order_text.lower()
            
            # Score based on color matches
            for color in intent.get('colors', []):
                if color in order_text_lower:
                    score += 2.0
            
            # Score based on product type matches
            for product in intent.get('products', []):
                if product in order_text_lower:
                    score += 3.0
            
            # Score based on general keyword matches
            for keyword in intent.get('keywords', []):
                if len(keyword) > 3 and keyword in order_text_lower:
                    score += 0.5
            
            # Check if return/replace action is available
            buttons = await order_element.query_selector_all('button, a')
            has_action_button = False
            
            for button in buttons:
                button_text = await button.inner_text()
                button_text_lower = button_text.lower()
                
                if intent['action'] == 'return' and 'return' in button_text_lower:
                    has_action_button = True
                    score += 1.0
                elif intent['action'] == 'replace' and ('replace' in button_text_lower or 'exchange' in button_text_lower):
                    has_action_button = True
                    score += 1.0
            
            # Penalize if action is not available
            if not has_action_button:
                score = 0.0
            
        except Exception as e:
            typer.echo(f"⚠️ Error calculating match score: {str(e)}")
            score = 0.0
        
        return score
    
    async def execute_return(self, page: Page, order_element) -> bool:
        """Execute return action for the specified order"""
        typer.echo("🔄 Executing return action...")
        
        try:
            # Find return button
            return_buttons = await order_element.query_selector_all('button, a')
            
            for button in return_buttons:
                button_text = await button.inner_text()
                if 'return' in button_text.lower():
                    typer.echo("🖱️ Clicking return button...")
                    await button.click()
                    
                    # Wait for return page/modal to load
                    await asyncio.sleep(3)
                    
                    # Handle return confirmation if needed
                    await self.handle_return_confirmation(page)
                    
                    typer.echo("✅ Return action completed")
                    return True
            
            typer.echo("❌ Return button not found")
            return False
            
        except Exception as e:
            typer.echo(f"❌ Error executing return: {str(e)}")
            return False
    
    async def execute_replace(self, page: Page, order_element) -> bool:
        """Execute replace action for the specified order"""
        typer.echo("🔄 Executing replace action...")
        
        try:
            # Find replace/exchange button
            replace_buttons = await order_element.query_selector_all('button, a')
            
            for button in replace_buttons:
                button_text = await button.inner_text()
                if 'replace' in button_text.lower() or 'exchange' in button_text.lower():
                    typer.echo("🖱️ Clicking replace button...")
                    await button.click()
                    
                    # Wait for replace page/modal to load
                    await asyncio.sleep(3)
                    
                    # Handle replace confirmation if needed
                    await self.handle_replace_confirmation(page)
                    
                    typer.echo("✅ Replace action completed")
                    return True
            
            typer.echo("❌ Replace button not found")
            return False
            
        except Exception as e:
            typer.echo(f"❌ Error executing replace: {str(e)}")
            return False
    
    async def handle_return_confirmation(self, page: Page):
        """Handle return confirmation steps"""
        try:
            # Look for reason selection
            reason_selectors = [
                'select[name*="reason"]',
                'input[name*="reason"]',
                '.reason-select',
                '[data-testid="return-reason"]'
            ]
            
            for selector in reason_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    
                    if selector.startswith('select'):
                        # Select a reason from dropdown
                        await page.select_option(selector, index=1)  # Select first available reason
                    else:
                        # Fill text input
                        await page.fill(selector, "Product not as expected")
                    
                    typer.echo("✅ Return reason selected")
                    break
                except:
                    continue
            
            # Look for confirmation button
            confirm_selectors = [
                'text="Confirm Return"',
                'text="Submit Return"',
                'button[type="submit"]',
                '.confirm-btn',
                '[data-testid="confirm-return"]'
            ]
            
            for selector in confirm_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    await page.click(selector)
                    typer.echo("✅ Return confirmed")
                    break
                except:
                    continue
                    
        except Exception as e:
            typer.echo(f"⚠️ Return confirmation not required or failed: {str(e)}")
    
    async def handle_replace_confirmation(self, page: Page):
        """Handle replace confirmation steps"""
        try:
            # Look for size/variant selection
            variant_selectors = [
                'select[name*="size"]',
                'select[name*="variant"]',
                '.size-select',
                '[data-testid="size-select"]'
            ]
            
            for selector in variant_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    await page.select_option(selector, index=1)  # Select first available option
                    typer.echo("✅ Replacement variant selected")
                    break
                except:
                    continue
            
            # Look for confirmation button
            confirm_selectors = [
                'text="Confirm Replace"',
                'text="Submit Exchange"',
                'button[type="submit"]',
                '.confirm-btn',
                '[data-testid="confirm-replace"]'
            ]
            
            for selector in confirm_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    await page.click(selector)
                    typer.echo("✅ Replace confirmed")
                    break
                except:
                    continue
                    
        except Exception as e:
            typer.echo(f"⚠️ Replace confirmation not required or failed: {str(e)}")
