import sqlite3
import os
import json
from pathlib import Path
from config import Config

from flask import has_app_context, current_app

def get_db_connection():
    if has_app_context() and 'DATABASE_PATH' in current_app.config:
        db_path = Path(current_app.config['DATABASE_PATH'])
    else:
        db_path = Config.DATABASE_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'patient',
            username TEXT UNIQUE,
            avatar TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Dynamic migration for existing users table
    cursor.execute("PRAGMA table_info(users)")
    existing_user_cols = [row[1] for row in cursor.fetchall()]
    if 'username' not in existing_user_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN username TEXT")
    if 'avatar' not in existing_user_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN avatar TEXT")

    # Analysis Records Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            original_filename TEXT NOT NULL,
            stored_filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            result_status TEXT NOT NULL, -- 'genuine_model', 'demo_simulation', 'unavailable'
            classification TEXT NOT NULL,
            confidence_score REAL,
            explanation TEXT NOT NULL,
            is_demo INTEGER DEFAULT 0,
            model_version TEXT DEFAULT 'CNN-HAM10000-v1',
            lesion_metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)

    # Software Engineering Test Cases Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_cases (
            test_case_id TEXT PRIMARY KEY,
            test_cases TEXT NOT NULL,
            priority TEXT NOT NULL DEFAULT 'A',
            preconditions TEXT NOT NULL,
            input_test_data TEXT NOT NULL,
            steps_to_be_executed TEXT NOT NULL,
            expected_results TEXT NOT NULL,
            actual_results TEXT DEFAULT '',
            pass_fail TEXT DEFAULT 'Not Run',
            comments TEXT DEFAULT '',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Seed the 4 required test cases if not already present
    cursor.execute("SELECT COUNT(*) as count FROM test_cases")
    if cursor.fetchone()['count'] == 0:
        seed_test_cases = [
            (
                'TC-01',
                'Test if the user is able to log in successfully.',
                'A',
                'User must already be registered.',
                'Correct registered email/username and correct password.',
                '1. Open the login page.\n2. Enter the correct registered email/username and password in their respective fields.\n3. Click Submit/Login.',
                'The user should successfully log in and be redirected to the dashboard.',
                'Not executed yet.',
                'Not Run',
                'Pending verification during live test run.'
            ),
            (
                'TC-02',
                'Test if an unregistered user or a user with incorrect credentials is unable to log in to the site.',
                'A',
                'The user is not registered, or the supplied credentials do not match an existing account.',
                'An unregistered email/username with an incorrect password, or incorrect credentials for an existing account.',
                '1. Open the login page.\n2. Enter invalid credentials in the respective fields.\n3. Click Submit/Login.',
                'An appropriate error message should be displayed. Access to the protected dashboard must be denied, and the user should be able to try again.',
                'Not executed yet.',
                'Not Run',
                'Pending verification during live test run.'
            ),
            (
                'TC-03',
                'Test whether the system rejects an unsupported or invalid image file.',
                'A',
                'The user is logged in and has opened the image upload page.',
                'A non-image file such as a .txt document, a corrupt image file, or a file exceeding the configured upload size limit.',
                '1. Open the image upload page.\n2. Attempt to upload an unsupported, corrupt or oversized file.\n3. Click Analyze Image if the interface permits submission.\n4. Observe the response.',
                'The system should reject the invalid file, display a clear error message and prevent analysis from proceeding. The backend must validate the file independently of frontend validation.',
                'Not executed yet.',
                'Not Run',
                'Pending verification during live test run.'
            ),
            (
                'TC-04',
                'Test whether an authenticated user can view their own saved analysis history and download an associated report.',
                'A',
                'The user is logged in and has at least one saved analysis record.',
                'An existing analysis record belonging to the authenticated user.',
                '1. Log in with valid credentials.\n2. Open the dashboard or prediction history page.\n3. Select an existing analysis record.\n4. Open the record details.\n5. Click Download Report.\n6. Verify the downloaded PDF.',
                'The correct record should be displayed, and a readable PDF report containing the corresponding analysis details, result status and medical disclaimer should be downloaded successfully. The user must not be able to access another user''s records.',
                'Not executed yet.',
                'Not Run',
                'Pending verification during live test run.'
            )
        ]
        cursor.executemany("""
            INSERT INTO test_cases (
                test_case_id, test_cases, priority, preconditions,
                input_test_data, steps_to_be_executed, expected_results,
                actual_results, pass_fail, comments
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, seed_test_cases)

    conn.commit()
    conn.close()

# User repository helpers
def create_user(full_name, email, password_hash, role='patient', username=None, avatar=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        username_val = username.strip().lower() if username else email.strip().lower().split('@')[0]
        cursor.execute(
            "INSERT INTO users (full_name, email, password_hash, role, username, avatar) VALUES (?, ?, ?, ?, ?, ?)",
            (full_name.strip(), email.strip().lower(), password_hash, role, username_val, avatar)
        )
        conn.commit()
        user_id = cursor.lastrowid
        return user_id
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def get_user_by_email(email):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email.strip().lower(),)).fetchone()
    conn.close()
    return user

def get_user_by_username(username):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username.strip().lower(),)).fetchone()
    conn.close()
    return user

def get_user_by_email_or_username(identifier):
    conn = get_db_connection()
    clean_id = identifier.strip().lower()
    user = conn.execute(
        "SELECT * FROM users WHERE email = ? OR username = ?",
        (clean_id, clean_id)
    ).fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return user

def update_user_profile(user_id, full_name, email, username=None, avatar=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users
        SET full_name = ?, email = ?, username = ?, avatar = COALESCE(?, avatar)
        WHERE id = ?
    """, (full_name.strip(), email.strip().lower(), username.strip().lower() if username else None, avatar, user_id))
    conn.commit()
    conn.close()
    return True

