"""
Order model for representing order data structure.
Defines the schema and validation for order information.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime
import json

@dataclass
class Order:
    """Order data model with validation and serialization capabilities"""
    
    order_id: str
    product_name: str
    price: Optional[str] = None
    image_url: Optional[str] = None
    delivery_status: Optional[str] = None
    has_return_option: bool = False
    has_replace_option: bool = False
    return_deadline: Optional[str] = None
    scraped_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def __post_init__(self):
        """Validate and set default values after initialization"""
        if not self.order_id:
            raise ValueError("Order ID is required")
        
        if not self.product_name:
            raise ValueError("Product name is required")
        
        # Set default timestamps
        current_time = datetime.now().isoformat()
        if not self.scraped_at:
            self.scraped_at = current_time
        
        if not self.updated_at:
            self.updated_at = current_time
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Order':
        """Create Order instance from dictionary"""
        return cls(
            order_id=data.get('order_id', ''),
            product_name=data.get('product_name', ''),
            price=data.get('price'),
            image_url=data.get('image_url'),
            delivery_status=data.get('delivery_status'),
            has_return_option=bool(data.get('has_return_option', False)),
            has_replace_option=bool(data.get('has_replace_option', False)),
            return_deadline=data.get('return_deadline'),
            scraped_at=data.get('scraped_at'),
            updated_at=data.get('updated_at')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Order instance to dictionary"""
        return {
            'order_id': self.order_id,
            'product_name': self.product_name,
            'price': self.price,
            'image_url': self.image_url,
            'delivery_status': self.delivery_status,
            'has_return_option': self.has_return_option,
            'has_replace_option': self.has_replace_option,
            'return_deadline': self.return_deadline,
            'scraped_at': self.scraped_at,
            'updated_at': self.updated_at
        }
    
    def to_json(self) -> str:
        """Convert Order instance to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Order':
        """Create Order instance from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def is_returnable(self) -> bool:
        """Check if order is eligible for return"""
        if not self.has_return_option:
            return False
        
        if not self.return_deadline:
            return False
        
        try:
            deadline_date = datetime.strptime(self.return_deadline, '%Y-%m-%d').date()
            current_date = datetime.now().date()
            return current_date <= deadline_date
        except ValueError:
            return False
    
    def is_replaceable(self) -> bool:
        """Check if order is eligible for replacement"""
        return self.has_replace_option and self.is_returnable()
    
    def days_until_deadline(self) -> Optional[int]:
        """Get number of days until return deadline"""
        if not self.return_deadline:
            return None
        
        try:
            deadline_date = datetime.strptime(self.return_deadline, '%Y-%m-%d').date()
            current_date = datetime.now().date()
            return (deadline_date - current_date).days
        except ValueError:
            return None
    
    def is_deadline_urgent(self, threshold_days: int = 2) -> bool:
        """Check if return deadline is approaching within threshold"""
        days_left = self.days_until_deadline()
        if days_left is None:
            return False
        return days_left <= threshold_days
    
    def get_status_emoji(self) -> str:
        """Get emoji representation of delivery status"""
        status_emojis = {
            'delivered': '✅',
            'shipped': '🚚',
            'processing': '⏳',
            'confirmed': '📋',
            'cancelled': '❌',
            'returned': '🔄',
            'refunded': '💰'
        }
        
        if self.delivery_status:
            status_lower = self.delivery_status.lower()
            for key, emoji in status_emojis.items():
                if key in status_lower:
                    return emoji
        
        return '📦'  # Default package emoji
    
    def get_summary(self) -> str:
        """Get a formatted summary of the order"""
        emoji = self.get_status_emoji()
        summary = f"{emoji} {self.product_name}"
        
        if self.price:
            summary += f" - {self.price}"
        
        if self.delivery_status:
            summary += f" ({self.delivery_status})"
        
        if self.return_deadline and self.is_returnable():
            days_left = self.days_until_deadline()
            if days_left is not None:
                if days_left < 0:
                    summary += f" - Return deadline expired!"
                elif days_left == 0:
                    summary += f" - Return deadline TODAY!"
                else:
                    summary += f" - {days_left} days to return"
        
        return summary
    
    def update_status(self, new_status: str):
        """Update delivery status and timestamp"""
        self.delivery_status = new_status
        self.updated_at = datetime.now().isoformat()
    
    def validate(self) -> bool:
        """Validate order data"""
        errors = []
        
        if not self.order_id or not self.order_id.strip():
            errors.append("Order ID cannot be empty")
        
        if not self.product_name or not self.product_name.strip():
            errors.append("Product name cannot be empty")
        
        if self.return_deadline:
            try:
                datetime.strptime(self.return_deadline, '%Y-%m-%d')
            except ValueError:
                errors.append("Return deadline must be in YYYY-MM-DD format")
        
        if self.scraped_at:
            try:
                datetime.fromisoformat(self.scraped_at.replace('Z', '+00:00'))
            except ValueError:
                errors.append("Invalid scraped_at timestamp format")
        
        if errors:
            raise ValueError(f"Validation errors: {', '.join(errors)}")
        
        return True
    
    def __str__(self) -> str:
        """String representation of the order"""
        return f"Order({self.order_id}: {self.product_name})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the order"""
        return f"Order(order_id='{self.order_id}', product_name='{self.product_name}', status='{self.delivery_status}')"
