from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import datetime
import pathlib
import os
import re
import secrets

# ── Load Environment Variables ──
env_path = pathlib.Path(__file__).parent / '.env'
print(f"Loading .env from: {env_path}")
print(f"File exists: {env_path.exists()}")
load_dotenv(env_path, override=True)
print(f"ADMIN_PASSWORD loaded: {os.getenv('ADMIN_PASSWORD')}")

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.getenv('SECRET_KEY', 'fallback_secret_key')
app.config['TEMPLATES_AUTO_RELOAD'] = True

# ── Database Setup ──
# ── Database Setup ──
database_url = os.getenv('DATABASE_URL', 'sqlite:///rkstudio.db')
# Fix for Render PostgreSQL URL
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ── Mail Setup ──
app.config['MAIL_SERVER']         = 'smtp.gmail.com'
app.config['MAIL_PORT']           = 587
app.config['MAIL_USE_TLS']        = True
app.config['MAIL_USERNAME']       = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD']       = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = ('R.K. Studio', os.getenv('MAIL_USERNAME'))
mail = Mail(app)

# ── Login Manager ──
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ── Admin Password ──
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')

# ══════════════════════════════════════
# DATABASE MODELS
# ══════════════════════════════════════
class User(UserMixin, db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    email       = db.Column(db.String(100), unique=True, nullable=False)
    phone       = db.Column(db.String(20), nullable=False)
    password    = db.Column(db.String(200), nullable=False)
    verified    = db.Column(db.Boolean, default=True)
    token       = db.Column(db.String(100), nullable=True)
    profile_pic = db.Column(db.String(200), nullable=True, default='default.png')
    created     = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Order(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_email   = db.Column(db.String(100), nullable=False)
    service      = db.Column(db.String(100), nullable=False)
    name         = db.Column(db.String(100), nullable=False)
    phone        = db.Column(db.String(20), nullable=False)
    quantity     = db.Column(db.String(50), nullable=False)
    size         = db.Column(db.String(50), nullable=True)
    design       = db.Column(db.Text, nullable=True)
    address      = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=True)
    status       = db.Column(db.String(50), default='Pending')
    created      = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Booking(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_email   = db.Column(db.String(100), nullable=False)
    name         = db.Column(db.String(100), nullable=False)
    phone        = db.Column(db.String(20), nullable=False)
    package      = db.Column(db.String(100), nullable=True)
    addons       = db.Column(db.Text, nullable=True)
    custom       = db.Column(db.Text, nullable=True)
    event_date   = db.Column(db.String(50), nullable=False)
    event_type   = db.Column(db.String(100), nullable=False)
    venue        = db.Column(db.String(200), nullable=False)
    guests       = db.Column(db.String(50), nullable=True)
    requirements = db.Column(db.Text, nullable=True)
    status       = db.Column(db.String(50), default='Pending')
    created      = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class ContactMessage(db.Model):
    id      = db.Column(db.Integer, primary_key=True)
    name    = db.Column(db.String(100), nullable=False)
    phone   = db.Column(db.String(20), nullable=False)
    email   = db.Column(db.String(100), nullable=False)
    service = db.Column(db.String(100), nullable=True)
    message = db.Column(db.Text, nullable=True)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ══════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════
def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
    return re.match(pattern, email) is not None

def send_verification_email(user):
    token = secrets.token_urlsafe(32)
    user.token = token
    db.session.commit()
    verify_url = url_for('verify_email', token=token, _external=True)
    msg = Message(
        subject='✅ Verify your R.K. Studio Account',
        recipients=[user.email]
    )
    msg.html = f'''
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 40px; background: #f9f6f1;">
        <div style="background: #1a1a2e; padding: 30px; border-radius: 12px; text-align: center;">
            <h1 style="color: #c9a96e; margin: 0;">R.K. Studio</h1>
        </div>
        <div style="background: white; padding: 40px; border-radius: 12px; margin-top: 20px;">
            <h2 style="color: #1a1a2e;">Hello {user.name}! 👋</h2>
            <p style="color: #555; line-height: 1.8;">Thank you for registering with R.K. Studio. Please verify your email by clicking below:</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{verify_url}"
                   style="background: #c9a96e; color: #1a1a2e; padding: 14px 36px; border-radius: 30px; text-decoration: none; font-weight: bold; font-size: 1rem;">
                   ✅ Verify My Email
                </a>
            </div>
            <p style="color: #888; font-size: 0.85rem;">If you did not register, please ignore this email.</p>
        </div>
        <p style="text-align: center; color: #aaa; font-size: 0.8rem; margin-top: 20px;">© 2025 R.K. Studio. All rights reserved.</p>
    </div>
    '''
    mail.send(msg)

# ══════════════════════════════════════
# ROUTES
# ══════════════════════════════════════
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/sitemap.xml')
def sitemap():
    return app.send_static_file('../sitemap.xml')

@app.route('/robots.txt')
def robots():
    return """User-agent: *
Allow: /
Disallow: /admin
Sitemap: https://rkstudio.com/sitemap.xml"""
@app.route('/wedding')
def wedding():
    return render_template('wedding.html')

@app.route('/printing')
def printing():
    return render_template('printing.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/about')
def about():
    return render_template('about.html')

# ── My Orders ──
@app.route('/myorders')
@login_required
def myorders():
    orders   = Order.query.filter_by(user_id=current_user.id).order_by(Order.created.desc()).all()
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.created.desc()).all()
    return render_template('myorders.html', orders=orders, bookings=bookings)

# ── Register ──
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        name     = request.form['name'].strip()
        email    = request.form['email'].strip().lower()
        phone    = request.form['phone'].strip()
        password = request.form['password']
        confirm  = request.form['confirm']

        if not is_valid_email(email):
            return render_template('register.html', error='Please enter a valid email address!')
        if password != confirm:
            return render_template('register.html', error='Passwords do not match!')
        if len(password) < 6:
            return render_template('register.html', error='Password must be at least 6 characters!')

        existing = User.query.filter_by(email=email).first()
        if existing:
            return render_template('register.html', error='Email already registered! Please login.')

        hashed = generate_password_hash(password)
        user   = User(name=name, email=email, phone=phone, password=hashed, verified=True)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect('/')

    return render_template('register.html', error=None)

# ── Verify Email ──
@app.route('/verify/<token>')
def verify_email(token):
    user = User.query.filter_by(token=token).first()
    if not user:
        return render_template('verify.html', status='invalid')
    if user.verified:
        return render_template('verify.html', status='already')
    user.verified = True
    user.token    = None
    db.session.commit()
    login_user(user)
    return render_template('verify.html', status='success', name=user.name)

# ── Login ──
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        email    = request.form['email'].strip().lower()
        password = request.form['password']
        user     = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            return render_template('login.html', error='Wrong email or password!')
        if not user.verified:
            return render_template('login.html', error='Please verify your email first!')

        login_user(user)
        next_page = request.args.get('next')
        return redirect(next_page or '/')

    return render_template('login.html', error=None)

# ── Logout ──
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

# ── Booking ──
@app.route('/booking', methods=['GET', 'POST'])
@login_required
def booking():
    if request.method == 'POST':
        new_booking = Booking(
            user_id      = current_user.id,
            user_email   = current_user.email,
            name         = request.form.get('name', ''),
            phone        = request.form.get('phone', ''),
            package      = request.form.get('package', 'None'),
            addons       = ', '.join(request.form.getlist('addons')) or 'None',
            custom       = ', '.join(request.form.getlist('custom')) or 'None',
            event_date   = request.form.get('event_date', ''),
            event_type   = request.form.get('event_type', ''),
            venue        = request.form.get('venue', ''),
            guests       = request.form.get('guests', 'Not specified'),
            requirements = request.form.get('requirements', ''),
            status       = 'Pending'
        )
        db.session.add(new_booking)
        db.session.commit()
        return render_template('booking.html', success=True)
    return render_template('booking.html', success=False)

# ── Order ──
@app.route('/order', methods=['GET', 'POST'])
@login_required
def order():
    if request.method == 'POST':
        new_order = Order(
            user_id      = current_user.id,
            user_email   = current_user.email,
            service      = request.form['service'],
            name         = request.form['name'],
            phone        = request.form['phone'],
            quantity     = request.form['quantity'],
            size         = request.form['size'],
            design       = request.form['design'],
            address      = request.form['address'],
            instructions = request.form['instructions'],
            status       = 'Pending'
        )
        db.session.add(new_order)
        db.session.commit()
        return render_template('order.html', success=True, service=request.form['service'])

    service = request.args.get('service', 'Printing Service')
    return render_template('order.html', success=False, service=service)

# ── Contact ──
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        msg = ContactMessage(
            name    = request.form['name'],
            phone   = request.form['phone'],
            email   = request.form['email'],
            service = request.form['service'],
            message = request.form['message']
        )
        db.session.add(msg)
        db.session.commit()
        return render_template('contact.html', success=True)
    return render_template('contact.html', success=False)

# ── Update Order Status (Admin) ──
@app.route('/admin/update_order/<int:order_id>', methods=['POST'])
def update_order_status(order_id):
    if not session.get('admin_logged_in'):
        return redirect('/admin')
    order = Order.query.get_or_404(order_id)
    order.status = request.form['status']
    db.session.commit()
    return redirect('/admin')

# ── Update Booking Status (Admin) ──
@app.route('/admin/update_booking/<int:booking_id>', methods=['POST'])
def update_booking_status(booking_id):
    if not session.get('admin_logged_in'):
        return redirect('/admin')
    booking = Booking.query.get_or_404(booking_id)
    booking.status = request.form['status']
    db.session.commit()
    return redirect('/admin')

# ── Cancel Order (User) ──
@app.route('/cancel_order/<int:order_id>', methods=['POST'])
@login_required
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        return redirect('/myorders')
    if order.status == 'Pending':
        order.status = 'Cancelled'
        db.session.commit()
    return redirect('/myorders')

# ── Cancel Booking (User) ──
@app.route('/cancel_booking/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        return redirect('/myorders')
    if booking.status == 'Pending':
        booking.status = 'Cancelled'
        db.session.commit()
    return redirect('/myorders')
# ── Profile ──
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        action = request.form.get('action')

        # ── Update Profile Info ──
        if action == 'update_info':
            name  = request.form.get('name', '').strip()
            phone = request.form.get('phone', '').strip()
            email = request.form.get('email', '').strip().lower()

            if not is_valid_email(email):
                return render_template('profile.html', error='Invalid email address!', success=None)

            existing = User.query.filter_by(email=email).first()
            if existing and existing.id != current_user.id:
                return render_template('profile.html', error='Email already in use!', success=None)

            current_user.name  = name
            current_user.phone = phone
            current_user.email = email
            db.session.commit()
            return render_template('profile.html', error=None, success='Profile updated successfully!')

        # ── Change Password ──
        elif action == 'change_password':
            old_password = request.form.get('old_password')
            new_password = request.form.get('new_password')
            confirm      = request.form.get('confirm_password')

            if not check_password_hash(current_user.password, old_password):
                return render_template('profile.html', error='Current password is incorrect!', success=None)
            if new_password != confirm:
                return render_template('profile.html', error='New passwords do not match!', success=None)
            if len(new_password) < 6:
                return render_template('profile.html', error='Password must be at least 6 characters!', success=None)

            current_user.password = generate_password_hash(new_password)
            db.session.commit()
            return render_template('profile.html', error=None, success='Password changed successfully!')

        # ── Upload Profile Picture ──
        elif action == 'upload_pic':
            if 'profile_pic' not in request.files:
                return render_template('profile.html', error='No file selected!', success=None)

            file = request.files['profile_pic']
            if file.filename == '':
                return render_template('profile.html', error='No file selected!', success=None)

            allowed = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
            ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
            if ext not in allowed:
                return render_template('profile.html', error='Only PNG, JPG, GIF images allowed!', success=None)

            filename = f"profile_{current_user.id}.{ext}"
            filepath = os.path.join(app.static_folder, 'profiles', filename)
            os.makedirs(os.path.join(app.static_folder, 'profiles'), exist_ok=True)
            file.save(filepath)
            current_user.profile_pic = filename
            db.session.commit()
            return render_template('profile.html', error=None, success='Profile picture updated!')

    return render_template('profile.html', error=None, success=None)

# ── Admin ──
@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if request.method == 'POST':
        password = request.form['password']
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect('/admin')
        else:
            return render_template('admin.html', logged_in=False, error=True,
                                   messages=[], orders=[], bookings=[], users=[])
    if session.get('admin_logged_in'):
        messages = ContactMessage.query.order_by(ContactMessage.created.desc()).all()
        orders   = Order.query.order_by(Order.created.desc()).all()
        bookings = Booking.query.order_by(Booking.created.desc()).all()
        users    = User.query.order_by(User.created.desc()).all()
        return render_template('admin.html', logged_in=True, error=False,
                               messages=messages, orders=orders,
                               bookings=bookings, users=users)
    return render_template('admin.html', logged_in=False, error=False,
                           messages=[], orders=[], bookings=[], users=[])

# ── Admin Logout ──
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect('/admin')

# ── Create Database ──
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=os.getenv('DEBUG', 'False') == 'True')