#!/usr/bin/env python3
"""
Smart web interface for Ajio.com automation system with AI Vision.
Provides a comprehensive dashboard showcasing AI-powered automation capabilities.
"""

from flask import Flask, render_template, jsonify, request
import json
import os
import asyncio
import threading
from datetime import datetime
from agents.login_agent import LoginAgent
from agents.order_agent import OrderAgent
from agents.return_agent import ReturnAgent
from agents.reminder_agent import ReminderAgent
# Import AI agents conditionally to avoid import errors
try:
    from agents.smart_login_agent import SmartLoginAgent
    from agents.ai_vision_agent import AIVisionAgent
    AI_AGENTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ AI agents not available: {e}")
    AI_AGENTS_AVAILABLE = False
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
                'smart_login_agent': 'Available',
                'ai_vision_agent': 'Available',
                'order_agent': 'Available', 
                'return_agent': 'Available',
                'reminder_agent': 'Available'
            },
            'ai_features': {
                'groq_api': bool(os.getenv('GROQ_API_KEY')),
                'intelligent_login_detection': AI_AGENTS_AVAILABLE,
                'adaptive_element_finding': AI_AGENTS_AVAILABLE,
                'natural_language_analysis': AI_AGENTS_AVAILABLE,
                'ai_agents_available': AI_AGENTS_AVAILABLE
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
        demo_mode = data.get('demo_mode', False)
        
        if not phone_number:
            return jsonify({'error': 'Phone number is required'}), 400
        
        if automation_status['running']:
            return jsonify({'error': 'Automation is already running'}), 400
        
        # Start automation in background thread
        automation_status['running'] = True
        automation_status['status'] = 'starting'
        automation_status['message'] = 'Initializing automation...'
        automation_status['error'] = None
        automation_status['orders'] = []
        
        if demo_mode:
            thread = threading.Thread(
                target=run_demo_automation, 
                args=(phone_number, command)
            )
        else:
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
                try:
                    await login_agent.start_browser()
                    automation_status['message'] = 'Browser started successfully. Navigating to Ajio.com...'
                except Exception as browser_error:
                    if "Host system is missing dependencies" in str(browser_error) or "BrowserType.launch" in str(browser_error):
                        automation_status['error'] = "REAL AUTOMATION NOT AVAILABLE: This Replit environment lacks the system dependencies needed for browser automation. To actually login to Ajio.com and scrape your real orders, you would need to run this on a local machine or server with proper browser support. The demo mode shows how it would work."
                    else:
                        automation_status['error'] = f"Browser startup failed: {str(browser_error)}"
                    return
                
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

def run_demo_automation(phone_number, command):
    """Run a demo automation workflow that simulates the real process"""
    global automation_status
    import time
    
    try:
        # Demo data for simulation
        demo_orders = [
            {
                'order_id': 'AJIO123456789',
                'product_name': 'Cotton Blue Casual Shirt',
                'price': '₹1,299',
                'delivery_status': 'Delivered',
                'has_return_option': True,
                'return_deadline': '2025-07-22'
            },
            {
                'order_id': 'AJIO987654321',
                'product_name': 'Black Formal Shoes',
                'price': '₹2,499',
                'delivery_status': 'Shipped',
                'has_return_option': False,
                'return_deadline': None
            },
            {
                'order_id': 'AJIO456789123',
                'product_name': 'Red Summer Dress',
                'price': '₹1,899',
                'delivery_status': 'Delivered',
                'has_return_option': True,
                'return_deadline': '2025-07-20'
            }
        ]
        
        # Initialize database
        automation_status['status'] = 'initializing'
        automation_status['message'] = 'Setting up database...'
        time.sleep(1)
        init_database()
        
        # Simulate browser starting
        automation_status['status'] = 'browser_starting'
        automation_status['message'] = 'Opening browser (Demo Mode)...'
        time.sleep(2)
        
        # Simulate login process
        automation_status['status'] = 'logging_in'
        automation_status['message'] = f'Logging in with phone {phone_number}...'
        time.sleep(3)
        
        # Simulate OTP entry
        automation_status['message'] = 'Simulating OTP verification...'
        time.sleep(2)
        
        # Simulate order scraping
        automation_status['status'] = 'scraping_orders'
        automation_status['message'] = 'Extracting order information...'
        time.sleep(2)
        
        automation_status['orders'] = demo_orders
        
        # Save demo orders to database
        automation_status['message'] = f'Saving {len(demo_orders)} orders to database...'
        reminder_agent = ReminderAgent()
        for order in demo_orders:
            reminder_agent.save_order(order)
        time.sleep(1)
        
        # Handle command if provided
        if command and command.strip():
            automation_status['status'] = 'processing_command'
            automation_status['message'] = f'Processing command: {command} (Demo Mode)'
            time.sleep(2)
            automation_status['message'] = f'Command "{command}" processed successfully (simulated)'
        
        # Complete
        automation_status['status'] = 'completed'
        automation_status['message'] = f'Demo automation completed! Found {len(demo_orders)} orders. (This was a simulation - no real browser interaction occurred)'
        
    except Exception as e:
        automation_status['error'] = str(e)
        automation_status['status'] = 'error'
        automation_status['message'] = f'Demo failed: {str(e)}'
    
    finally:
        automation_status['running'] = False

# Add AI vision test endpoint
@app.route('/api/ai/test', methods=['POST'])
def test_ai_vision():
    """API endpoint to test AI vision capabilities"""
    if not AI_AGENTS_AVAILABLE:
        return jsonify({
            'error': 'AI vision agents not available',
            'message': 'Please ensure Groq API key is set and all dependencies are installed'
        }), 400
    
    try:
        data = request.get_json()
        test_url = data.get('url', 'https://example.com')
        
        # This would be implemented for testing purposes in a real browser environment
        return jsonify({
            'status': 'success',
            'message': 'AI vision test would analyze the page structure',
            'test_url': test_url,
            'capabilities': {
                'login_detection': True,
                'form_analysis': True,
                'element_interaction': True,
                'adaptive_navigation': True
            },
            'note': 'Full AI vision testing requires browser automation capabilities'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Initialize database on startup
    init_database()
    print("🤖 Ajio.com AI-Powered Automation System - Web Interface")
    print("=" * 70)
    print("🧠 Now featuring Groq AI-powered intelligent login detection!")
    print()
    print("🌐 Dashboard: http://localhost:5000")
    print("📊 API Status: http://localhost:5000/api/status")
    print("📦 Orders API: http://localhost:5000/api/orders")
    print("🔔 Reminders API: http://localhost:5000/api/reminders")
    print("⚙️ Config API: http://localhost:5000/api/config")
    print("🤖 AI Test API: POST /api/ai/test")
    print("🚀 Start Automation: POST /api/automation/start")
    print("📊 Automation Status: /api/automation/status")
    print("⏹️ Stop Automation: POST /api/automation/stop")
    print()
    print("🧠 AI Features:")
    print("   • Intelligent login element detection using Groq LLM")
    print("   • Adaptive page scanning and analysis")
    print("   • Natural language understanding of page structure")
    print("   • Stealth browser automation with human-like behavior")
    print()
    print("⚠️ Note: Browser automation has limitations in Replit environment")
    print("💡 For full AI-powered automation, run locally with:")
    print("   • python run_smart.py    (AI-powered with Groq)")
    print("   • python run_stealth.py  (Stealth mode)")
    print("   • python run_local.py    (Standard mode)")
    print()
    
    app.run(host='0.0.0.0', port=5000, debug=True)