from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from datetime import datetime

# Import db from app to avoid circular imports
def get_db():
    from app import db
    return db

db = get_db()

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(String(255), unique=True, nullable=False)
    product_name = Column(String(500), nullable=False)
    price = Column(String(100))
    image_url = Column(Text)
    delivery_status = Column(String(100))
    has_return_option = Column(Boolean, default=False)
    has_replace_option = Column(Boolean, default=False)
    return_deadline = Column(String(100))
    scraped_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_name': self.product_name,
            'price': self.price,
            'image_url': self.image_url,
            'delivery_status': self.delivery_status,
            'has_return_option': self.has_return_option,
            'has_replace_option': self.has_replace_option,
            'return_deadline': self.return_deadline,
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Session(db.Model):
    __tablename__ = 'sessions'
    
    id = Column(Integer, primary_key=True)
    session_data = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Reminder(db.Model):
    __tablename__ = 'reminders'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(String(255), nullable=False)
    reminder_type = Column(String(100), nullable=False)
    reminder_date = Column(DateTime, nullable=False)
    is_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)