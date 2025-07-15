"""
Routes for the Ajio.com automation web application.
Provides web interface for automation system functionality.
"""

import asyncio
import threading
from datetime import datetime
from flask import render_template, jsonify, request, redirect, url_for, flash
from app import app, db
from models_flask import Order, Session, Reminder
from agents.login_agent import LoginAgent
from agents.order_agent import OrderAgent
from agents.return_agent import ReturnAgent
from agents.reminder_agent import ReminderAgent
from config import Config

# Global variables to track automation status
automation_status = {
    'running': False,
    'status': 'idle',
    'message': '',
    'orders': [],
    'error': None
}

@app.route('/')
def dashboard():
    """Main dashboard showing system status and features"""
    return render_template('dashboard.html')

@app.route('/api/status')
def api_status():
    """API endpoint to get system status"""
    try:
        # Get orders count from database
        orders_count = Order.query.count()
        
        status = {
            'status': 'running',
            'timestamp': datetime.now().isoformat(),
            'database': {
                'initialized': True,
                'orders_count': orders_count,
                'tables': ['orders', 'sessions', 'reminders']
            },
            'features': {
                'browser_automation': True,
                'order_scraping': True,
                'return_management': True,
                'deadline_reminders': True
            },
            'agents': {
                'login_agent': 'Available',
                'order_agent': 'Available', 
                'return_agent': 'Available',
                'reminder_agent': 'Available'
            }
        }
        
        return jsonify(status)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/orders')
def api_orders():
    """API endpoint to get saved orders"""
    try:
        orders = Order.query.order_by(Order.scraped_at.desc()).all()
        orders_data = [order.to_dict() for order in orders]
        
        return jsonify({
            'orders': orders_data,
            'count': len(orders_data)
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/reminders')
def api_reminders():
    """API endpoint to check reminders"""
    try:
        # Get orders with upcoming return deadlines
        reminder_agent = ReminderAgent()
        reminders = reminder_agent.check_reminders()
        
        return jsonify({
            'reminders': reminders or [],
            'count': len(reminders) if reminders else 0
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/config')
def api_config():
    """API endpoint to get system configuration"""
    try:
        config = Config()
        
        return jsonify({
            'ajio_base_url': config.AJIO_BASE_URL,
            'timeouts': {
                'browser': config.BROWSER_TIMEOUT,
                'page_load': config.PAGE_LOAD_TIMEOUT,
                'element': config.ELEMENT_TIMEOUT
            },
            'automation': {
                'headless_mode': True,
                'popup_handling': True,
                'user_agent_rotation': True
            },
            'features': {
                'natural_language_commands': bool(config.GROQ_API_KEY),
                'deadline_tracking': True,
                'order_management': True
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/automation/start', methods=['POST'])
def start_automation():
    """Start the automation process"""
    global automation_status
    
    if automation_status['running']:
        return jsonify({
            'error': 'Automation is already running'
        }), 400
    
    try:
        data = request.get_json() or {}
        phone_number = data.get('phone_number')
        command = data.get('command')
        headless = data.get('headless', True)
        
        # Start automation in background thread
        automation_status['running'] = True
        automation_status['status'] = 'starting'
        automation_status['message'] = 'Initializing automation...'
        automation_status['error'] = None
        
        def run_automation():
            asyncio.run(run_automation_workflow(phone_number, command, headless))
        
        thread = threading.Thread(target=run_automation)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'status': 'started',
            'message': 'Automation started successfully'
        })
        
    except Exception as e:
        automation_status['running'] = False
        automation_status['error'] = str(e)
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/automation/status')
def automation_status_api():
    """Get current automation status"""
    return jsonify(automation_status)

@app.route('/automation/stop', methods=['POST'])
def stop_automation():
    """Stop the automation process"""
    global automation_status
    
    automation_status['running'] = False
    automation_status['status'] = 'stopped'
    automation_status['message'] = 'Automation stopped by user'
    
    return jsonify({
        'status': 'stopped',
        'message': 'Automation stopped successfully'
    })

async def run_automation_workflow(phone_number, command, headless):
    """Run the automation workflow in background"""
    global automation_status
    
    try:
        automation_status['status'] = 'initializing'
        automation_status['message'] = 'Initializing agents...'
        
        # Initialize agents
        login_agent = LoginAgent(headless=headless)
        order_agent = OrderAgent()
        return_agent = ReturnAgent()
        reminder_agent = ReminderAgent()
        
        automation_status['status'] = 'connecting'
        automation_status['message'] = 'Starting browser and connecting to Ajio...'
        
        # Start browser and login
        await login_agent.start_browser()
        success = await login_agent.login(phone_number)
        
        if not success:
            automation_status['error'] = 'Login failed'
            automation_status['status'] = 'failed'
            return
        
        automation_status['status'] = 'scraping'
        automation_status['message'] = 'Scraping order information...'
        
        # Scrape orders
        orders = await order_agent.scrape_orders(login_agent.page)
        
        if orders:
            automation_status['message'] = f'Found {len(orders)} orders, saving to database...'
            
            # Save orders to database
            for order_data in orders:
                existing_order = Order.query.filter_by(order_id=order_data.get('order_id')).first()
                
                if existing_order:
                    # Update existing order
                    for key, value in order_data.items():
                        if hasattr(existing_order, key):
                            setattr(existing_order, key, value)
                    existing_order.updated_at = datetime.utcnow()
                else:
                    # Create new order
                    new_order = Order(
                        order_id=order_data.get('order_id'),
                        product_name=order_data.get('product_name'),
                        price=order_data.get('price'),
                        image_url=order_data.get('image_url'),
                        delivery_status=order_data.get('delivery_status'),
                        has_return_option=order_data.get('has_return_option', False),
                        has_replace_option=order_data.get('has_replace_option', False),
                        return_deadline=order_data.get('return_deadline')
                    )
                    db.session.add(new_order)
            
            db.session.commit()
            automation_status['orders'] = orders
        
        # Handle return/replace commands
        if command:
            automation_status['status'] = 'processing_command'
            automation_status['message'] = f'Processing command: {command}'
            await return_agent.process_command(login_agent.page, command)
        
        automation_status['status'] = 'completed'
        automation_status['message'] = 'Automation completed successfully'
        
    except Exception as e:
        automation_status['error'] = str(e)
        automation_status['status'] = 'failed'
        automation_status['message'] = f'Automation failed: {str(e)}'
    
    finally:
        automation_status['running'] = False
        if 'login_agent' in locals():
            await login_agent.close_browser()

# Import routes to register them with the app
@app.route('/orders')
def orders_page():
    """Orders management page"""
    orders = Order.query.order_by(Order.scraped_at.desc()).all()
    return render_template('orders.html', orders=orders)

@app.route('/automation')
def automation_page():
    """Automation control page"""
    return render_template('automation.html')