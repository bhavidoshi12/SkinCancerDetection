"""
Automated Software Engineering Functional Test Execution:
- TC-01: Successful user login
- TC-02: Login with invalid credentials
"""
import pytest

def test_tc01_successful_user_login(client):
    """
    Test Case ID: TC-01
    Test Case: Test if the user is able to log in successfully.
    Priority: A
    Preconditions: User must already be registered.
    Input Test Data: Correct registered email/username and correct password.
    Steps:
      1. Open registration and register a new user.
      2. Open the login page.
      3. Enter correct registered email and password.
      4. Click Submit/Login.
    Expected: User should successfully log in and be redirected to dashboard.
    """
    # Step 1: Precondition - Register user
    reg_response = client.post('/register', data={
        'full_name': 'Test Physician',
        'email': 'physician@example.com',
        'password': 'Password123!',
        'confirm_password': 'Password123!',
        'role': 'physician'
    }, follow_redirects=True)
    assert reg_response.status_code == 200
    assert b"Account registered successfully" in reg_response.data

    # Step 2-4: Login with valid credentials
    login_response = client.post('/login', data={
        'email': 'physician@example.com',
        'password': 'Password123!'
    }, follow_redirects=True)
    
    assert login_response.status_code == 200
    # Expected: redirected to dashboard and authenticated welcome message displayed
    assert b"Welcome, Test Physician" in login_response.data
    assert b"Upload New Image" in login_response.data

def test_tc02_login_with_invalid_credentials(client):
    """
    Test Case ID: TC-02
    Test Case: Test if an unregistered user or a user with incorrect credentials is not able to login.
    Priority: A
    Preconditions: User is not registered or credentials do not match.
    Input Test Data: An unregistered email with an incorrect password.
    Steps:
      1. Open login page.
      2. Enter invalid credentials.
      3. Click Submit/Login.
    Expected: Proper error must be displayed and access to dashboard denied.
    """
    # Attempt 1: Completely unregistered user
    response_unregistered = client.post('/login', data={
        'email': 'nonexistent_user@example.com',
        'password': 'WrongPassword999!'
    }, follow_redirects=True)
    
    assert response_unregistered.status_code == 200
    assert b"Invalid email or password" in response_unregistered.data
    assert b"Dashboard" not in response_unregistered.data or b"Welcome, " not in response_unregistered.data

    # Attempt 2: Register a user then enter incorrect password
    client.post('/register', data={
        'full_name': 'John Doe',
        'email': 'johndoe@example.com',
        'password': 'RealPassword123!',
        'confirm_password': 'RealPassword123!',
        'role': 'patient'
    }, follow_redirects=True)

    response_wrong_password = client.post('/login', data={
        'email': 'johndoe@example.com',
        'password': 'IncorrectPassword!'
    }, follow_redirects=True)

    assert response_wrong_password.status_code == 200
    assert b"Invalid email or password" in response_wrong_password.data
    assert b"Welcome, John Doe" not in response_wrong_password.data

def test_unauthenticated_dashboard_access_denied(client):
    """
    Verify that protected dashboard requires active session.
    """
    response = client.get('/dashboard', follow_redirects=True)
    assert response.status_code == 200
    assert b"Please log in to access this page" in response.data

def test_login_with_username_and_profile_access(client):
    """
    Verify that users can log in using their username instead of email,
    access their personal profile page, and update their full name.
    """
    # Register user with explicit username
    reg_response = client.post('/register', data={
        'full_name': 'Bhavi Doshi',
        'email': 'bhavi.test@example.com',
        'username': 'bhavitest',
        'password': 'Password123!',
        'confirm_password': 'Password123!',
        'role': 'patient'
    }, follow_redirects=True)
    assert reg_response.status_code == 200

    # Log in using username instead of email
    login_response = client.post('/login', data={
        'email': 'bhavitest',  # entering username in identifier field
        'password': 'Password123!'
    }, follow_redirects=True)
    assert login_response.status_code == 200
    assert b"Welcome, Bhavi Doshi" in login_response.data

    # Access profile page
    profile_response = client.get('/profile')
    assert profile_response.status_code == 200
    assert b"Member Profile" in profile_response.data
    assert b"bhavitest" in profile_response.data
    assert b"bhavi.test@example.com" in profile_response.data

    # Update profile full name
    update_response = client.post('/profile', data={
        'full_name': 'Bhavi Doshi Updated',
        'username': 'bhavitest'
    }, follow_redirects=True)
    assert update_response.status_code == 200
    assert b"Profile updated successfully" in update_response.data
    assert b"Bhavi Doshi Updated" in update_response.data

