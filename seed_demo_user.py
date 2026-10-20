"""
Seed Script: Pre-registered Demo Member (Bhavi Doshi)
Creates the official demo account and realistic preloaded sample history records
for the college mini-project demonstration.
"""

import os
import shutil
import sqlite3
import json
from pathlib import Path
from werkzeug.security import generate_password_hash
from config import Config
from database.db import get_db_connection, init_db

DEMO_USER = {
    'full_name': 'Bhavi Doshi',
    'email': 'bhavidoshi12@gmail.com',
    'username': 'bhavi12',
    'password': 'Bhavi@2026!',
    'role': 'patient',
    'avatar': 'avatar_bhavi.png'
}

DEMO_ADMIN = {
    'full_name': 'System Administrator',
    'email': 'admin@dermacare.ai',
    'username': 'admin',
    'password': 'Admin@2026!Demo',
    'role': 'admin',
    'avatar': ''
}

SAMPLE_RECORDS = [
    {
        'title': 'HAM10000_ISIC_0024306.jpg',
        'classification': 'Melanocytic Nevi (nv) — Common Benign Mole',
        'confidence_score': 94.20,
        'result_status': 'demo_simulation',
        'is_demo': 1,
        'created_at': '2026-10-10 14:22:15',
        'explanation': (
            "PRELOADED DEMO/SAMPLE RECORD: Reference benchmark from the HAM10000 dataset (ISIC_0024306). "
            "Illustrates a classic benign melanocytic nevus featuring regular pigmentation and symmetric architecture. "
            "Not a live clinical finding."
        ),
        'metadata': {
            'width': 256, 'height': 256, 'format': 'JPEG', 'aspect_ratio': 1.0, 'sample_case': True,
            'all_class_scores': [
                {'code': 'nv', 'label': 'Melanocytic Nevi (nv)', 'probability': 94.20, 'is_concerning': False},
                {'code': 'bkl', 'label': 'Benign Keratosis-like Lesions (bkl)', 'probability': 3.10, 'is_concerning': False},
                {'code': 'mel', 'label': 'Melanoma (mel)', 'probability': 1.50, 'is_concerning': True},
                {'code': 'df', 'label': 'Dermatofibroma (df)', 'probability': 0.55, 'is_concerning': False},
                {'code': 'bcc', 'label': 'Basal Cell Carcinoma (bcc)', 'probability': 0.35, 'is_concerning': True},
                {'code': 'vasc', 'label': 'Vascular Lesions (vasc)', 'probability': 0.20, 'is_concerning': False},
                {'code': 'akiec', 'label': 'Actinic Keratoses (akiec)', 'probability': 0.10, 'is_concerning': True}
            ]
        }
    },
    {
        'title': 'HAM10000_ISIC_0029314.jpg',
        'classification': 'Melanoma (mel) — High Risk / Requires Urgent Evaluation',
        'confidence_score': 88.70,
        'result_status': 'demo_simulation',
        'is_demo': 1,
        'created_at': '2026-10-14 10:15:40',
        'explanation': (
            "PRELOADED DEMO/SAMPLE RECORD: Reference benchmark from the HAM10000 dataset (ISIC_0029314). "
            "Illustrates superficial spreading melanoma with characteristic asymmetry, border irregularity, and multi-color pigment variegation. "
            "Not a live clinical finding."
        ),
        'metadata': {
            'width': 256, 'height': 256, 'format': 'JPEG', 'aspect_ratio': 1.0, 'sample_case': True,
            'all_class_scores': [
                {'code': 'mel', 'label': 'Melanoma (mel)', 'probability': 88.70, 'is_concerning': True},
                {'code': 'nv', 'label': 'Melanocytic Nevi (nv)', 'probability': 6.20, 'is_concerning': False},
                {'code': 'bkl', 'label': 'Benign Keratosis-like Lesions (bkl)', 'probability': 2.80, 'is_concerning': False},
                {'code': 'bcc', 'label': 'Basal Cell Carcinoma (bcc)', 'probability': 1.20, 'is_concerning': True},
                {'code': 'akiec', 'label': 'Actinic Keratoses (akiec)', 'probability': 0.60, 'is_concerning': True},
                {'code': 'df', 'label': 'Dermatofibroma (df)', 'probability': 0.30, 'is_concerning': False},
                {'code': 'vasc', 'label': 'Vascular Lesions (vasc)', 'probability': 0.20, 'is_concerning': False}
            ]
        }
    },
    {
        'title': 'HAM10000_ISIC_0024310.jpg',
        'classification': 'Basal Cell Carcinoma (bcc) — Malignant Non-Melanoma',
        'confidence_score': 91.50,
        'result_status': 'demo_simulation',
        'is_demo': 1,
        'created_at': '2026-10-17 16:45:00',
        'explanation': (
            "PRELOADED DEMO/SAMPLE RECORD: Reference benchmark from the HAM10000 dataset (ISIC_0024310). "
            "Illustrates nodular basal cell carcinoma with translucent appearance and arborizing telangiectasia. "
            "Not a live clinical finding."
        ),
        'metadata': {
            'width': 256, 'height': 256, 'format': 'JPEG', 'aspect_ratio': 1.0, 'sample_case': True,
            'all_class_scores': [
                {'code': 'bcc', 'label': 'Basal Cell Carcinoma (bcc)', 'probability': 91.50, 'is_concerning': True},
                {'code': 'akiec', 'label': 'Actinic Keratoses (akiec)', 'probability': 4.20, 'is_concerning': True},
                {'code': 'bkl', 'label': 'Benign Keratosis-like Lesions (bkl)', 'probability': 2.10, 'is_concerning': False},
                {'code': 'mel', 'label': 'Melanoma (mel)', 'probability': 1.10, 'is_concerning': True},
                {'code': 'nv', 'label': 'Melanocytic Nevi (nv)', 'probability': 0.60, 'is_concerning': False},
                {'code': 'df', 'label': 'Dermatofibroma (df)', 'probability': 0.35, 'is_concerning': False},
                {'code': 'vasc', 'label': 'Vascular Lesions (vasc)', 'probability': 0.15, 'is_concerning': False}
            ]
        }
    },
    {
        'title': 'HAM10000_ISIC_0024312.jpg',
        'classification': 'Benign Keratosis-like Lesions (bkl) — Non-Cancerous',
        'confidence_score': 92.00,
        'result_status': 'demo_simulation',
        'is_demo': 1,
        'created_at': '2026-10-18 09:30:10',
        'explanation': (
            "PRELOADED DEMO/SAMPLE RECORD: Reference benchmark from the HAM10000 dataset (ISIC_0024312). "
            "Illustrates a benign seborrheic keratosis lesion with characteristic stuck-on appearance and defined borders. "
            "Not a live clinical finding."
        ),
        'metadata': {
            'width': 256, 'height': 256, 'format': 'JPEG', 'aspect_ratio': 1.0, 'sample_case': True,
            'all_class_scores': [
                {'code': 'bkl', 'label': 'Benign Keratosis-like Lesions (bkl)', 'probability': 92.00, 'is_concerning': False},
                {'code': 'nv', 'label': 'Melanocytic Nevi (nv)', 'probability': 4.40, 'is_concerning': False},
                {'code': 'mel', 'label': 'Melanoma (mel)', 'probability': 1.80, 'is_concerning': True},
                {'code': 'akiec', 'label': 'Actinic Keratoses (akiec)', 'probability': 0.90, 'is_concerning': True},
                {'code': 'bcc', 'label': 'Basal Cell Carcinoma (bcc)', 'probability': 0.50, 'is_concerning': True},
                {'code': 'df', 'label': 'Dermatofibroma (df)', 'probability': 0.25, 'is_concerning': False},
                {'code': 'vasc', 'label': 'Vascular Lesions (vasc)', 'probability': 0.15, 'is_concerning': False}
            ]
        }
    }
]

