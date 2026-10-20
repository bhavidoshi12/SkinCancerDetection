"""
Automated Software Engineering Functional Test Execution:
- TC-04: View prediction history and download report
- User Data Isolation: Verify that user A cannot access or download user B's records
"""
import io
import pytest
from PIL import Image

def create_user_and_scan(client, name, email, password):
    client.post('/register', data={
        'full_name': name,
        'email': email,
        'password': password,
        'confirm_password': password,
        'role': 'patient'
    }, follow_redirects=True)
    
    client.post('/login', data={'email': email, 'password': password}, follow_redirects=True)
    
    # Upload an image
    img = Image.new('RGB', (224, 224), color=(200, 170, 150))
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    buf.seek(0)
    
    client.post('/analyze', data={
        'image': (buf, 'test_lesion.jpg')
    }, content_type='multipart/form-data', follow_redirects=True)

def test_tc04_view_history_and_download_report(client):
    """
    Test Case ID: TC-04
    Test Case: Test whether an authenticated user can view their own saved analysis history and download an associated report.
    Priority: A
    Preconditions: User is logged in and has at least one saved analysis record.
    Input Test Data: An existing analysis record belonging to the authenticated user.
    Steps:
      1. Log in with valid credentials.
      2. Open history page.
      3. Select an existing record.
      4. Open record details.
      5. Click Download Report.
      6. Verify downloaded PDF.
    Expected: Record displayed, PDF downloaded with application/pdf mime type and disclaimers.
    """
    create_user_and_scan(client, 'Alice Smith', 'alice@example.com', 'AlicePassword123!')

    # Step 2: Open History page
    history_response = client.get('/history')
    assert history_response.status_code == 200
    assert b"test_lesion.jpg" in history_response.data
    assert b"PDF" in history_response.data

    # Step 4: Open Record Details
    record_response = client.get('/results/1')
    assert record_response.status_code == 200
    assert b"Download Official PDF Report" in record_response.data

    # Step 5-6: Download PDF Report
    pdf_response = client.get('/report/1/download')
    assert pdf_response.status_code == 200
    assert pdf_response.headers.get('Content-Type') == 'application/pdf'
    assert b'%PDF' in pdf_response.data  # Valid PDF binary signature
    assert len(pdf_response.data) > 1000

def test_user_data_isolation_and_security(client):
    """
    Verify that User B CANNOT download or view User A's private medical screening report.
    Returns 403 Forbidden.
    """
    # Create User A with record ID 1
    create_user_and_scan(client, 'User Alpha', 'alpha@example.com', 'AlphaPass123!')
    client.get('/logout', follow_redirects=True)

    # Create User B
    client.post('/register', data={
        'full_name': 'User Beta',
        'email': 'beta@example.com',
        'password': 'BetaPass123!',
        'confirm_password': 'BetaPass123!',
        'role': 'patient'
    }, follow_redirects=True)
    client.post('/login', data={'email': 'beta@example.com', 'password': 'BetaPass123!'}, follow_redirects=True)

    # Attempt to download User A's report (record ID 1) as User B
    unauthorized_report = client.get('/report/1/download')
    assert unauthorized_report.status_code == 403

    # Attempt to view User A's result page as User B
    unauthorized_view = client.get('/results/1', follow_redirects=True)
    assert b"Record not found or access denied" in unauthorized_view.data or unauthorized_view.status_code == 403
