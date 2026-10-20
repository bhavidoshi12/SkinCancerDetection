from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from services.auth_service import validate_registration_data, register_user, authenticate_user, login_required, get_current_user
from database.db import update_user_profile, get_user_analysis_stats

auth_bp = Blueprint('auth', __name__, url_prefix='')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('analysis.dashboard'))
        
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        username = request.form.get('username', '').strip() or None
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', 'patient')
        
        errors = validate_registration_data(full_name, email, password, confirm_password)
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/register.html', full_name=full_name, email=email, role=role)
            
        user_id = register_user(full_name, email, password, role, username=username)
        if user_id:
            flash("Account registered successfully! You can now log in.", "success")
            return redirect(url_for('auth.login'))
        else:
            flash("An account with this email address already exists. Please log in or use a different email.", "danger")
            return render_template('auth/register.html', full_name=full_name, email=email, role=role)
            
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('analysis.dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        user, error = authenticate_user(email, password)
        if error:
            flash(error, 'danger')
            return render_template('auth/login.html', email=email)
            
        # Set session
        session.clear()
        session['user_id'] = user['id']
        session['user_name'] = user['full_name']
        session['user_email'] = user['email']
        session['user_role'] = user['role']
        session['user_username'] = user['username'] if 'username' in user.keys() and user['username'] else ''
        session['user_avatar'] = user['avatar'] if 'avatar' in user.keys() and user['avatar'] else ''
        
        flash(f"Welcome back, {user['full_name']}!", "success")
        next_url = request.args.get('next')
        if next_url and next_url.startswith('/'):
            return redirect(next_url)
        return redirect(url_for('analysis.dashboard'))
        
    return render_template('auth/login.html')

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = get_current_user()
    stats = get_user_analysis_stats(user['id'])
    
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        username = request.form.get('username', '').strip()
        
        if not full_name or len(full_name) < 2:
            flash("Name must be at least 2 characters long.", "danger")
        else:
            update_user_profile(user['id'], full_name, user['email'], username=username)
            session['user_name'] = full_name
            session['user_username'] = username
            flash("Profile updated successfully.", "success")
            return redirect(url_for('auth.profile'))
            
    return render_template('auth/profile.html', user=user, stats=stats)

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('auth.login'))
