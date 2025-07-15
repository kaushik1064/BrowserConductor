"""
Database utilities for SQLite operations.
Handles database initialization, connections, and migrations.
"""

import sqlite3
import os
from contextlib import contextmanager
from typing import Optional
import typer

DATABASE_PATH = "orders.db"

def init_database():
    """Initialize the SQLite database with required tables"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Create orders table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id TEXT UNIQUE NOT NULL,
                    product_name TEXT NOT NULL,
                    price TEXT,
                    image_url TEXT,
                    delivery_status TEXT,
                    has_return_option INTEGER DEFAULT 0,
                    has_replace_option INTEGER DEFAULT 0,
                    return_deadline TEXT,
                    scraped_at TEXT,
                    updated_at TEXT
                )
            """)
            
            # Create sessions table for storing login sessions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone_number TEXT,
                    session_data TEXT,
                    created_at TEXT,
                    expires_at TEXT,
                    is_active INTEGER DEFAULT 1
                )
            """)
            
            # Create reminders table for tracking notifications
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id TEXT NOT NULL,
                    reminder_type TEXT NOT NULL,
                    reminder_date TEXT NOT NULL,
                    is_sent INTEGER DEFAULT 0,
                    created_at TEXT,
                    FOREIGN KEY (order_id) REFERENCES orders (order_id)
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_order_id ON orders(order_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_deadline ON orders(return_deadline)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_reminders_date ON reminders(reminder_date)")
            
            conn.commit()
            typer.echo("✅ Database initialized successfully")
            
    except Exception as e:
        typer.echo(f"❌ Error initializing database: {str(e)}")
        raise

@contextmanager
def get_db_connection():
    """Get database connection with automatic cleanup"""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        yield conn
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

def execute_query(query: str, params: tuple = (), fetch: bool = False):
    """Execute a database query with parameters"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            if fetch:
                return cursor.fetchall()
            else:
                conn.commit()
                return cursor.rowcount
                
    except Exception as e:
        typer.echo(f"❌ Database query error: {str(e)}")
        return None

def backup_database(backup_path: Optional[str] = None):
    """Create a backup of the database"""
    if not backup_path:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"orders_backup_{timestamp}.db"
    
    try:
        import shutil
        shutil.copy2(DATABASE_PATH, backup_path)
        typer.echo(f"✅ Database backed up to: {backup_path}")
        return backup_path
    except Exception as e:
        typer.echo(f"❌ Error creating backup: {str(e)}")
        return None

def restore_database(backup_path: str):
    """Restore database from backup"""
    try:
        import shutil
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, DATABASE_PATH)
            typer.echo(f"✅ Database restored from: {backup_path}")
            return True
        else:
            typer.echo(f"❌ Backup file not found: {backup_path}")
            return False
    except Exception as e:
        typer.echo(f"❌ Error restoring database: {str(e)}")
        return False

def get_database_info():
    """Get database information and statistics"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get table information
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            info = {
                'database_path': DATABASE_PATH,
                'database_size': os.path.getsize(DATABASE_PATH) if os.path.exists(DATABASE_PATH) else 0,
                'tables': tables
            }
            
            # Get row counts for each table
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                info[f'{table}_count'] = cursor.fetchone()[0]
            
            return info
            
    except Exception as e:
        typer.echo(f"❌ Error getting database info: {str(e)}")
        return {}

def vacuum_database():
    """Optimize database by running VACUUM"""
    try:
        with get_db_connection() as conn:
            conn.execute("VACUUM")
            typer.echo("✅ Database optimized")
            return True
    except Exception as e:
        typer.echo(f"❌ Error optimizing database: {str(e)}")
        return False

def migrate_database():
    """Handle database migrations for schema updates"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check current schema version
            try:
                cursor.execute("SELECT value FROM metadata WHERE key = 'schema_version'")
                version = cursor.fetchone()
                current_version = int(version[0]) if version else 0
            except:
                # Create metadata table if it doesn't exist
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS metadata (
                        key TEXT PRIMARY KEY,
                        value TEXT
                    )
                """)
                cursor.execute("INSERT OR REPLACE INTO metadata (key, value) VALUES ('schema_version', '1')")
                current_version = 1
            
            # Apply migrations based on current version
            if current_version < 2:
                # Example migration - add new column
                try:
                    cursor.execute("ALTER TABLE orders ADD COLUMN tags TEXT")
                    cursor.execute("UPDATE metadata SET value = '2' WHERE key = 'schema_version'")
                    typer.echo("✅ Applied migration: Added tags column")
                except:
                    pass  # Column might already exist
            
            conn.commit()
            typer.echo("✅ Database migrations completed")
            
    except Exception as e:
        typer.echo(f"❌ Error applying migrations: {str(e)}")
