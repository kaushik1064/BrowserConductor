"""
Test suite for the Ajio.com automation agents.
Uses pytest for testing browser automation functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

from agents.login_agent import LoginAgent
from agents.order_agent import OrderAgent
from agents.return_agent import ReturnAgent
from agents.reminder_agent import ReminderAgent
from models.order import Order
from utils.database import init_database, get_db_connection
from config import TestConfig

# Test configuration
@pytest.fixture
def test_config():
    return TestConfig()

@pytest.fixture
def test_database():
    """Set up test database"""
    init_database()
    yield
    # Cleanup after tests
    import os
    if os.path.exists(TestConfig.DATABASE_PATH):
        os.remove(TestConfig.DATABASE_PATH)

@pytest.fixture
def mock_page():
    """Mock Playwright page object"""
    page = AsyncMock()
    page.url = "https://www.ajio.com"
    page.title.return_value = "Ajio - Test Page"
    page.content.return_value = "<html><body>Test Content</body></html>"
    return page

@pytest.fixture
def sample_order_data():
    """Sample order data for testing"""
    return {
        'order_id': 'TEST123456',
        'product_name': 'Test Product',
        'price': '₹1,999',
        'image_url': 'https://example.com/image.jpg',
        'delivery_status': 'Delivered',
        'has_return_option': True,
        'has_replace_option': False,
        'return_deadline': (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d'),
        'scraped_at': datetime.now().isoformat()
    }

class TestLoginAgent:
    """Test cases for LoginAgent"""
    
    @pytest.mark.asyncio
    async def test_start_browser(self):
        """Test browser initialization"""
        login_agent = LoginAgent(headless=True)
        
        with patch('agents.login_agent.async_playwright') as mock_playwright:
            mock_pw = AsyncMock()
            mock_playwright.return_value.start.return_value = mock_pw
            
            mock_browser = AsyncMock()
            mock_pw.chromium.launch.return_value = mock_browser
            
            mock_page = AsyncMock()
            mock_browser.new_page.return_value = mock_page
            
            await login_agent.start_browser()
            
            assert login_agent.browser == mock_browser
            assert login_agent.page == mock_page
            mock_pw.chromium.launch.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_navigate_to_ajio(self, mock_page):
        """Test navigation to Ajio homepage"""
        login_agent = LoginAgent()
        login_agent.page = mock_page
        
        with patch.object(login_agent.popup_handler, 'dismiss_popups', new_callable=AsyncMock):
            await login_agent.navigate_to_ajio()
            
            mock_page.goto.assert_called_once_with(
                TestConfig.AJIO_BASE_URL, 
                wait_until='networkidle'
            )
    
    @pytest.mark.asyncio
    async def test_click_login_button_success(self, mock_page):
        """Test successful login button click"""
        login_agent = LoginAgent()
        login_agent.page = mock_page
        
        # Mock successful selector find
        mock_page.wait_for_selector.return_value = True
        mock_page.click.return_value = None
        
        result = await login_agent.click_login_button()
        
        assert result is True
        mock_page.click.assert_called()
    
    @pytest.mark.asyncio
    async def test_enter_phone_number(self, mock_page):
        """Test phone number entry"""
        login_agent = LoginAgent()
        login_agent.page = mock_page
        
        # Mock successful input field find
        mock_page.wait_for_selector.return_value = True
        mock_page.fill.return_value = None
        
        result = await login_agent.enter_phone_number("9876543210")
        
        assert result is True
        mock_page.fill.assert_called()

class TestOrderAgent:
    """Test cases for OrderAgent"""
    
    @pytest.mark.asyncio
    async def test_navigate_to_orders(self, mock_page):
        """Test navigation to orders page"""
        order_agent = OrderAgent()
        
        # Mock successful navigation
        mock_page.wait_for_selector.return_value = True
        mock_page.click.return_value = None
        
        result = await order_agent.navigate_to_orders(mock_page)
        
        assert result is True
        mock_page.click.assert_called()
    
    @pytest.mark.asyncio
    async def test_extract_single_order(self, mock_page, sample_order_data):
        """Test extraction of single order data"""
        order_agent = OrderAgent()
        
        # Mock order element
        mock_order_element = AsyncMock()
        mock_order_element.query_selector.side_effect = self._mock_query_selector
        mock_order_element.query_selector_all.return_value = []
        
        result = await order_agent.extract_single_order(mock_page, mock_order_element, 0)
        
        assert 'product_name' in result
        assert 'order_id' in result
    
    def _mock_query_selector(self, selector):
        """Helper to mock query_selector results"""
        mock_element = AsyncMock()
        if 'product' in selector or 'name' in selector:
            mock_element.inner_text.return_value = "Test Product"
            return mock_element
        elif 'order' in selector:
            mock_element.inner_text.return_value = "Order ID: TEST123"
            return mock_element
        elif 'price' in selector:
            mock_element.inner_text.return_value = "₹1,999"
            return mock_element
        return None

class TestReturnAgent:
    """Test cases for ReturnAgent"""
    
    def test_parse_command_return(self):
        """Test parsing return command"""
        return_agent = ReturnAgent()
        
        command = "return my red shoes"
        intent = return_agent.parse_command(command)
        
        assert intent['action'] == 'return'
        assert 'red' in intent['colors']
        assert 'shoes' in intent['products']
    
    def test_parse_command_replace(self):
        """Test parsing replace command"""
        return_agent = ReturnAgent()
        
        command = "replace blue shirt"
        intent = return_agent.parse_command(command)
        
        assert intent['action'] == 'replace'
        assert 'blue' in intent['colors']
        assert 'shirt' in intent['products']
    
    @pytest.mark.asyncio
    async def test_calculate_match_score(self):
        """Test order matching score calculation"""
        return_agent = ReturnAgent()
        
        # Mock order element
        mock_element = AsyncMock()
        mock_element.inner_text.return_value = "Red Nike Shoes - ₹2,999 - Delivered"
        mock_element.query_selector_all.return_value = [
            self._create_mock_button("Return Item")
        ]
        
        intent = {
            'action': 'return',
            'colors': ['red'],
            'products': ['shoes'],
            'keywords': ['return', 'my', 'red', 'shoes']
        }
        
        score = await return_agent.calculate_match_score(mock_element, intent)
        
        assert score > 0  # Should have positive score for matching order
    
    def _create_mock_button(self, text):
        """Helper to create mock button element"""
        button = AsyncMock()
        button.inner_text.return_value = text
        return button

class TestReminderAgent:
    """Test cases for ReminderAgent"""
    
    def test_save_order(self, test_database, sample_order_data):
        """Test saving order to database"""
        reminder_agent = ReminderAgent()
        
        result = reminder_agent.save_order(sample_order_data)
        
        assert result is True
        
        # Verify order was saved
        orders = reminder_agent.get_all_orders()
        assert len(orders) == 1
        assert orders[0]['order_id'] == sample_order_data['order_id']
    
    def test_check_reminders_urgent(self, test_database):
        """Test checking for urgent reminders"""
        reminder_agent = ReminderAgent()
        
        # Create order with deadline tomorrow
        urgent_order = {
            'order_id': 'URGENT123',
            'product_name': 'Urgent Product',
            'price': '₹999',
            'delivery_status': 'Delivered',
            'has_return_option': True,
            'return_deadline': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'scraped_at': datetime.now().isoformat()
        }
        
        reminder_agent.save_order(urgent_order)
        urgent_orders = reminder_agent.check_reminders()
        
        assert len(urgent_orders) == 1
        assert urgent_orders[0]['order_id'] == 'URGENT123'
    
    def test_get_statistics(self, test_database, sample_order_data):
        """Test getting order statistics"""
        reminder_agent = ReminderAgent()
        reminder_agent.save_order(sample_order_data)
        
        stats = reminder_agent.get_statistics()
        
        assert stats['total_orders'] == 1
        assert stats['returnable_orders'] == 1
        assert 'Delivered' in stats['status_counts']

class TestOrderModel:
    """Test cases for Order model"""
    
    def test_order_creation(self, sample_order_data):
        """Test creating Order instance"""
        order = Order.from_dict(sample_order_data)
        
        assert order.order_id == sample_order_data['order_id']
        assert order.product_name == sample_order_data['product_name']
        assert order.price == sample_order_data['price']
    
    def test_order_validation(self):
        """Test order validation"""
        # Valid order
        valid_order = Order(
            order_id='TEST123',
            product_name='Test Product'
        )
        assert valid_order.validate() is True
        
        # Invalid order - empty order_id
        with pytest.raises(ValueError):
            Order(order_id='', product_name='Test Product')
    
    def test_is_returnable(self, sample_order_data):
        """Test return eligibility check"""
        order = Order.from_dict(sample_order_data)
        
        assert order.is_returnable() is True
        
        # Test expired deadline
        order.return_deadline = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        assert order.is_returnable() is False
    
    def test_days_until_deadline(self, sample_order_data):
        """Test deadline calculation"""
        order = Order.from_dict(sample_order_data)
        
        days_left = order.days_until_deadline()
        assert days_left == 5  # Set to 5 days in sample data
    
    def test_is_deadline_urgent(self, sample_order_data):
        """Test urgent deadline detection"""
        # Set deadline to tomorrow
        sample_order_data['return_deadline'] = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        order = Order.from_dict(sample_order_data)
        
        assert order.is_deadline_urgent(threshold_days=2) is True
        
        # Set deadline to next week
        sample_order_data['return_deadline'] = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        order = Order.from_dict(sample_order_data)
        
        assert order.is_deadline_urgent(threshold_days=2) is False
    
    def test_get_summary(self, sample_order_data):
        """Test order summary generation"""
        order = Order.from_dict(sample_order_data)
        
        summary = order.get_summary()
        
        assert order.product_name in summary
        assert order.price in summary
        assert order.delivery_status in summary

class TestIntegration:
    """Integration tests"""
    
    @pytest.mark.asyncio
    async def test_full_workflow_mock(self, test_database, sample_order_data):
        """Test full workflow with mocked components"""
        # Mock login
        login_agent = LoginAgent(headless=True)
        
        with patch.object(login_agent, 'start_browser', new_callable=AsyncMock):
            with patch.object(login_agent, 'login', new_callable=AsyncMock) as mock_login:
                mock_login.return_value = True
                
                # Mock order scraping
                order_agent = OrderAgent()
                with patch.object(order_agent, 'scrape_orders', new_callable=AsyncMock) as mock_scrape:
                    mock_scrape.return_value = [sample_order_data]
                    
                    # Mock reminder agent
                    reminder_agent = ReminderAgent()
                    
                    # Simulate workflow
                    await login_agent.start_browser()
                    login_success = await login_agent.login("9876543210")
                    assert login_success is True
                    
                    orders = await order_agent.scrape_orders(None)
                    assert len(orders) == 1
                    
                    # Save order
                    reminder_agent.save_order(orders[0])
                    
                    # Check reminders
                    urgent_orders = reminder_agent.check_reminders()
                    assert isinstance(urgent_orders, list)

# Pytest configuration
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )

# Test utilities
class TestUtils:
    """Utility functions for testing"""
    
    @staticmethod
    def create_mock_order_element(product_name: str, order_id: str, price: str):
        """Create a mock order element for testing"""
        element = AsyncMock()
        
        def mock_query_selector(selector):
            mock_el = AsyncMock()
            if 'product' in selector or 'name' in selector:
                mock_el.inner_text.return_value = product_name
                return mock_el
            elif 'order' in selector:
                mock_el.inner_text.return_value = f"Order ID: {order_id}"
                return mock_el
            elif 'price' in selector:
                mock_el.inner_text.return_value = price
                return mock_el
            return None
        
        element.query_selector.side_effect = mock_query_selector
        element.query_selector_all.return_value = []
        
        return element
    
    @staticmethod
    def create_test_order(order_id: str = "TEST123", days_until_deadline: int = 5):
        """Create a test order with specified deadline"""
        return {
            'order_id': order_id,
            'product_name': f'Test Product {order_id}',
            'price': '₹1,999',
            'image_url': 'https://example.com/image.jpg',
            'delivery_status': 'Delivered',
            'has_return_option': True,
            'has_replace_option': False,
            'return_deadline': (datetime.now() + timedelta(days=days_until_deadline)).strftime('%Y-%m-%d'),
            'scraped_at': datetime.now().isoformat()
        }

if __name__ == "__main__":
    pytest.main([__file__])
