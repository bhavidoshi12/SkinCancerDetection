"""
Automated Security and Role-Based Access Control (RBAC) Tests for the Administrator Portal.
Verifies:
1. Unauthenticated users cannot access /admin (redirected to /login).
2. Authenticated non-admin users (patient/physician) receive 403 Forbidden.
3. Authenticated admin users have full access to the admin dashboard, KPIs, and user roster.
4. Navigation bar dynamically displays Admin Portal only for admin users.
"""
import pytest
from database.db import create_user
from werkzeug.security import generate_password_hash

def test_admin_portal_unauthenticated_redirect(client):
    """Unauthenticated access to /admin must redirect to login."""
    res = client.get('/admin', follow_redirects=False)
    assert res.status_code == 302
    assert '/login' in res.headers['Location']

    res2 = client.get('/admin/dashboard', follow_redirects=False)
    assert res2.status_code == 302
    assert '/login' in res2.headers['Location']

def test_non_admin_forbidden_access(client):
    """Regular patient or physician accounts must receive HTTP 403 Forbidden when accessing /admin."""
    # Register standard patient
    client.post('/register', data={
        'full_name': 'Standard Patient',
        'email': 'patient@example.com',
        'password': 'PatientPass123!',
        'confirm_password': 'PatientPass123!',
        'role': 'patient'
    }, follow_redirects=True)

    # Login as patient
    client.post('/login', data={
        'email': 'patient@example.com',
        'password': 'PatientPass123!'
    }, follow_redirects=True)

    # Attempt to access /admin
    res = client.get('/admin')
    assert res.status_code == 403
    assert b"Access Denied" in res.data or b"403" in res.data

def test_admin_authorized_access(client):
    """Users with role 'admin' must successfully access the administrator dashboard."""
    # Create admin user in test database
    with client.application.app_context():
        pwd_hash = generate_password_hash('AdminPass123!', method='scrypt')
        create_user(
            full_name='Lead Admin',
            email='leadadmin@example.com',
            password_hash=pwd_hash,
            role='admin',
            username='leadadmin'
        )

    # Login as admin
    login_res = client.post('/login', data={
        'email': 'leadadmin@example.com',
        'password': 'AdminPass123!'
      }, follow_redirects=True)
    assert login_res.status_code == 200

    # Access admin dashboard
    admin_res = client.get('/admin/dashboard')
    assert admin_res.status_code == 200
    assert b"Administrative Command Center" in admin_res.data
    assert b"Registered Accounts" in admin_res.data
    assert b"TensorFlow / Keras MobileNetV2 Architecture" in admin_res.data
    assert b"leadadmin@example.com" in admin_res.data
    assert b"Admin Portal" in admin_res.data

def test_admin_navbar_visibility_per_role(client):
    """Navbar should show 'Admin Portal' link only when logged in as admin."""
    # 1. Anonymous: no Admin Portal link
    anon_res = client.get('/')
    assert b"Admin Portal" not in anon_res.data

    # 2. Patient: no Admin Portal link
    client.post('/register', data={
        'full_name': 'Regular User',
        'email': 'regular@example.com',
        'password': 'RegularPass123!',
        'confirm_password': 'RegularPass123!',
        'role': 'patient'
    }, follow_redirects=True)
    client.post('/login', data={'email': 'regular@example.com', 'password': 'RegularPass123!'}, follow_redirects=True)
    user_res = client.get('/')
    assert b"Admin Portal" not in user_res.data

    # Logout
    client.get('/logout')

    # 3. Admin: Admin Portal link is visible
    with client.application.app_context():
        pwd_hash = generate_password_hash('AdminKey123!', method='scrypt')
        create_user(
            full_name='Super Admin',
            email='super@admin.com',
            password_hash=pwd_hash,
            role='admin',
            username='superadmin'
        )
    client.post('/login', data={'email': 'super@admin.com', 'password': 'AdminKey123!'}, follow_redirects=True)
    admin_home = client.get('/')
    assert b"Admin Portal" in admin_home.data
