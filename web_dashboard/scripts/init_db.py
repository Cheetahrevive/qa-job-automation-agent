import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.application_tracker import ApplicationTracker

def init_database():
    """Initialize the application database"""
    print("Initializing database...")
    
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    db_path = os.path.join(data_dir, 'applications.db')
    tracker = ApplicationTracker(db_path)
    
    print(f"Database initialized at: {db_path}")
    tracker.close()

if __name__ == '__main__':
    init_database()
    print("Database setup complete!")
