#!/usr/bin/env python3
"""
Stealth automation runner for Ajio.com with anti-detection measures
"""

import asyncio
import typer
from agents.stealth_login_agent import StealthLoginAgent
from agents.order_agent import OrderAgent
from agents.return_agent import ReturnAgent
from agents.reminder_agent import ReminderAgent
from utils.database import init_database

async def stealth_automation(
    phone_number: str,
    headless: bool = False,
    command: str = None
):
    """Run automation with stealth measures"""
    
    print("🚀 Starting stealth automation for Ajio.com...")
    print("🔒 Using anti-detection measures...")
    
    # Initialize database
    init_database()
    
    # Use stealth agent instead of regular login agent
    login_agent = StealthLoginAgent(headless=headless)
    order_agent = OrderAgent()
    return_agent = ReturnAgent()
    reminder_agent = ReminderAgent()
    
    try:
        # Start browser with stealth configurations
        await login_agent.start_browser()
        
        # Login with stealth measures
        print("🔐 Attempting stealth login...")
        success = await login_agent.login(phone_number)
        
        if success:
            print("✅ Login successful!")
            
            # Scrape orders
            print("📦 Scraping orders...")
            orders = await order_agent.scrape_orders(login_agent.page)
            
            if orders:
                print(f"✅ Found {len(orders)} orders")
                
                # Save orders to database
                for order in orders:
                    reminder_agent.save_order(order)
                
                # Show order summary
                print("\n📋 Order Summary:")
                for order in orders:
                    status_emoji = "✅" if order.get('delivery_status') == 'Delivered' else "🚚"
                    print(f"{status_emoji} {order.get('product_name')} - {order.get('price')} - {order.get('delivery_status')}")
                    
                    if order.get('return_deadline'):
                        print(f"   ⏰ Return deadline: {order.get('return_deadline')}")
            else:
                print("ℹ️ No orders found")
            
            # Handle return/replace commands
            if command:
                print(f"🔄 Processing command: {command}")
                await return_agent.process_command(login_agent.page, command)
            
            return True
        else:
            print("❌ Login failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    finally:
        await login_agent.close_browser()

def main():
    """Main CLI interface"""
    print("🛡️ Ajio.com Stealth Automation Tool")
    print("=" * 50)
    
    phone = input("📱 Enter your phone number (with country code): ")
    
    print("\n🖥️ Browser Options:")
    print("1. Visible browser (Recommended for first use)")
    print("2. Hidden browser (Headless mode)")
    
    choice = input("Select option (1 or 2): ").strip()
    headless = choice == "2"
    
    if headless:
        print("⚠️ Running in headless mode")
    else:
        print("👀 Running with visible browser")
    
    command = input("\n🔄 Enter return/replace command (optional, press Enter to skip): ").strip()
    if not command:
        command = None
    
    print("\n🚀 Starting automation...")
    try:
        result = asyncio.run(stealth_automation(phone, headless, command))
        
        if result:
            print("\n✅ Automation completed successfully!")
            print("💾 Orders saved to database")
            print("📊 Check reminders with: python run_stealth.py --check-reminders")
        else:
            print("\n❌ Automation failed")
            print("💡 Tips:")
            print("  1. Try running with visible browser first")
            print("  2. Check your internet connection")
            print("  3. Make sure phone number is correct")
            print("  4. Try again after some time")
            
    except KeyboardInterrupt:
        print("\n⏹️ Automation stopped by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")

def check_reminders():
    """Check for return deadline reminders"""
    print("🔔 Checking return deadlines...")
    init_database()
    reminder_agent = ReminderAgent()
    reminders = reminder_agent.check_reminders()
    
    if reminders:
        print(f"⚠️ Found {len(reminders)} urgent reminders!")
        for reminder in reminders:
            print(f"  📦 {reminder['product_name']} - Return by: {reminder['return_deadline']}")
    else:
        print("✅ No urgent return deadlines")

def list_orders():
    """List all saved orders"""
    print("📦 Listing saved orders...")
    init_database()
    reminder_agent = ReminderAgent()
    orders = reminder_agent.get_all_orders()
    
    if orders:
        print(f"📋 Found {len(orders)} orders:")
        for order in orders:
            print(f"  • {order['product_name']} (ID: {order['order_id']})")
            print(f"    Price: {order['price']} | Status: {order['delivery_status']}")
            if order['return_deadline']:
                print(f"    Return deadline: {order['return_deadline']}")
            print()
    else:
        print("📦 No orders found in database")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--check-reminders":
            check_reminders()
        elif sys.argv[1] == "--list-orders":
            list_orders()
        else:
            print("Usage:")
            print("  python run_stealth.py                 # Run automation")
            print("  python run_stealth.py --check-reminders  # Check reminders")
            print("  python run_stealth.py --list-orders      # List orders")
    else:
        main()