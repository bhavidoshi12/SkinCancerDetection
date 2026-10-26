"""
Automated Pytest Suite for Persistent Backend Database & Synchronized Patient Records:
Covers all 12 comprehensive scenarios:
 1. Patient registration persistence in database.
 2. Server restart simulation (clean connection / client).
 3. Patient medical history and concerns: saving and subsequent retrieval.
 4. Admin dashboard reflects patient-saved medical information and concerns.
 5. Admin updates to authorized fields: patient dashboard reflects changes on next load.
 6. Skin image upload: saved correctly to persistent folder with DB record and symptoms.
 7. Prediction history and PDF report retrieval by authorized user.
 8. Cross-patient isolation: patient A cannot access patient B's profile, history, images, or reports (HTTP 403).
 9. Admin-only endpoints: non-admin cannot access admin features (HTTP 403).
 10. Demo/sample records: clearly labelled and handled separately from real inferences.
 11. CSV export: contains authorized records and sanitizes CSV formula injection (CWE-1236).
 12. Application startup & DB init: clean idempotency without losing data or schema failures.
"""
import io
from pathlib import Path
import pytest
from PIL import Image
from database.db import (
    get_db_connection, init_db, get_patient_medical_profile,
    get_patient_full_details, search_patients
)
from blueprints.admin_bp import sanitize_csv_cell
from config import Config

def register_and_login(client, name, email, password, username=None, role='patient'):
    data = {
        'full_name': name,
        'email': email,
        'password': password,
        'confirm_password': password,
        'role': role
    }
    if username:
        data['username'] = username
    client.post('/register', data=data, follow_redirects=True)
    client.post('/login', data={'email': email, 'password': password}, follow_redirects=True)

def create_sample_image_bytes():
    img = Image.new('RGB', (224, 224), color=(180, 140, 120))
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    buf.seek(0)
    return buf

# =========================================================================
# Scenario 1: Patient registration persistence in the database
# =========================================================================
def test_scenario_01_patient_registration_persistence(client, app):
    with app.app_context():
        db = get_db_connection()
        initial_count = db.execute("SELECT COUNT(*) as c FROM users").fetchone()['c']

    register_and_login(client, 'Persistence Test Patient', 'persist@example.com', 'SecurePass123!', 'persist_user')

    with app.app_context():
        db = get_db_connection()
        row = db.execute("SELECT * FROM users WHERE email = 'persist@example.com'").fetchone()
        assert row is not None
        assert row['full_name'] == 'Persistence Test Patient'
        assert row['username'] == 'persist_user'
        # Password must be hashed, never plain text
        assert row['password_hash'] != 'SecurePass123!'
        assert row['password_hash'].startswith('scrypt:') or len(row['password_hash']) > 20

# =========================================================================
# Scenario 2: Server restart simulation (clean connection / new client)
# =========================================================================
def test_scenario_02_server_restart_simulation(client, app):
    register_and_login(client, 'Restart Patient', 'restart@example.com', 'Pass12345!', 'restart_user')
    client.get('/logout', follow_redirects=True)

    # Simulate restart by creating a completely fresh test client with fresh session
    new_client = app.test_client()
    login_resp = new_client.post('/login', data={
        'email': 'restart@example.com',
        'password': 'Pass12345!'
    }, follow_redirects=True)

    assert login_resp.status_code == 200
    assert b"Restart Patient" in login_resp.data

