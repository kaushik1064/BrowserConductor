"""
Order Agent for scraping order information from Ajio.com.
Extracts product details, prices, delivery status, and return information.
"""

import asyncio
import re
from typing import List, Dict, Any
from playwright.async_api import Page
from datetime import datetime, timedelta
import typer

from utils.crawl4ai_helper import CrawlHelper

class OrderAgent:
    def __init__(self):
        self.crawl_helper = CrawlHelper()
    
    async def navigate_to_orders(self, page: Page):
        """Navigate to My Orders page"""
        typer.echo("📦 Navigating to My Orders...")
        
        # Try multiple approaches to reach orders page
        try:
            # Method 1: Click on user account menu
            await page.wait_for_selector('text="My Account"', timeout=10000)
            await page.click('text="My Account"')
            await asyncio.sleep(1)
            
            # Click on My Orders
            await page.wait_for_selector('text="My Orders"', timeout=5000)
            await page.click('text="My Orders"')
            
        except:
            # Method 2: Direct URL navigation
            try:
                await page.goto('https://www.ajio.com/my-account/orders', wait_until='networkidle')
            except:
                typer.echo("❌ Could not navigate to orders page")
                return False
        
        # Wait for orders to load
        await asyncio.sleep(3)
        typer.echo("✅ Successfully navigated to orders page")
        return True
    
    async def extract_order_cards(self, page: Page) -> List[Dict[str, Any]]:
        """Extract order information from order cards"""
        orders = []
        
        try:
            # Wait for orders to load
            await page.wait_for_selector('.order-card, .order-item, [data-testid="order"]', timeout=10000)
            
            # Get all order elements
            order_elements = await page.query_selector_all('.order-card, .order-item, [data-testid="order"]')
            
            if not order_elements:
                # Try alternative selectors
                order_elements = await page.query_selector_all('div[class*="order"]')
            
            typer.echo(f"📋 Found {len(order_elements)} order elements")
            
            for i, order_element in enumerate(order_elements):
                try:
                    order_data = await self.extract_single_order(page, order_element, i)
                    if order_data:
                        orders.append(order_data)
                        typer.echo(f"✅ Extracted order: {order_data.get('product_name', 'Unknown')}")
                except Exception as e:
                    typer.echo(f"⚠️ Failed to extract order {i}: {str(e)}")
                    continue
        
        except Exception as e:
            typer.echo(f"❌ Error extracting orders: {str(e)}")
        
        return orders
    
    async def extract_single_order(self, page: Page, order_element, index: int) -> Dict[str, Any]:
        """Extract data from a single order element"""
        order_data = {}
        
        try:
            # Extract product name
            product_selectors = [
                '.product-name',
                '.item-name',
                '[data-testid="product-name"]',
                'h3',
                'h4',
                '.title'
            ]
            
            for selector in product_selectors:
                try:
                    product_element = await order_element.query_selector(selector)
                    if product_element:
                        order_data['product_name'] = await product_element.inner_text()
                        break
                except:
                    continue
            
            # Extract order ID
            order_id_selectors = [
                '.order-id',
                '[data-testid="order-id"]',
                'text="Order ID"',
                'span[class*="order"]'
            ]
            
            for selector in order_id_selectors:
                try:
                    order_id_element = await order_element.query_selector(selector)
                    if order_id_element:
                        text = await order_id_element.inner_text()
                        # Extract order ID from text using regex
                        order_id_match = re.search(r'(?:Order ID|#)\s*:?\s*([A-Z0-9]+)', text, re.IGNORECASE)
                        if order_id_match:
                            order_data['order_id'] = order_id_match.group(1)
                            break
                except:
                    continue
            
            # Extract price
            price_selectors = [
                '.price',
                '.amount',
                '[data-testid="price"]',
                'span[class*="price"]',
                'span[class*="amount"]'
            ]
            
            for selector in price_selectors:
                try:
                    price_element = await order_element.query_selector(selector)
                    if price_element:
                        price_text = await price_element.inner_text()
                        # Extract price using regex
                        price_match = re.search(r'₹\s*(\d+(?:,\d+)*(?:\.\d{2})?)', price_text)
                        if price_match:
                            order_data['price'] = f"₹{price_match.group(1)}"
                            break
                except:
                    continue
            
            # Extract image URL
            try:
                img_element = await order_element.query_selector('img')
                if img_element:
                    img_src = await img_element.get_attribute('src')
                    if img_src:
                        order_data['image_url'] = img_src if img_src.startswith('http') else f"https://www.ajio.com{img_src}"
            except:
                pass
            
            # Extract delivery status
            status_selectors = [
                '.status',
                '.delivery-status',
                '[data-testid="status"]',
                'span[class*="status"]'
            ]
            
            for selector in status_selectors:
                try:
                    status_element = await order_element.query_selector(selector)
                    if status_element:
                        order_data['delivery_status'] = await status_element.inner_text()
                        break
                except:
                    continue
            
            # Look for return/replace buttons
            return_buttons = await order_element.query_selector_all('button, a')
            order_data['has_return_option'] = False
            order_data['has_replace_option'] = False
            
            for button in return_buttons:
                try:
                    button_text = await button.inner_text()
                    if 'return' in button_text.lower():
                        order_data['has_return_option'] = True
                    if 'replace' in button_text.lower() or 'exchange' in button_text.lower():
                        order_data['has_replace_option'] = True
                except:
                    continue
            
            # Calculate return deadline (typically 7-30 days from delivery)
            if order_data.get('delivery_status', '').lower() == 'delivered':
                # Assume 7 days return policy (can be made configurable)
                order_data['return_deadline'] = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
            
            # Set default values for missing fields
            order_data.setdefault('product_name', f'Product {index + 1}')
            order_data.setdefault('order_id', f'ORDER_{index + 1}')
            order_data.setdefault('price', 'Price not found')
            order_data.setdefault('delivery_status', 'Status unknown')
            order_data.setdefault('image_url', '')
            order_data.setdefault('scraped_at', datetime.now().isoformat())
            
        except Exception as e:
            typer.echo(f"❌ Error extracting single order: {str(e)}")
        
        return order_data
    
    async def scrape_orders(self, page: Page) -> List[Dict[str, Any]]:
        """Main method to scrape all orders"""
        try:
            if not await self.navigate_to_orders(page):
                return []
            
            # Extract orders from current page
            orders = await self.extract_order_cards(page)
            
            # Check for pagination and scrape additional pages
            page_number = 1
            while True:
                try:
                    # Look for next page button
                    next_button = await page.query_selector('button[aria-label="Next"], .next-page, [data-testid="next-page"]')
                    if not next_button:
                        break
                    
                    # Check if next button is disabled
                    is_disabled = await next_button.get_attribute('disabled')
                    if is_disabled:
                        break
                    
                    # Click next page
                    await next_button.click()
                    await asyncio.sleep(3)
                    
                    page_number += 1
                    typer.echo(f"📄 Scraping page {page_number}...")
                    
                    # Extract orders from this page
                    page_orders = await self.extract_order_cards(page)
                    orders.extend(page_orders)
                    
                    # Safety limit to prevent infinite loops
                    if page_number >= 10:
                        typer.echo("⚠️ Reached maximum page limit (10)")
                        break
                        
                except Exception as e:
                    typer.echo(f"⚠️ Error navigating to next page: {str(e)}")
                    break
            
            typer.echo(f"✅ Successfully scraped {len(orders)} orders from {page_number} page(s)")
            return orders
            
        except Exception as e:
            typer.echo(f"❌ Error scraping orders: {str(e)}")
            return []
