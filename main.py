#!/usr/bin/env python3
"""
Main orchestrator for Ajio.com multi-agent browser automation system.
Handles login, order scraping, return management, and reminder functionality.
"""

import asyncio
import typer
from typing import Optional
from pathlib import Path

from agents.login_agent import LoginAgent
from agents.order_agent import OrderAgent
from agents.return_agent import ReturnAgent
from agents.reminder_agent import ReminderAgent
from utils.database import init_database
from config import Config

app = typer.Typer(help="Ajio.com Multi-Agent Browser Automation System")

async def main_workflow(
    headless: bool = True,
    phone_number: Optional[str] = None,
    command: Optional[str] = None
):
    """Main workflow orchestrating all agents"""
    
    # Initialize database
    init_database()
    
    # Initialize agents
    login_agent = LoginAgent(headless=headless)
    order_agent = OrderAgent()
    return_agent = ReturnAgent()
    reminder_agent = ReminderAgent()
    
    try:
        # Step 1: Check for pending reminders
        typer.echo("🔔 Checking for return deadline reminders...")
        reminder_agent.check_reminders()
        
        # Step 2: Login to Ajio
        typer.echo("🚀 Starting Ajio.com automation...")
        await login_agent.start_browser()
        
        success = await login_agent.login(phone_number)
        if not success:
            typer.echo("❌ Login failed. Exiting.")
            return
        
        # Step 3: Scrape orders
        typer.echo("📦 Scraping order information...")
        orders = await order_agent.scrape_orders(login_agent.page)
        
        if orders:
            typer.echo(f"✅ Found {len(orders)} orders")
            
            # Save orders to database
            for order in orders:
                reminder_agent.save_order(order)
        
        # Step 4: Handle return/replace commands
        if command:
            typer.echo(f"🔄 Processing command: {command}")
            await return_agent.process_command(login_agent.page, command)
        
        # Step 5: Show order summary
        typer.echo("\n📋 Order Summary:")
        for order in orders:
            status_emoji = "✅" if order.get('delivery_status') == 'Delivered' else "🚚"
            typer.echo(f"{status_emoji} {order.get('product_name')} - {order.get('price')} - {order.get('delivery_status')}")
            
            if order.get('return_deadline'):
                typer.echo(f"   ⏰ Return deadline: {order.get('return_deadline')}")
    
    except Exception as e:
        typer.echo(f"❌ Error: {str(e)}")
    
    finally:
        await login_agent.close_browser()

@app.command()
def login_and_scrape(
    phone_number: Optional[str] = typer.Option(None, "--phone", "-p", help="Phone number for login"),
    headless: bool = typer.Option(True, "--headless/--headed", help="Run browser in headless mode"),
    command: Optional[str] = typer.Option(None, "--command", "-c", help="Natural language command for returns/replacements")
):
    """Login to Ajio and scrape order information"""
    asyncio.run(main_workflow(headless, phone_number, command))

@app.command()
def check_reminders():
    """Check for return deadline reminders"""
    init_database()
    reminder_agent = ReminderAgent()
    reminder_agent.check_reminders()

@app.command()
def list_orders():
    """List all saved orders from database"""
    init_database()
    reminder_agent = ReminderAgent()
    orders = reminder_agent.get_all_orders()
    
    if not orders:
        typer.echo("📦 No orders found in database.")
        return
    
    typer.echo(f"📦 Found {len(orders)} saved orders:")
    for order in orders:
        typer.echo(f"  • {order['product_name']} (Order ID: {order['order_id']})")
        typer.echo(f"    Price: {order['price']} | Status: {order['delivery_status']}")
        if order['return_deadline']:
            typer.echo(f"    Return deadline: {order['return_deadline']}")
        typer.echo()

if __name__ == "__main__":
    app()
