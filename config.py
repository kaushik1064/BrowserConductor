"""
Configuration settings for the Ajio.com automation system.
Contains URLs, timeouts, and other configurable parameters.
"""

import os
from typing import Dict, Any

class Config:
    """Configuration class for the automation system"""
    
    # Ajio.com URLs
    AJIO_BASE_URL = "https://www.ajio.com"
    AJIO_LOGIN_URL = "https://www.ajio.com/login"
    AJIO_ORDERS_URL = "https://www.ajio.com/my-account/orders"
    
    # Browser settings
    BROWSER_TIMEOUT = 30000  # 30 seconds
    PAGE_LOAD_TIMEOUT = 60000  # 60 seconds
    ELEMENT_TIMEOUT = 10000  # 10 seconds
    
    # Database settings
    DATABASE_PATH = "orders.db"
    BACKUP_RETENTION_DAYS = 30
    
    # Automation settings
    MAX_POPUP_ATTEMPTS = 3
    POPUP_WAIT_DELAY = 2  # seconds
    PAGE_SCROLL_DELAY = 1  # seconds
    ELEMENT_INTERACTION_DELAY = 0.5  # seconds
    
    # Return deadline settings
    DEFAULT_RETURN_PERIOD_DAYS = 7
    URGENT_DEADLINE_THRESHOLD_DAYS = 2
    
    # API settings
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL = "llama3-8b-8192"
    
    # User agent strings
    USER_AGENTS = [
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    ]
    
    # Selectors configuration
    SELECTORS = {
        'login': {
            'login_button': [
                '[data-testid="login-button"]',
                'text="Sign In"',
                'text="Login"',
                '.login-btn',
                '[title="Login"]',
                'a[href*="login"]'
            ],
            'phone_input': [
                'input[name="username"]',
                'input[placeholder*="phone"]',
                'input[placeholder*="mobile"]',
                'input[type="tel"]',
                '#username'
            ],
            'otp_button': [
                'text="Send OTP"',
                'text="Get OTP"',
                'button[type="submit"]',
                '.otp-btn',
                '[data-testid="send-otp"]'
            ],
            'otp_input': [
                'input[name="otp"]',
                'input[placeholder*="OTP"]',
                'input[placeholder*="code"]',
                '.otp-input',
                '[data-testid="otp-input"]'
            ],
            'verify_button': [
                'text="Verify"',
                'text="Login"',
                'text="Submit"',
                'button[type="submit"]',
                '.verify-btn',
                '[data-testid="verify-otp"]'
            ]
        },
        'orders': {
            'order_cards': [
                '.order-card',
                '.order-item',
                '[data-testid="order"]',
                'div[class*="order"]'
            ],
            'product_name': [
                '.product-name',
                '.item-name',
                '[data-testid="product-name"]',
                'h3',
                'h4',
                '.title'
            ],
            'order_id': [
                '.order-id',
                '[data-testid="order-id"]',
                'text="Order ID"',
                'span[class*="order"]'
            ],
            'price': [
                '.price',
                '.amount',
                '[data-testid="price"]',
                'span[class*="price"]',
                'span[class*="amount"]'
            ],
            'status': [
                '.status',
                '.delivery-status',
                '[data-testid="status"]',
                'span[class*="status"]'
            ]
        },
        'popups': {
            'cookie_accept': [
                'button:has-text("Accept")',
                'button:has-text("Accept All")',
                'button:has-text("I Accept")',
                '[data-testid="cookie-accept"]',
                '.cookie-accept',
                '#cookie-accept'
            ],
            'close_buttons': [
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
    }
    
    # Logging configuration
    LOGGING = {
        'level': 'INFO',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'file': 'ajio_automation.log'
    }
    
    @classmethod
    def get_selector_list(cls, category: str, selector_type: str) -> list:
        """Get list of selectors for a specific category and type"""
        return cls.SELECTORS.get(category, {}).get(selector_type, [])
    
    @classmethod
    def get_user_agent(cls, index: int = 0) -> str:
        """Get user agent string by index"""
        return cls.USER_AGENTS[index % len(cls.USER_AGENTS)]
    
    @classmethod
    def get_browser_options(cls, headless: bool = True) -> Dict[str, Any]:
        """Get browser launch options"""
        return {
            'headless': headless,
            'args': [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        }
    
    @classmethod
    def get_page_options(cls) -> Dict[str, Any]:
        """Get page creation options"""
        return {
            'viewport': {'width': 1920, 'height': 1080},
            'user_agent': cls.get_user_agent()
        }
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate configuration settings"""
        errors = []
        
        # Check required URLs
        if not cls.AJIO_BASE_URL:
            errors.append("AJIO_BASE_URL is required")
        
        # Check timeout values
        if cls.BROWSER_TIMEOUT <= 0:
            errors.append("BROWSER_TIMEOUT must be positive")
        
        if cls.PAGE_LOAD_TIMEOUT <= 0:
            errors.append("PAGE_LOAD_TIMEOUT must be positive")
        
        # Check database path
        if not cls.DATABASE_PATH:
            errors.append("DATABASE_PATH is required")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
        
        return True

# Environment-specific configurations
class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    BROWSER_TIMEOUT = 60000  # Longer timeouts for debugging
    PAGE_LOAD_TIMEOUT = 120000

class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    BROWSER_TIMEOUT = 30000
    PAGE_LOAD_TIMEOUT = 60000

class TestConfig(Config):
    """Test environment configuration"""
    DEBUG = True
    DATABASE_PATH = "test_orders.db"
    BROWSER_TIMEOUT = 15000
    PAGE_LOAD_TIMEOUT = 30000

# Get configuration based on environment
def get_config() -> Config:
    """Get configuration based on environment variable"""
    env = os.getenv('AJIO_ENV', 'development').lower()
    
    if env == 'production':
        return ProductionConfig()
    elif env == 'test':
        return TestConfig()
    else:
        return DevelopmentConfig()
