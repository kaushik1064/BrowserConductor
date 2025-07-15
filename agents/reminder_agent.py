"""
Reminder Agent for tracking return deadlines and managing order database.
Handles SQLite operations and deadline notifications.
"""

import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import typer

from utils.database import get_db_connection
# from models.order import Order  # No longer needed as we're using Flask-SQLAlchemy

class ReminderAgent:
    def __init__(self):
        self.db_path = "orders.db"
    
    def save_order(self, order_data: Dict[str, Any]) -> bool:
        """Save order to database"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Insert or update order
                cursor.execute("""
                    INSERT OR REPLACE INTO orders (
                        order_id, product_name, price, image_url, delivery_status,
                        has_return_option, has_replace_option, return_deadline,
                        scraped_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    order_data.get('order_id'),
                    order_data.get('product_name'),
                    order_data.get('price'),
                    order_data.get('image_url'),
                    order_data.get('delivery_status'),
                    order_data.get('has_return_option', False),
                    order_data.get('has_replace_option', False),
                    order_data.get('return_deadline'),
                    order_data.get('scraped_at'),
                    datetime.now().isoformat()
                ))
                
                conn.commit()
                typer.echo(f"💾 Saved order: {order_data.get('product_name')}")
                return True
                
        except Exception as e:
            typer.echo(f"❌ Error saving order: {str(e)}")
            return False
    
    def get_all_orders(self) -> List[Dict[str, Any]]:
        """Get all orders from database"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM orders ORDER BY scraped_at DESC")
                rows = cursor.fetchall()
                
                orders = []
                for row in rows:
                    order = {
                        'id': row[0],
                        'order_id': row[1],
                        'product_name': row[2],
                        'price': row[3],
                        'image_url': row[4],
                        'delivery_status': row[5],
                        'has_return_option': bool(row[6]),
                        'has_replace_option': bool(row[7]),
                        'return_deadline': row[8],
                        'scraped_at': row[9],
                        'updated_at': row[10]
                    }
                    orders.append(order)
                
                return orders
                
        except Exception as e:
            typer.echo(f"❌ Error fetching orders: {str(e)}")
            return []
    
    def get_orders_with_deadlines(self) -> List[Dict[str, Any]]:
        """Get orders that have return deadlines"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM orders 
                    WHERE return_deadline IS NOT NULL 
                    AND return_deadline != ''
                    ORDER BY return_deadline ASC
                """)
                rows = cursor.fetchall()
                
                orders = []
                for row in rows:
                    order = {
                        'id': row[0],
                        'order_id': row[1],
                        'product_name': row[2],
                        'price': row[3],
                        'image_url': row[4],
                        'delivery_status': row[5],
                        'has_return_option': bool(row[6]),
                        'has_replace_option': bool(row[7]),
                        'return_deadline': row[8],
                        'scraped_at': row[9],
                        'updated_at': row[10]
                    }
                    orders.append(order)
                
                return orders
                
        except Exception as e:
            typer.echo(f"❌ Error fetching orders with deadlines: {str(e)}")
            return []
    
    def check_reminders(self) -> List[Dict[str, Any]]:
        """Check for orders with approaching return deadlines"""
        urgent_orders = []
        
        try:
            orders = self.get_orders_with_deadlines()
            current_date = datetime.now().date()
            
            for order in orders:
                if order['return_deadline']:
                    try:
                        deadline_date = datetime.strptime(order['return_deadline'], '%Y-%m-%d').date()
                        days_until_deadline = (deadline_date - current_date).days
                        
                        if days_until_deadline <= 2:
                            order['days_until_deadline'] = days_until_deadline
                            urgent_orders.append(order)
                            
                            # Display reminder
                            if days_until_deadline < 0:
                                typer.echo(f"🚨 EXPIRED: Return deadline for '{order['product_name']}' was {abs(days_until_deadline)} days ago!")
                            elif days_until_deadline == 0:
                                typer.echo(f"⚠️ URGENT: Return deadline for '{order['product_name']}' is TODAY!")
                            else:
                                typer.echo(f"⏰ REMINDER: Return deadline for '{order['product_name']}' is in {days_until_deadline} day(s)")
                                
                    except ValueError:
                        typer.echo(f"⚠️ Invalid date format for order: {order['product_name']}")
                        continue
            
            if not urgent_orders:
                typer.echo("✅ No urgent return deadlines")
            else:
                typer.echo(f"📋 Found {len(urgent_orders)} orders with urgent return deadlines")
                
        except Exception as e:
            typer.echo(f"❌ Error checking reminders: {str(e)}")
        
        return urgent_orders
    
    def update_order_status(self, order_id: str, status: str) -> bool:
        """Update order delivery status"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE orders 
                    SET delivery_status = ?, updated_at = ?
                    WHERE order_id = ?
                """, (status, datetime.now().isoformat(), order_id))
                
                conn.commit()
                
                if cursor.rowcount > 0:
                    typer.echo(f"✅ Updated status for order {order_id}: {status}")
                    return True
                else:
                    typer.echo(f"⚠️ Order {order_id} not found")
                    return False
                    
        except Exception as e:
            typer.echo(f"❌ Error updating order status: {str(e)}")
            return False
    
    def delete_order(self, order_id: str) -> bool:
        """Delete order from database"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM orders WHERE order_id = ?", (order_id,))
                conn.commit()
                
                if cursor.rowcount > 0:
                    typer.echo(f"🗑️ Deleted order: {order_id}")
                    return True
                else:
                    typer.echo(f"⚠️ Order {order_id} not found")
                    return False
                    
        except Exception as e:
            typer.echo(f"❌ Error deleting order: {str(e)}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get order statistics"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Total orders
                cursor.execute("SELECT COUNT(*) FROM orders")
                total_orders = cursor.fetchone()[0]
                
                # Orders by status
                cursor.execute("SELECT delivery_status, COUNT(*) FROM orders GROUP BY delivery_status")
                status_counts = dict(cursor.fetchall())
                
                # Orders with return options
                cursor.execute("SELECT COUNT(*) FROM orders WHERE has_return_option = 1")
                returnable_orders = cursor.fetchone()[0]
                
                # Orders with upcoming deadlines
                cursor.execute("""
                    SELECT COUNT(*) FROM orders 
                    WHERE return_deadline IS NOT NULL 
                    AND return_deadline != ''
                    AND date(return_deadline) >= date('now')
                """)
                upcoming_deadlines = cursor.fetchone()[0]
                
                stats = {
                    'total_orders': total_orders,
                    'status_counts': status_counts,
                    'returnable_orders': returnable_orders,
                    'upcoming_deadlines': upcoming_deadlines
                }
                
                return stats
                
        except Exception as e:
            typer.echo(f"❌ Error getting statistics: {str(e)}")
            return {}