# =========================================================================
# Scenario 3: Patient medical history & concerns: saving & retrieval
# =========================================================================
def test_scenario_03_patient_medical_history_saving_and_retrieval(client, app):
    register_and_login(client, 'History Patient', 'history@example.com', 'Pass12345!')

    # Update medical profile
    update_resp = client.post('/patient/medical-profile/update', data={
        'skin_concerns': 'Irregular border on mole on right thigh with mild itching',
        'medical_history': 'Prior dysplastic nevus removed in 2023',
        'allergies': 'Latex, Penicillin',
        'sun_exposure_level': 'High',
        'fitzpatrick_skin_type': 'Type II (Burns easily, tans minimally)',
        'emergency_contact': 'Dr. Sharma (+1-555-0199)'
    }, follow_redirects=True)

    assert update_resp.status_code == 200
    assert b"Your personal medical history and skin concerns have been saved to the backend database." in update_resp.data

    # Verify retrieval on dashboard
    dash_resp = client.get('/dashboard')
    assert dash_resp.status_code == 200
    assert b"Irregular border on mole on right thigh" in dash_resp.data
    assert b"Prior dysplastic nevus removed in 2023" in dash_resp.data
    assert b"Latex, Penicillin" in dash_resp.data

# =========================================================================
# Scenario 4: Admin dashboard reflects patient medical info & concerns
# =========================================================================
def test_scenario_04_admin_dashboard_reflects_patient_info(client, app):
    # Register patient & update profile
    register_and_login(client, 'Sync Patient A', 'sync_a@example.com', 'Pass12345!')
    client.post('/patient/medical-profile/update', data={
        'skin_concerns': 'Darkening lesion on neck with occasional bleeding',
        'medical_history': 'Maternal history of melanoma',
        'allergies': 'None',
        'sun_exposure_level': 'Moderate',
        'fitzpatrick_skin_type': 'Type I (Burns always, never tans)',
        'emergency_contact': '911'
    }, follow_redirects=True)

    with app.app_context():
        db = get_db_connection()
        patient_id = db.execute("SELECT id FROM users WHERE email = 'sync_a@example.com'").fetchone()['id']

    client.get('/logout', follow_redirects=True)

    # Register & login as admin
    register_and_login(client, 'Chief Admin', 'admin_sync@example.com', 'AdminPass123!', role='admin')

    # View admin dashboard
    admin_dash = client.get('/admin')
    assert admin_dash.status_code == 200
    assert b"Sync Patient A" in admin_dash.data
    assert b"Darkening lesion on neck" in admin_dash.data

    # View patient detail page
    detail_resp = client.get(f'/admin/patient/{patient_id}')
    assert detail_resp.status_code == 200
    assert b"Darkening lesion on neck with occasional bleeding" in detail_resp.data
    assert b"Maternal history of melanoma" in detail_resp.data

# =========================================================================
# Scenario 5: Admin updates authorized fields -> patient dashboard reflects
# =========================================================================
def test_scenario_05_admin_updates_reflected_on_patient_dashboard(client, app):
    # Create patient
    register_and_login(client, 'Review Patient', 'review@example.com', 'Pass12345!')
    with app.app_context():
        patient_id = get_db_connection().execute("SELECT id FROM users WHERE email = 'review@example.com'").fetchone()['id']
    client.get('/logout', follow_redirects=True)

    # Admin modifies verification status and adds clinical notes
    register_and_login(client, 'Clinic Lead', 'clinic_lead@example.com', 'AdminPass123!', role='admin')
    post_resp = client.post(f'/admin/patient/{patient_id}', data={
        'verification_status': 'Verified by Physician',
        'admin_notes': 'Clinical review complete: lesion displays benign features. Schedule checkup in 12 months.',
        'phone': '+1-800-555-4321',
        'emergency_contact': 'Dr. Marcus (Dermatology Clinic)'
    }, follow_redirects=True)
    assert post_resp.status_code == 200
    client.get('/logout', follow_redirects=True)

    # Patient logs back in and checks dashboard
    client.post('/login', data={'email': 'review@example.com', 'password': 'Pass12345!'}, follow_redirects=True)
    patient_dash = client.get('/dashboard')
    assert patient_dash.status_code == 200
    assert b"Verified by Physician" in patient_dash.data
    assert b"Clinical review complete: lesion displays benign features" in patient_dash.data

