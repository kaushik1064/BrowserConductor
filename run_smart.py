#!/usr/bin/env python3
"""
Smart automation runner with AI vision for Ajio.com
Uses Groq LLM to intelligently identify login elements
"""

import asyncio
import typer
from agents.smart_login_agent import SmartLoginAgent
from agents.order_agent import OrderAgent
from agents.return_agent import ReturnAgent
from agents.reminder_agent import ReminderAgent
from utils.database import init_database

async def smart_automation(
    phone_number: str,
    headless: bool = False,
    command: str = None
):
    """Run automation with AI-powered element detection"""
    
    print("🤖 Starting AI-powered automation for Ajio.com...")
    print("🧠 Using Groq LLM for intelligent element detection...")
    
    # Initialize database
    init_database()
    
    # Use smart agent with AI vision
    login_agent = SmartLoginAgent(headless=headless)
    order_agent = OrderAgent()
    return_agent = ReturnAgent()
    reminder_agent = ReminderAgent()
    
    try:
        # Start browser with stealth + AI capabilities
        await login_agent.start_browser()
        
        # Login with AI assistance
        print("🔐 Attempting smart login with AI vision...")
        success = await login_agent.login(phone_number)
        
        if success:
            print("✅ AI-powered login successful!")
            
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
            print("❌ AI-powered login failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    finally:
        await login_agent.close_browser()

def main():
    """Main CLI interface for smart automation"""
    print("🤖 Ajio.com Smart Automation with AI Vision")
    print("=" * 60)
    print("🧠 Powered by Groq LLM for intelligent element detection")
    print()
    
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
    
    print("\n🚀 Starting AI-powered automation...")
    print("🤖 The AI will:")
    print("  • Analyze the page content intelligently")
    print("  • Find login elements using natural language understanding")
    print("  • Adapt to different layouts and website changes")
    print("  • Provide detailed reasoning for its decisions")
    print()
    
    try:
        result = asyncio.run(smart_automation(phone, headless, command))
        
        if result:
            print("\n✅ AI-powered automation completed successfully!")
            print("🧠 The AI successfully identified and interacted with page elements")
            print("💾 Orders saved to database")
            print("📊 Check reminders with: python run_smart.py --check-reminders")
        else:
            print("\n❌ AI-powered automation failed")
            print("💡 AI Analysis Tips:")
            print("  1. Make sure the page loads completely")
            print("  2. Check if Groq API key is set correctly")
            print("  3. Try with visible browser to see AI decision making")
            print("  4. The AI learns from the page structure - it may work better on second try")
            
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
        elif sys.argv[1] == "--help":
            print("🤖 Smart Automation Commands:")
            print("  python run_smart.py                    # Run AI-powered automation")
            print("  python run_smart.py --check-reminders  # Check return deadlines")
            print("  python run_smart.py --list-orders      # List saved orders")
            print("  python run_smart.py --help             # Show this help")
        else:
            print("❌ Unknown command. Use --help for available options.")
    else:
        main()