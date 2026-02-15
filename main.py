from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Perfume
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-key-change-this-in-production' # Required for sessions

# FIXED: Changed __name__ to __file__ so it finds the correct folder
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'perfumes.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Redirects here if unauthorized users try to access protected routes

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize database and dummy data
with app.app_context():
    db.create_all()
    if not Perfume.query.first():
        sample_perfumes = [
            Perfume(name='Midnight Rose', brand='Lancôme', price=85.00, description='A sweet and sultry floral scent.', image_url='https://via.placeholder.com/200x200?text=Midnight+Rose'),
            Perfume(name='Ocean Breeze', brand='Aqua Di', price=60.00, description='Fresh, aquatic, and invigorating.', image_url='https://via.placeholder.com/200x200?text=Ocean+Breeze'),
            Perfume(name='Oud Wood', brand='Tom Ford', price=250.00, description='Rich, dark, and woody notes.', image_url='https://via.placeholder.com/200x200?text=Oud+Wood'),
            Perfume(name='Vanilla Sky', brand='Skylar', price=45.00, description='Warm vanilla with a hint of caramel.', image_url='https://via.placeholder.com/200x200?text=Vanilla+Sky')
        ]
        db.session.bulk_save_objects(sample_perfumes)
        db.session.commit()

@app.route('/')
def index():
    all_perfumes = Perfume.query.all()
    return render_template('index.html', perfumes=all_perfumes)

# --- NEW AUTHENTICATION ROUTES ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Prevent duplicate usernames
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different one.')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        # Check if user exists and password is correct
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Example of a protected route
    return f"<h1>Welcome to your dashboard, {current_user.username}!</h1><a href='/'>Back to Home</a>"

if __name__ == '__main__':
    app.run(debug=True)