# Analysis record helpers
def create_analysis_record(user_id, original_filename, stored_filename, file_path, file_size,
                           result_status, classification, confidence_score, explanation,
                           is_demo=0, model_version='CNN-HAM10000-v1', lesion_metadata=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    metadata_json = json.dumps(lesion_metadata) if lesion_metadata else '{}'
    cursor.execute("""
        INSERT INTO analysis_records (
            user_id, original_filename, stored_filename, file_path, file_size,
            result_status, classification, confidence_score, explanation,
            is_demo, model_version, lesion_metadata
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id, original_filename, stored_filename, str(file_path), file_size,
        result_status, classification, confidence_score, explanation,
        is_demo, model_version, metadata_json
    ))
    conn.commit()
    record_id = cursor.lastrowid
    conn.close()
    return record_id

def get_user_analysis_records(user_id, limit=None, status_filter=None, search_query=None):
    conn = get_db_connection()
    query = "SELECT * FROM analysis_records WHERE user_id = ?"
    params = [user_id]
    
    if status_filter and status_filter != 'all':
        query += " AND result_status = ?"
        params.append(status_filter)
        
    if search_query:
        query += " AND (original_filename LIKE ? OR classification LIKE ?)"
        term = f"%{search_query.strip()}%"
        params.extend([term, term])
        
    query += " ORDER BY created_at DESC"
    if limit:
        query += f" LIMIT {int(limit)}"
        
    records = conn.execute(query, params).fetchall()
    conn.close()
    return records

def get_analysis_record_by_id(record_id, user_id=None):
    conn = get_db_connection()
    if user_id is not None:
        record = conn.execute(
            "SELECT * FROM analysis_records WHERE id = ? AND user_id = ?",
            (record_id, user_id)
        ).fetchone()
    else:
        record = conn.execute("SELECT * FROM analysis_records WHERE id = ?", (record_id,)).fetchone()
    conn.close()
    return record

def get_user_analysis_stats(user_id):
    conn = get_db_connection()
    total = conn.execute("SELECT COUNT(*) as count FROM analysis_records WHERE user_id = ?", (user_id,)).fetchone()['count']
    genuine = conn.execute("SELECT COUNT(*) as count FROM analysis_records WHERE user_id = ? AND is_demo = 0 AND result_status = 'genuine_model'", (user_id,)).fetchone()['count']
    demo_count = conn.execute("SELECT COUNT(*) as count FROM analysis_records WHERE user_id = ? AND is_demo = 1", (user_id,)).fetchone()['count']
    benign = conn.execute("SELECT COUNT(*) as count FROM analysis_records WHERE user_id = ? AND classification LIKE '%Benign%'", (user_id,)).fetchone()['count']
    attention = conn.execute("SELECT COUNT(*) as count FROM analysis_records WHERE user_id = ? AND (classification LIKE '%Malignant%' OR classification LIKE '%Melanoma%')", (user_id,)).fetchone()['count']
    conn.close()
    return {
        'total': total,
        'genuine': genuine,
        'demo_count': demo_count,
        'benign': benign,
        'attention': attention
    }

# Administrator portal helpers
def get_admin_system_stats():
    conn = get_db_connection()
    total_users = conn.execute("SELECT COUNT(*) as count FROM users").fetchone()['count']
    total_records = conn.execute("SELECT COUNT(*) as count FROM analysis_records").fetchone()['count']
    genuine_records = conn.execute("SELECT COUNT(*) as count FROM analysis_records WHERE is_demo = 0").fetchone()['count']
    demo_records = conn.execute("SELECT COUNT(*) as count FROM analysis_records WHERE is_demo = 1").fetchone()['count']
    concerning_count = conn.execute("SELECT COUNT(*) as count FROM analysis_records WHERE classification LIKE '%Malignant%' OR classification LIKE '%Melanoma%'").fetchone()['count']
    benign_count = conn.execute("SELECT COUNT(*) as count FROM analysis_records WHERE classification LIKE '%Benign%' OR classification LIKE '%Nevus%' OR classification LIKE '%Nevi%'").fetchone()['count']
    conn.close()
    return {
        'total_users': total_users,
        'total_records': total_records,
        'genuine_records': genuine_records,
        'demo_records': demo_records,
        'concerning_count': concerning_count,
        'benign_count': benign_count
    }

def get_all_users_summary():
    conn = get_db_connection()
    # Safe read-only summary omitting password_hash
    users = conn.execute("""
        SELECT u.id, u.full_name, u.email, u.username, u.role, u.created_at,
               COUNT(a.id) as analysis_count
        FROM users u
        LEFT JOIN analysis_records a ON u.id = a.user_id
        GROUP BY u.id
        ORDER BY u.id ASC
    """).fetchall()
    conn.close()
    return users

def get_recent_global_records(limit=15):
    conn = get_db_connection()
    records = conn.execute("""
        SELECT a.id, a.user_id, a.original_filename, a.stored_filename, a.classification,
               a.confidence_score, a.result_status, a.is_demo, a.created_at,
               u.full_name as user_full_name, u.email as user_email
        FROM analysis_records a
        LEFT JOIN users u ON a.user_id = u.id
        ORDER BY a.created_at DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return records

# Test cases helpers
def get_all_test_cases():
    conn = get_db_connection()
    records = conn.execute("SELECT * FROM test_cases ORDER BY test_case_id ASC").fetchall()
    conn.close()
    return records

def update_test_case_execution(test_case_id, actual_results, pass_fail, comments):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE test_cases
        SET actual_results = ?, pass_fail = ?, comments = ?, updated_at = CURRENT_TIMESTAMP
        WHERE test_case_id = ?
    """, (actual_results, pass_fail, comments, test_case_id))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0

def reset_test_cases():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE test_cases
        SET actual_results = 'Not executed yet.', pass_fail = 'Not Run', comments = 'Pending live testing.', updated_at = CURRENT_TIMESTAMP
    """)
    conn.commit()
    conn.close()
