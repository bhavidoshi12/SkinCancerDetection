import re
from functools import wraps
from flask import session, redirect, url_for, flash, abort, request
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_user_by_email, get_user_by_id, create_user, get_user_by_email_or_username

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

def validate_registration_data(full_name, email, password, confirm_password):
    errors = []
    
    if not full_name or len(full_name.strip()) < 2:
        errors.append("Please enter your full name (at least 2 characters).")
        
    if not email or not EMAIL_REGEX.match(email.strip()):
        errors.append("Please provide a valid email address.")
        
    if not password or len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
        
    if not any(char.isdigit() for char in password):
        errors.append("Password should contain at least one numerical digit.")
        
    if password != confirm_password:
        errors.append("Password and confirmation password do not match.")
        
    if not errors:
        existing_user = get_user_by_email(email)
        if existing_user:
            errors.append("An account with this email address is already registered.")
            
    return errors

def register_user(full_name, email, password, role='patient', username=None):
    password_hash = generate_password_hash(password, method='scrypt')
    user_id = create_user(full_name, email, password_hash, role, username=username)
    return user_id

def authenticate_user(identifier, password):
    if not identifier or not password:
        return None, "Please enter both email/username and password."
        
    user = get_user_by_email_or_username(identifier)
    if not user:
        return None, "Invalid email or password. Please verify your credentials and try again."
        
    if not check_password_hash(user['password_hash'], password):
        return None, "Invalid email or password. Please verify your credentials and try again."
        
    return user, None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('auth.login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in with administrator privileges to access this portal.", "warning")
            return redirect(url_for('auth.login', next=request.path))
        if session.get('user_role') != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    if 'user_id' in session:
        return get_user_by_id(session['user_id'])
    return None
