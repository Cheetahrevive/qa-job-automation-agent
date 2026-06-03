# web_dashboard/app.py
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_cors import CORS
from datetime import datetime, timedelta
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.application_tracker import ApplicationTracker

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
CORS(app)

# Initialize tracker with path relative to web_dashboard folder
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'applications.db')
tracker = ApplicationTracker(db_path)

# Simple user store (use environment variables in production)
USERS = {
    os.getenv('ADMIN_USERNAME', 'admin'): os.getenv('ADMIN_PASSWORD', 'password')
}

# Decorator for protected routes
def login_required(f):
    from functools import wraps
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
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in USERS and USERS[username] == password:
            session['username'] = username
            session.permanent = True
            flash('✅ Login successful! Welcome back.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('❌ Invalid credentials. Please try again.', 'danger')
    
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
                             recent_apps=recent_apps_list,
                             username=session.get('username'))
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'danger')
        return render_template('dashboard.html', 
                             stats={'total_applications': 0, 'interviews': 0, 
                                   'offers': 0, 'response_rate': 0},
                             recent_apps=[],
                             username=session.get('username'))

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
        apps_list = []
        flash(f'Error loading applications: {str(e)}', 'danger')
    
    return render_template('applications.html', 
                         applications=apps_list,
                         current_filter=status_filter,
                         date_range=date_range)

@app.route('/analytics')
@login_required
def analytics():
    try:
        daily_stats = tracker.conn.execute('''
            SELECT 
                date(application_date) as date,
                COUNT(*) as count,
                AVG(match_score) as avg_score
            FROM applications
            WHERE application_date >= datetime('now', '-30 days')
            GROUP BY date(application_date)
            ORDER BY date
        ''').fetchall()
        
        platform_stats = tracker.conn.execute('''
            SELECT 
                COALESCE(platform, 'Unknown') as platform,
                COUNT(*) as count,
                ROUND(AVG(match_score) * 100, 1) as avg_score
            FROM applications
            WHERE application_date >= datetime('now', '-30 days')
            GROUP BY platform
            ORDER BY count DESC
        ''').fetchall()
        
        return render_template('analytics.html',
                             daily_stats=[dict(s) for s in daily_stats],
                             platform_stats=[dict(p) for p in platform_stats])
    except Exception as e:
        flash(f'Error loading analytics: {str(e)}', 'danger')
        return render_template('analytics.html', daily_stats=[], platform_stats=[])

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

# API Routes
@app.route('/api/stats')
@login_required
def api_stats():
    try:
        stats = tracker.get_stats(days=request.args.get('days', 30, type=int))
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

@app.route('/api/applications/<int:app_id>/status', methods=['PUT'])
@login_required
def update_application_status(app_id):
    try:
        data = request.json
        new_status = data.get('status')
        notes = data.get('notes', '')
        
        tracker.update_status(str(app_id), new_status, notes)
        return jsonify({'success': True, 'message': 'Status updated'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/agent/start', methods=['POST'])
@login_required
def api_start_agent():
    # Placeholder for agent start logic
    return jsonify({
        'success': True,
        'message': 'Agent started successfully',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/agent/stop', methods=['POST'])
@login_required
def api_stop_agent():
    # Placeholder for agent stop logic
    return jsonify({
        'success': True,
        'message': 'Agent stopped successfully',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/agent/status')
@login_required
def api_agent_status():
    stats = tracker.get_stats(days=1)
    return jsonify({
        'status': 'idle',
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

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'resume'), exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'reports'), exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'logs'), exist_ok=True)
    
    # Run the app
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