def seed_demo_member():
    print("[1/3] Ensuring database schema is initialized...")
    init_db()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Create or retrieve demo user
    cursor.execute("SELECT id FROM users WHERE email = ? OR username = ?", (DEMO_USER['email'], DEMO_USER['username']))
    row = cursor.fetchone()
    
    if row:
        user_id = row['id']
        print(f"[2/3] Demo member '{DEMO_USER['full_name']}' already exists (User ID: {user_id}).")
        # Ensure password hash is updated to standard demo password
        cursor.execute(
            "UPDATE users SET password_hash = ?, full_name = ?, username = ?, avatar = ? WHERE id = ?",
            (generate_password_hash(DEMO_USER['password'], method='scrypt'),
             DEMO_USER['full_name'], DEMO_USER['username'], DEMO_USER['avatar'], user_id)
        )
        conn.commit()
    else:
        password_hash = generate_password_hash(DEMO_USER['password'], method='scrypt')
        cursor.execute(
            "INSERT INTO users (full_name, email, username, password_hash, role, avatar) VALUES (?, ?, ?, ?, ?, ?)",
            (DEMO_USER['full_name'], DEMO_USER['email'], DEMO_USER['username'], password_hash, DEMO_USER['role'], DEMO_USER['avatar'])
        )
        conn.commit()
        user_id = cursor.lastrowid
        print(f"[2/3] Created demo member '{DEMO_USER['full_name']}' (User ID: {user_id}).")

    # 1b. Create or retrieve demo admin
    cursor.execute("SELECT id FROM users WHERE email = ? OR username = ?", (DEMO_ADMIN['email'], DEMO_ADMIN['username']))
    admin_row = cursor.fetchone()
    if admin_row:
        admin_id = admin_row['id']
        cursor.execute(
            "UPDATE users SET password_hash = ?, full_name = ?, username = ?, role = 'admin' WHERE id = ?",
            (generate_password_hash(DEMO_ADMIN['password'], method='scrypt'),
             DEMO_ADMIN['full_name'], DEMO_ADMIN['username'], admin_id)
        )
        conn.commit()
        print(f"      Demo admin '{DEMO_ADMIN['full_name']}' verified (User ID: {admin_id}).")
    else:
        cursor.execute(
            "INSERT INTO users (full_name, email, username, password_hash, role, avatar) VALUES (?, ?, ?, ?, ?, ?)",
            (DEMO_ADMIN['full_name'], DEMO_ADMIN['email'], DEMO_ADMIN['username'],
             generate_password_hash(DEMO_ADMIN['password'], method='scrypt'),
             DEMO_ADMIN['role'], DEMO_ADMIN['avatar'])
        )
        conn.commit()
        admin_id = cursor.lastrowid
        print(f"      Created demo admin '{DEMO_ADMIN['full_name']}' (User ID: {admin_id}).")
        
    # 2. Seed realistic sample history records
    upload_dir = Config.UPLOAD_FOLDER
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Check existing records for this user
    cursor.execute("SELECT COUNT(*) as count FROM analysis_records WHERE user_id = ?", (user_id,))
    existing_records_count = cursor.fetchone()['count']
    
    dataset_images = list(Path("dataset/images").glob("*.jpg"))
    for idx, rec in enumerate(SAMPLE_RECORDS):
        cursor.execute("SELECT id FROM analysis_records WHERE user_id = ? AND original_filename = ?", (user_id, rec['title']))
        existing = cursor.fetchone()
        
        stored_filename = f"demo_bhavi_sample_{idx+1}.jpg"
        dest_image_path = upload_dir / stored_filename
        
        # Copy real image from dataset/images if available, or generate clean fallback
        if idx < len(dataset_images) and dataset_images[idx].exists():
            shutil.copy(dataset_images[idx], dest_image_path)
        elif not dest_image_path.exists():
            from PIL import Image, ImageDraw
            img = Image.new('RGB', (256, 256), color=(235, 215, 195))
            d = ImageDraw.Draw(img)
            d.ellipse([70, 70, 185, 185], fill=(120, 75, 55), outline=(70, 40, 30), width=3)
            img.save(dest_image_path)
            
        file_size = dest_image_path.stat().st_size if dest_image_path.exists() else 10240
        
        if existing:
            cursor.execute("""
                UPDATE analysis_records 
                SET lesion_metadata = ?, confidence_score = ?, classification = ?, explanation = ?
                WHERE id = ?
            """, (json.dumps(rec['metadata']), rec['confidence_score'], rec['classification'], rec['explanation'], existing['id']))
            print(f"  Updated existing sample record ID {existing['id']}: {rec['classification']}")
        else:
            cursor.execute("""
                INSERT INTO analysis_records (
                    user_id, original_filename, stored_filename, file_path, file_size,
                    result_status, classification, confidence_score, explanation,
                    is_demo, model_version, lesion_metadata, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, rec['title'], stored_filename, str(dest_image_path), file_size,
                rec['result_status'], rec['classification'], rec['confidence_score'],
                rec['explanation'], rec['is_demo'], 'HAM10000-Benchmark-Study-Reference',
                json.dumps(rec['metadata']), rec['created_at']
            ))
            print(f"  Added sample history record: {rec['classification']}")
        
    conn.commit()
    print("Preloaded sample records synchronized successfully.")
        
    conn.close()
    print("\n" + "="*70)
    print(" DEMO ACCOUNTS CREATED & READY FOR PRESENTATION")
    print("="*70)
    print(f" Demo Member:  {DEMO_USER['full_name']}")
    print(f" Email:        {DEMO_USER['email']}")
    print(f" Username:     {DEMO_USER['username']}")
    print(f" Password:     {DEMO_USER['password']}")
    print(f" Role:         {DEMO_USER['role']}")
    print("-" * 70)
    print(f" Administrator:{DEMO_ADMIN['full_name']}")
    print(f" Email:        {DEMO_ADMIN['email']}")
    print(f" Username:     {DEMO_ADMIN['username']}")
    print(f" Password:     {DEMO_ADMIN['password']}")
    print(f" Role:         {DEMO_ADMIN['role']}")
    print("="*70)

if __name__ == '__main__':
    seed_demo_member()
