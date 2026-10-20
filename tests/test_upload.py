"""
Automated Software Engineering Functional Test Execution:
- TC-03: Invalid skin lesion image upload
"""
import io
import pytest
from PIL import Image

def login_test_user(client):
    client.post('/register', data={
        'full_name': 'Upload Tester',
        'email': 'uploader@example.com',
        'password': 'SecurePassword123!',
        'confirm_password': 'SecurePassword123!',
        'role': 'patient'
    }, follow_redirects=True)
    client.post('/login', data={
        'email': 'uploader@example.com',
        'password': 'SecurePassword123!'
    }, follow_redirects=True)

def test_tc03_rejects_non_image_text_file(client):
    """
    Test Case ID: TC-03
    Test Case: Test whether the system rejects an unsupported or invalid image file.
    Priority: A
    Preconditions: User is logged in and opened upload page.
    Input Test Data: A non-image file such as a .txt document.
    Steps:
      1. Open upload page.
      2. Attempt to upload a .txt document.
      3. Click Analyze Image.
      4. Observe response.
    Expected: System rejects file, displays clear error, and halts analysis.
    """
    login_test_user(client)

    # Attempt to upload plain text file
    txt_data = io.BytesIO(b"This is a text document, not a skin lesion photograph.")
    response = client.post('/analyze', data={
        'image': (txt_data, 'notes.txt')
    }, content_type='multipart/form-data', follow_redirects=True)

    assert response.status_code == 200
    assert b"Upload rejected" in response.data or b"Unsupported file format" in response.data

def test_tc03_rejects_renamed_fake_image(client):
    """
    TC-03 Boundary Case: Renaming a text/binary file to .jpg to bypass frontend validation.
    The backend PIL inspection must detect corruption/invalid structure independently.
    """
    login_test_user(client)

    fake_jpeg_data = io.BytesIO(b"Plain text disguised as JPEG file header.")
    response = client.post('/analyze', data={
        'image': (fake_jpeg_data, 'fake_mole.jpg')
    }, content_type='multipart/form-data', follow_redirects=True)

    assert response.status_code == 200
    assert b"corrupt, invalid, or not a recognizable image file" in response.data

def test_tc03_rejects_missing_file(client):
    """
    TC-03 Edge Case: Submitting empty form with no file chosen.
    """
    login_test_user(client)

    response = client.post('/analyze', data={}, content_type='multipart/form-data', follow_redirects=True)
    assert response.status_code == 200
    assert b"No file was uploaded" in response.data or b"No image file was selected" in response.data

def test_valid_image_upload_success(client):
    """
    Verify that a genuine valid PNG/JPEG image passes validation and produces a screening record.
    """
    login_test_user(client)

    # Generate a genuine small 224x224 RGB image in memory
    img = Image.new('RGB', (224, 224), color=(210, 180, 160))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    response = client.post('/analyze', data={
        'image': (img_byte_arr, 'valid_lesion.png')
    }, content_type='multipart/form-data', follow_redirects=True)

    assert response.status_code == 200
    assert b"Preliminary Finding" in response.data
    assert b"Download Official PDF Report" in response.data
    assert b"7-Class Neural Network Probability Distribution" in response.data
    assert b"GENUINE TENSORFLOW CNN MODEL INFERENCE" in response.data
    assert b"HAM10000 7-Class Scheme" in response.data
