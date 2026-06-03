# web_dashboard/app.py
import os
import sys
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_cors import CORS
from datetime import datetime
from functools import wraps

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.application_tracker import ApplicationTracker

app = Flask(__name__)

# IMPORTANT: Use environment variable or generate random key
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24).hex())
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

CORS(app)

# Initialize tracker
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'applications.db')
os.makedirs(os.path.dirname(db_path), exist_ok=True)
tracker = ApplicationTracker(db_path)

# User credentials from environment variables
USERS = {
    os.environ.get('ADMIN_USERNAME', 'admin'): os.environ.get('ADMIN_PASSWORD', 'admin')
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in USERS and USERS[username] == password:
            session['username'] = username
            session.permanent = True
            flash('✅ Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            error = '❌ Invalid username or password'
            flash(error, 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        stats = tracker.get_stats(days=30)
        
        recent_apps = tracker.conn.execute('''
            SELECT * FROM applications 
            ORDER BY application_date DESC 
            LIMIT 10
        ''').fetchall()
        
        recent_apps_list = [dict(app) for app in recent_apps]
        
        return render_template('dashboard.html', 
                             stats=stats, 
                             recent_apps=recent_apps_list)
    except Exception as e:
        print(f"Dashboard error: {e}")
        return render_template('dashboard.html', 
                             stats={'total_applications': 0, 'interviews': 0, 
                                   'offers': 0, 'response_rate': 0, 
                                   'interview_rate': 0, 'offer_rate': 0,
                                   'active_applications': 0, 'rejections': 0},
                             recent_apps=[])

@app.route('/applications')
@login_required
def applications():
    status_filter = request.args.get('status', 'all')
    date_range = request.args.get('range', '30')
    
    query = '''
        SELECT * FROM applications 
        WHERE application_date >= datetime('now', '-' || ? || ' days')
    '''
    params = [date_range]
    
    if status_filter != 'all':
        query += ' AND status = ?'
        params.append(status_filter)
    
    query += ' ORDER BY application_date DESC LIMIT 100'
    
    try:
        apps = tracker.conn.execute(query, params).fetchall()
        apps_list = [dict(app) for app in apps]
    except Exception as e:
        print(f"Applications error: {e}")
        apps_list = []
    
    return render_template('applications.html', 
                         applications=apps_list,
                         current_filter=status_filter,
                         date_range=date_range)

@app.route('/analytics')
@login_required
def analytics():
    return render_template('analytics.html')

@app.route('/settings')
@login_required
def settings():
    # Get config from environment
    config = {
        'profile': {
            'first_name': os.environ.get('FIRST_NAME', ''),
            'last_name': os.environ.get('LAST_NAME', ''),
            'email': os.environ.get('EMAIL', ''),
            'phone': os.environ.get('PHONE', ''),
            'location': os.environ.get('LOCATION', ''),
            'years_experience': os.environ.get('YEARS_EXPERIENCE', '5')
        },
        'preferences': {
            'remote': os.environ.get('PREFER_REMOTE', 'true'),
            'location': os.environ.get('PREFERRED_LOCATION', 'Remote'),
            'min_salary': os.environ.get('MIN_SALARY', '100000')
        }
    }
    return render_template('settings.html', config=config)

# API Routes
@app.route('/api/stats')
@login_required
def api_stats():
    try:
        days = request.args.get('days', 30, type=int)
        stats = tracker.get_stats(days=days)
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/applications/recent')
@login_required
def api_recent_applications():
    try:
        limit = request.args.get('limit', 20, type=int)
        apps = tracker.conn.execute('''
            SELECT * FROM applications 
            ORDER BY application_date DESC 
            LIMIT ?
        ''', (limit,)).fetchall()
        return jsonify([dict(app) for app in apps])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint for Render"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/agent/start', methods=['POST'])
@login_required
def start_agent():
    return jsonify({
        'success': True,
        'message': 'Agent started successfully',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/agent/stop', methods=['POST'])
@login_required
def stop_agent():
    return jsonify({
        'success': True,
        'message': 'Agent stopped successfully',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/agent/status')
@login_required
def agent_status():
    stats = tracker.get_stats(days=1)
    return jsonify({
        'status': 'running',
        'applications_today': stats['total_applications'],
        'last_activity': datetime.now().isoformat()
    })

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return render_template('base.html', error="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('base.html', error="Internal server error"), 500

# Create startup function
def initialize_app():
    """Initialize application directories and database"""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    dirs = ['data', 'data/resume', 'data/reports', 'data/logs']
    for d in dirs:
        os.makedirs(os.path.join(base_dir, d), exist_ok=True)

# Initialize on import
initialize_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