# =========================================================================
# Scenario 6: Skin image upload: persistent folder & symptoms noted
# =========================================================================
def test_scenario_06_skin_image_upload_persistence(client, app):
    register_and_login(client, 'Uploader Patient', 'uploader_pers@example.com', 'Pass12345!')

    buf = create_sample_image_bytes()
    upload_resp = client.post('/analyze', data={
        'image': (buf, 'arm_lesion_test.jpg'),
        'symptoms': 'Slight redness around lesion circumference'
    }, content_type='multipart/form-data', follow_redirects=True)

    assert upload_resp.status_code == 200

    # Verify record in DB
    with app.app_context():
        db = get_db_connection()
        rec = db.execute("SELECT * FROM analysis_records WHERE symptoms_noted = 'Slight redness around lesion circumference'").fetchone()
        assert rec is not None
        assert 'patient_images' in rec['file_path'] or 'patient_images' in rec['stored_filename']
        # Verify file exists on disk
        target_path = Path(rec['file_path'])
        assert target_path.exists()

# =========================================================================
# Scenario 7: Prediction history & PDF report retrieval by authorized user
# =========================================================================
def test_scenario_07_prediction_history_and_pdf_retrieval(client, app):
    register_and_login(client, 'Report Patient', 'report_pers@example.com', 'Pass12345!')

    buf = create_sample_image_bytes()
    client.post('/analyze', data={
        'image': (buf, 'report_scan.jpg'),
        'symptoms': 'Dry surface'
    }, content_type='multipart/form-data', follow_redirects=True)

    with app.app_context():
        rec_id = get_db_connection().execute("SELECT id FROM analysis_records ORDER BY id DESC LIMIT 1").fetchone()['id']

    # Download report
    report_resp = client.get(f'/report/{rec_id}')
    assert report_resp.status_code == 200
    assert report_resp.headers['Content-Type'] == 'application/pdf'
    assert len(report_resp.data) > 500

    # Verify pdf path updated in db and file exists on disk
    with app.app_context():
        rec = get_db_connection().execute("SELECT pdf_report_path, file_path FROM analysis_records WHERE id = ?", (rec_id,)).fetchone()
        assert rec['pdf_report_path'] is not None
        pdf_filename = Path(rec['pdf_report_path']).name
        test_reports_dir = Path(app.config.get('UPLOAD_FOLDER', Config.UPLOAD_FOLDER)) / 'reports'
        pdf_disk_file = test_reports_dir / pdf_filename
        assert pdf_disk_file.exists() or (Config.BASE_DIR / rec['pdf_report_path']).exists()

# =========================================================================
# Scenario 8: Cross-patient isolation (Patient A vs Patient B)
# =========================================================================
def test_scenario_08_cross_patient_isolation_security(client, app):
    # Patient A creates a scan
    register_and_login(client, 'Patient Alpha', 'alpha_sec@example.com', 'Pass12345!')
    buf = create_sample_image_bytes()
    client.post('/analyze', data={'image': (buf, 'alpha_mole.jpg')}, content_type='multipart/form-data', follow_redirects=True)

    with app.app_context():
        rec = get_db_connection().execute("SELECT id, stored_filename FROM analysis_records ORDER BY id DESC LIMIT 1").fetchone()
        alpha_rec_id = rec['id']
        alpha_img_name = rec['stored_filename']

    client.get('/logout', follow_redirects=True)

    # Patient B attempts unauthorized access to Patient A's resources
    register_and_login(client, 'Patient Beta', 'beta_sec@example.com', 'Pass12345!')

    # 1. Attempt viewing result details: unauthorized access denied
    res_resp = client.get(f'/results/{alpha_rec_id}', follow_redirects=True)
    assert b"Record not found or access denied" in res_resp.data or res_resp.status_code == 403

    # 2. Attempt downloading PDF report: 403 Forbidden
    rep_resp = client.get(f'/report/{alpha_rec_id}')
    assert rep_resp.status_code == 403

    # 3. Attempt direct download of Patient A's image file: 403 Forbidden
    img_resp = client.get(f'/uploads/{alpha_img_name}')
    assert img_resp.status_code == 403

