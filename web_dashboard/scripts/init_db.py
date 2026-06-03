# scripts/init_db.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.application_tracker import ApplicationTracker
import sqlite3

def init_database():
    """Initialize the application database"""
    print("🗄️  Initializing database...")
    
    # Create data directory
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    db_path = os.path.join(data_dir, 'applications.db')
    
    # Initialize tracker (creates tables)
    tracker = ApplicationTracker(db_path)
    
    # Create additional tables if needed
    conn = tracker.conn
    
    # Create scheduled tasks table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS scheduled_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_type TEXT NOT NULL,
            scheduled_time DATETIME NOT NULL,
            application_id INTEGER,
            template_type TEXT,
            status TEXT DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            completed_at DATETIME
        )
    ''')
    
    # Create networking activities table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS networking_activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id INTEGER,
            person_name TEXT,
            person_title TEXT,
            person_type TEXT,
            company TEXT,
            profile_url TEXT,
            action TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print("✅ Database initialized successfully!")
    print(f"📁 Database location: {db_path}")

if __name__ == '__main__':
    init_database()
