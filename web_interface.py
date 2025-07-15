#!/usr/bin/env python3
"""
Simple web interface for Ajio.com automation system demo.
Provides a basic dashboard to showcase the application's capabilities.
"""

from flask import Flask, render_template, jsonify, request
import json
import asyncio
import threading
from datetime import datetime
from agents.login_agent import LoginAgent
from agents.order_agent import OrderAgent
from agents.return_agent import ReturnAgent
from agents.reminder_agent import ReminderAgent
from utils.database import init_database, get_database_info
from config import Config

app = Flask(__name__)

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
        # Initialize database
        init_database()
        
        # Get database info
        db_info = get_database_info()
        
        # Get orders count
        reminder_agent = ReminderAgent()
        orders = reminder_agent.get_all_orders()
        
        status = {
            'status': 'running',
            'timestamp': datetime.now().isoformat(),
            'database': {
                'initialized': True,
                'orders_count': len(orders) if orders else 0,
                'tables': db_info.get('tables', [])
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
        init_database()
        reminder_agent = ReminderAgent()
        orders = reminder_agent.get_all_orders()
        
        return jsonify({
            'orders': orders or [],
            'count': len(orders) if orders else 0
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/reminders')
def api_reminders():
    """API endpoint to check reminders"""
    try:
        init_database()
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
            'features': {
                'database_path': config.DATABASE_PATH,
                'return_period_days': config.DEFAULT_RETURN_PERIOD_DAYS,
                'urgent_threshold_days': config.URGENT_DEADLINE_THRESHOLD_DAYS
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/automation/start', methods=['POST'])
def start_automation():
    """Start the automation process"""
    global automation_status
    
    try:
        data = request.get_json()
        phone_number = data.get('phone_number')
        command = data.get('command', '')
        headless = data.get('headless', False)
        
        if not phone_number:
            return jsonify({'error': 'Phone number is required'}), 400
        
        if automation_status['running']:
            return jsonify({'error': 'Automation is already running'}), 400
        
        # Start automation in background thread
        automation_status['running'] = True
        automation_status['status'] = 'starting'
        automation_status['message'] = 'Initializing automation...'
        automation_status['error'] = None
        
        thread = threading.Thread(
            target=run_automation, 
            args=(phone_number, command, headless)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Automation started'
        })
        
    except Exception as e:
        automation_status['running'] = False
        automation_status['error'] = str(e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/automation/status')
def automation_status_api():
    """Get current automation status"""
    return jsonify(automation_status)

@app.route('/api/automation/stop', methods=['POST'])
def stop_automation():
    """Stop the automation process"""
    global automation_status
    
    automation_status['running'] = False
    automation_status['status'] = 'stopped'
    automation_status['message'] = 'Automation stopped by user'
    
    return jsonify({
        'success': True,
        'message': 'Automation stopped'
    })

def run_automation(phone_number, command, headless):
    """Run the automation workflow in background"""
    global automation_status
    
    try:
        # Initialize database
        automation_status['status'] = 'initializing'
        automation_status['message'] = 'Setting up database...'
        init_database()
        
        # Initialize agents
        automation_status['message'] = 'Starting browser...'
        login_agent = LoginAgent(headless=headless)
        order_agent = OrderAgent()
        return_agent = ReturnAgent()
        reminder_agent = ReminderAgent()
        
        # Run the automation workflow
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def automation_workflow():
            try:
                # Step 1: Start browser
                automation_status['status'] = 'browser_starting'
                automation_status['message'] = 'Opening browser...'
                await login_agent.start_browser()
                
                # Step 2: Login
                automation_status['status'] = 'logging_in'
                automation_status['message'] = 'Navigating to Ajio.com and logging in...'
                success = await login_agent.login(phone_number)
                
                if not success:
                    automation_status['error'] = 'Login failed'
                    return
                
                # Step 3: Scrape orders
                automation_status['status'] = 'scraping_orders'
                automation_status['message'] = 'Extracting order information...'
                orders = await order_agent.scrape_orders(login_agent.page)
                
                automation_status['orders'] = orders or []
                
                if orders:
                    # Save orders to database
                    automation_status['message'] = f'Saving {len(orders)} orders to database...'
                    for order in orders:
                        reminder_agent.save_order(order)
                
                # Step 4: Handle command if provided
                if command and command.strip():
                    automation_status['status'] = 'processing_command'
                    automation_status['message'] = f'Processing command: {command}'
                    await return_agent.process_command(login_agent.page, command)
                
                # Step 5: Complete
                automation_status['status'] = 'completed'
                automation_status['message'] = f'Automation completed successfully! Found {len(orders or [])} orders.'
                
            except Exception as e:
                automation_status['error'] = str(e)
                automation_status['status'] = 'error'
                automation_status['message'] = f'Error: {str(e)}'
            
            finally:
                await login_agent.close_browser()
                automation_status['running'] = False
        
        loop.run_until_complete(automation_workflow())
        
    except Exception as e:
        automation_status['running'] = False
        automation_status['error'] = str(e)
        automation_status['status'] = 'error'
        automation_status['message'] = f'Failed to run automation: {str(e)}'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)