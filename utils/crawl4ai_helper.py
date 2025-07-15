"""
Helper utilities for web scraping using crawl4ai and other scraping tools.
Provides enhanced content extraction and parsing capabilities.
"""

import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
import re
import typer

class CrawlHelper:
    def __init__(self):
        self.session = None
    
    async def get_session(self):
        """Get or create aiohttp session"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def extract_page_content(self, page) -> Dict[str, Any]:
        """Extract content from a Playwright page"""
        try:
            # Get page HTML
            html_content = await page.content()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract structured data
            content = {
                'title': await page.title(),
                'url': page.url,
                'text_content': soup.get_text(strip=True),
                'links': self.extract_links(soup),
                'images': await self.extract_images(page),
                'forms': self.extract_forms(soup),
                'metadata': self.extract_metadata(soup)
            }
            
            return content
            
        except Exception as e:
            typer.echo(f"❌ Error extracting page content: {str(e)}")
            return {}
    
    def extract_links(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract all links from the page"""
        links = []
        
        for link in soup.find_all('a', href=True):
            links.append({
                'url': link['href'],
                'text': link.get_text(strip=True),
                'title': link.get('title', '')
            })
        
        return links
    
    async def extract_images(self, page) -> List[Dict[str, str]]:
        """Extract image information from the page"""
        images = []
        
        try:
            img_elements = await page.query_selector_all('img')
            
            for img in img_elements:
                src = await img.get_attribute('src')
                alt = await img.get_attribute('alt')
                title = await img.get_attribute('title')
                
                if src:
                    images.append({
                        'src': src,
                        'alt': alt or '',
                        'title': title or ''
                    })
        
        except Exception as e:
            typer.echo(f"⚠️ Error extracting images: {str(e)}")
        
        return images
    
    def extract_forms(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract form information from the page"""
        forms = []
        
        for form in soup.find_all('form'):
            form_data = {
                'action': form.get('action', ''),
                'method': form.get('method', 'GET'),
                'inputs': []
            }
            
            # Extract input fields
            for input_field in form.find_all(['input', 'select', 'textarea']):
                field_info = {
                    'type': input_field.get('type', ''),
                    'name': input_field.get('name', ''),
                    'placeholder': input_field.get('placeholder', ''),
                    'required': input_field.has_attr('required')
                }
                form_data['inputs'].append(field_info)
            
            forms.append(form_data)
        
        return forms
    
    def extract_metadata(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract metadata from the page"""
        metadata = {}
        
        # Extract meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property') or meta.get('http-equiv')
            content = meta.get('content')
            
            if name and content:
                metadata[name] = content
        
        return metadata
    
    def extract_product_info(self, html_content: str) -> Dict[str, Any]:
        """Extract product information from HTML content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        product_info = {}
        
        # Common selectors for product information
        selectors = {
            'name': ['.product-name', '.item-name', 'h1', 'h2', '.title'],
            'price': ['.price', '.amount', '.cost', '[class*="price"]'],
            'description': ['.description', '.product-desc', '.details'],
            'rating': ['.rating', '.stars', '[class*="rating"]'],
            'availability': ['.stock', '.availability', '[class*="stock"]']
        }
        
        for field, field_selectors in selectors.items():
            for selector in field_selectors:
                element = soup.select_one(selector)
                if element:
                    product_info[field] = element.get_text(strip=True)
                    break
        
        return product_info
    
    def extract_order_details(self, html_content: str) -> List[Dict[str, Any]]:
        """Extract order details from HTML content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        orders = []
        
        # Find order containers
        order_containers = soup.find_all(['div', 'section'], class_=re.compile(r'order', re.I))
        
        for container in order_containers:
            order = {}
            
            # Extract order ID
            order_id_element = container.find(['span', 'div'], string=re.compile(r'order\s*id', re.I))
            if order_id_element:
                order['order_id'] = re.search(r'[A-Z0-9]+', order_id_element.get_text()).group()
            
            # Extract product name
            name_element = container.find(['h1', 'h2', 'h3', 'h4'], class_=re.compile(r'name|title', re.I))
            if name_element:
                order['product_name'] = name_element.get_text(strip=True)
            
            # Extract price
            price_element = container.find(['span', 'div'], class_=re.compile(r'price|amount', re.I))
            if price_element:
                price_match = re.search(r'₹\s*(\d+(?:,\d+)*(?:\.\d{2})?)', price_element.get_text())
                if price_match:
                    order['price'] = f"₹{price_match.group(1)}"
            
            # Extract status
            status_element = container.find(['span', 'div'], class_=re.compile(r'status', re.I))
            if status_element:
                order['delivery_status'] = status_element.get_text(strip=True)
            
            if order:
                orders.append(order)
        
        return orders
    
    async def scrape_url(self, url: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Scrape content from a URL"""
        try:
            session = await self.get_session()
            
            if not headers:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    html_content = await response.text()
                    
                    return {
                        'url': url,
                        'status': response.status,
                        'html_content': html_content,
                        'product_info': self.extract_product_info(html_content),
                        'orders': self.extract_order_details(html_content)
                    }
                else:
                    return {
                        'url': url,
                        'status': response.status,
                        'error': f'HTTP {response.status}'
                    }
        
        except Exception as e:
            return {
                'url': url,
                'error': str(e)
            }
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters
        text = re.sub(r'[^\w\s₹.,()-]', '', text)
        
        return text.strip()
    
    def extract_price_from_text(self, text: str) -> Optional[str]:
        """Extract price from text using regex patterns"""
        price_patterns = [
            r'₹\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
            r'Rs\.\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
            r'INR\s*(\d+(?:,\d+)*(?:\.\d{2})?)'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return f"₹{match.group(1)}"
        
        return None
    
    def extract_order_id_from_text(self, text: str) -> Optional[str]:
        """Extract order ID from text using regex patterns"""
        order_id_patterns = [
            r'(?:Order\s*ID|Order\s*#|#)\s*:?\s*([A-Z0-9]+)',
            r'\b([A-Z]{2,}\d{6,})\b',
            r'\b(\d{10,})\b'
        ]
        
        for pattern in order_id_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