# =========================================================================
# Scenario 9: Admin-only endpoints protected against non-admins
# =========================================================================
def test_scenario_09_admin_only_endpoints_protection(client, app):
    register_and_login(client, 'Standard Patient', 'patient_norm@example.com', 'Pass12345!', role='patient')

    # Non-admin attempting admin dashboard
    admin_resp = client.get('/admin')
    assert admin_resp.status_code == 403

    # Non-admin attempting admin patient detail
    detail_resp = client.get('/admin/patient/1')
    assert detail_resp.status_code == 403

    # Non-admin attempting admin CSV export
    csv_resp = client.get('/admin/export-patients-csv')
    assert csv_resp.status_code == 403

# =========================================================================
# Scenario 10: Demo/sample records distinction
# =========================================================================
def test_scenario_10_demo_sample_records_distinction(client, app):
    register_and_login(client, 'Demo Check Patient', 'demo_check@example.com', 'Pass12345!')

    # Run demo sample analysis
    client.post('/sample-analysis', data={'sample_id': 'HAM_BENIGN_01'}, follow_redirects=True)

    with app.app_context():
        rec = get_db_connection().execute("SELECT * FROM analysis_records WHERE is_demo = 1 ORDER BY id DESC LIMIT 1").fetchone()
        assert rec is not None
        assert rec['is_demo'] == 1
        assert rec['result_status'] == 'demo_simulation'

    # Check dashboard shows demo badge
    dash_resp = client.get('/dashboard')
    assert dash_resp.status_code == 200
    assert b"Demo / Sample Record" in dash_resp.data

# =========================================================================
# Scenario 11: CSV export authorized records & formula injection defense
# =========================================================================
def test_scenario_11_csv_export_and_formula_injection_defense(client, app):
    # Test formula injection unit sanitizer
    assert sanitize_csv_cell("=CMD|' /C calc'!A0") == "'=CMD|' /C calc'!A0"
    assert sanitize_csv_cell("+12345") == "'+12345"
    assert sanitize_csv_cell("-50") == "'-50"
    assert sanitize_csv_cell("@SUM(A1:A10)") == "'@SUM(A1:A10)"
    assert sanitize_csv_cell("Normal Note") == "Normal Note"

    # Register patient with formula injection in skin concerns
    register_and_login(client, 'CSV Target', 'csv_target@example.com', 'Pass12345!')
    client.post('/patient/medical-profile/update', data={
        'skin_concerns': '=cmd|\'/c calc\'!A0',
        'medical_history': '@malicious_eval',
        'allergies': '+penicillin'
    }, follow_redirects=True)
    client.get('/logout', follow_redirects=True)

    # Admin exports CSV
    register_and_login(client, 'Audit Admin', 'csv_admin@example.com', 'AdminPass123!', role='admin')
    csv_resp = client.get('/admin/export-patients-csv')
    assert csv_resp.status_code == 200
    assert 'text/csv' in csv_resp.headers['Content-Type']

    csv_text = csv_resp.data.decode('utf-8-sig')
    # Must contain sanitized single quote prefix
    assert "'=cmd|'/c calc'!A0" in csv_text
    assert "'@malicious_eval" in csv_text
    assert "'+penicillin" in csv_text

# =========================================================================
# Scenario 12: Application startup & DB init idempotency
# =========================================================================
def test_scenario_12_db_init_idempotency_and_schema_preservation(client, app):
    with app.app_context():
        # First check initial count
        db = get_db_connection()
        users_before = db.execute("SELECT COUNT(*) as c FROM users").fetchone()['c']

        # Call init_db multiple times consecutively
        init_db()
        init_db()

        users_after = db.execute("SELECT COUNT(*) as c FROM users").fetchone()['c']
        # No users lost or corrupted
        assert users_after == users_before

        # Check table schemas are intact
        db.execute("SELECT verification_status, admin_notes FROM patient_medical_profiles LIMIT 1")
        db.execute("SELECT symptoms_noted, pdf_report_path, is_demo FROM analysis_records LIMIT 1")
        db.execute("SELECT record_type, action, timestamp FROM audit_logs LIMIT 1")
