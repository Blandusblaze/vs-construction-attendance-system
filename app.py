from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import sqlite3
import base64
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database setup
def get_db():
    conn = sqlite3.connect('attendance.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            check_in_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            check_out_time TIMESTAMP,
            front_image_path TEXT,
            rear_image_path TEXT,
            latitude REAL,
            longitude REAL,
            city TEXT,
            full_address TEXT,
            status TEXT DEFAULT 'checked_in',
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create default admin if not exists
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        admin_hash = generate_password_hash('admin123')
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
            ('admin', 'admin@attendance.com', admin_hash, 'admin')
        )
        conn.commit()
    conn.close()

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, email, role):
        self.id = id
        self.username = username
        self.email = email
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if user:
        return User(user['id'], user['username'], user['email'], user['role'])
    return None

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('user_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            user_obj = User(user['id'], user['username'], user['email'], user['role'])
            login_user(user_obj)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    conn = get_db()
    users = conn.execute('SELECT id, username, email, role, created_at FROM users').fetchall()
    attendance = conn.execute('''
        SELECT a.*, u.username 
        FROM attendance a 
        JOIN users u ON a.user_id = u.id 
        ORDER BY a.check_in_time DESC 
        LIMIT 50
    ''').fetchall()
    conn.close()
    return render_template('admin_dashboard.html', users=users, attendance=attendance)

@app.route('/admin/add_user', methods=['POST'])
@login_required
@admin_required
def add_user():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role', 'user')
    
    if not username or not email or not password:
        flash('All fields are required', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    conn = get_db()
    try:
        password_hash = generate_password_hash(password)
        conn.execute(
            'INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)',
            (username, email, password_hash, role)
        )
        conn.commit()
        flash(f'User {username} added successfully', 'success')
    except sqlite3.IntegrityError:
        flash('Username or email already exists', 'danger')
    finally:
        conn.close()
    
    return redirect(url_for('admin_dashboard'))

@app.route('/user/dashboard')
@login_required
def user_dashboard():
    conn = get_db()
    attendance = conn.execute(
        'SELECT * FROM attendance WHERE user_id = ? ORDER BY check_in_time DESC LIMIT 10',
        (current_user.id,)
    ).fetchall()
    
    # Check if user is currently checked in
    current_checkin = conn.execute(
        'SELECT * FROM attendance WHERE user_id = ? AND status = "checked_in" ORDER BY check_in_time DESC LIMIT 1',
        (current_user.id,)
    ).fetchone()
    conn.close()
    
    return render_template('user_dashboard.html', attendance=attendance, current_checkin=current_checkin)

@app.route('/user/checkin')
@login_required
def checkin_page():
    # Check if already checked in
    conn = get_db()
    current_checkin = conn.execute(
        'SELECT * FROM attendance WHERE user_id = ? AND status = "checked_in"',
        (current_user.id,)
    ).fetchone()
    conn.close()
    
    if current_checkin:
        flash('You are already checked in. Please check out first.', 'warning')
        return redirect(url_for('user_dashboard'))
    
    return render_template('checkin.html')

@app.route('/api/checkin', methods=['POST'])
@login_required
def api_checkin():
    data = request.json
    
    # Save images
    front_image = data.get('front_image')
    rear_image = data.get('rear_image')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    city = data.get('city', 'Unknown')
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    front_filename = f"front_{current_user.id}_{timestamp}.jpg"
    rear_filename = f"rear_{current_user.id}_{timestamp}.jpg"
    
    # Save front image
    if front_image:
        front_image_data = front_image.split(',')[1]
        front_path = os.path.join(app.config['UPLOAD_FOLDER'], front_filename)
        with open(front_path, 'wb') as f:
            f.write(base64.b64decode(front_image_data))
    
    # Save rear image
    if rear_image:
        rear_image_data = rear_image.split(',')[1]
        rear_path = os.path.join(app.config['UPLOAD_FOLDER'], rear_filename)
        with open(rear_path, 'wb') as f:
            f.write(base64.b64decode(rear_image_data))
    
    # Save to database
    conn = get_db()
    conn.execute('''
        INSERT INTO attendance (user_id, front_image_path, rear_image_path, latitude, longitude, city)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (current_user.id, front_filename, rear_filename, latitude, longitude, city))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Check-in successful!'})

@app.route('/api/checkout', methods=['POST'])
@login_required
def api_checkout():
    conn = get_db()
    conn.execute('''
        UPDATE attendance 
        SET check_out_time = CURRENT_TIMESTAMP, status = 'checked_out'
        WHERE user_id = ? AND status = 'checked_in'
    ''', (current_user.id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Check-out successful!'})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)