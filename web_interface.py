#!/usr/bin/env python3
"""
Simple web interface for Ajio.com automation system demo.
Provides a basic dashboard to showcase the application's capabilities.
"""

from flask import Flask, render_template, jsonify, request
import json
import asyncio
from datetime import datetime
from agents.reminder_agent import ReminderAgent
from utils.database import init_database, get_database_info
from config import Config

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)