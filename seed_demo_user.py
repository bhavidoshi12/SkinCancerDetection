"""
Seed Script: Pre-registered Demo Accounts (Bhavi Doshi, Vidisha Ajmera, System Administrator)
Creates the official demo accounts, realistic preloaded sample history records,
and synchronized patient medical profiles for the Software Engineering project demonstration.
"""

import os
import shutil
import sqlite3
import json
from pathlib import Path
from werkzeug.security import generate_password_hash
from config import Config
from database.db import get_db_connection, init_db, upsert_patient_medical_profile, admin_update_patient_profile
from services.pdf_service import save_screening_report_pdf

DEMO_USERS = [
    {
        'full_name': 'Bhavi Doshi',
        'email': 'bhavidoshi12@gmail.com',
        'username': 'bhavi12',
        'password': 'Bhavi@2026!',
        'role': 'patient',
        'avatar': 'avatar_bhavi.png',
        'medical_profile': {
            'medical_history': '[DEMO / SAMPLE RECORD] Routine skin screening evaluation. No personal or first-degree family history of melanoma. Routine SPF 50 sunscreen application.',
            'skin_concerns': '[DEMO / SAMPLE RECORD] Voluntary self-monitoring of common pigmented moles (ABCDE tracking).',
            'allergies': 'None documented.',
            'sun_exposure_level': 'Moderate',
            'fitzpatrick_skin_type': 'Type III',
            'family_history_skin_cancer': 'None',
            'phone': '+91 98200 12345',
            'emergency_contact': 'Dr. K. Doshi (Family Physician): +91 98200 54321',
            'verification_status': 'Verified by Physician',
            'admin_notes': 'Documented for academic Software Engineering viva demonstration.'
        }
    },
    {
        'full_name': 'Vidisha Ajmera',
        'email': 'vidisha.ajmera@dermacare.ai',
        'username': 'vidisha_ajmera',
        'password': 'Vidisha@2026!',
        'role': 'patient',
        'avatar': '',
        'medical_profile': {
            'medical_history': '[DEMO / SAMPLE RECORD] Voluntary self-report: Family history of melanoma (maternal grandfather), high sun exposure during outdoor sports, Fitzpatrick Skin Type II. Mild seasonal eczema.',
            'skin_concerns': '[DEMO / SAMPLE RECORD] Noticed a slightly asymmetrical pigmented lesion on upper back; seeks dermatologist screening.',
            'allergies': 'Penicillin; contact dermatitis to latex.',
            'sun_exposure_level': 'High (Outdoor Sports)',
            'fitzpatrick_skin_type': 'Type II',
            'family_history_skin_cancer': 'Melanoma (Maternal Grandfather)',
            'phone': '+91 98111 67890',
            'emergency_contact': 'S. Ajmera (Parent): +91 98111 09876',
            'verification_status': 'Follow-up Recommended',
            'admin_notes': 'Clinical follow-up scheduled with attending dermatologist.'
        }
    }
]

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

def seed_demo_members():
    print("[1/4] Ensuring database schema and tables are initialized...")
    init_db()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Ensure dedicated storage directories exist
    Config.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    Config.PATIENT_IMAGES_FOLDER.mkdir(parents=True, exist_ok=True)
    Config.REPORTS_FOLDER.mkdir(parents=True, exist_ok=True)
    
    # 1. Create or retrieve demo admin
    cursor.execute("SELECT id FROM users WHERE email = ? OR username = ?", (DEMO_ADMIN['email'], DEMO_ADMIN['username']))
    admin_row = cursor.fetchone()
    if admin_row:
        admin_id = admin_row['id']
        cursor.execute(
            "UPDATE users SET password_hash = ?, full_name = ?, username = ?, role = 'admin', updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (generate_password_hash(DEMO_ADMIN['password'], method='scrypt'),
             DEMO_ADMIN['full_name'], DEMO_ADMIN['username'], admin_id)
        )
        conn.commit()
        print(f"[2/4] Verified demo admin '{DEMO_ADMIN['full_name']}' (User ID: {admin_id}).")
    else:
        cursor.execute(
            "INSERT INTO users (full_name, email, username, password_hash, role, avatar) VALUES (?, ?, ?, ?, ?, ?)",
            (DEMO_ADMIN['full_name'], DEMO_ADMIN['email'], DEMO_ADMIN['username'],
             generate_password_hash(DEMO_ADMIN['password'], method='scrypt'),
             DEMO_ADMIN['role'], DEMO_ADMIN['avatar'])
        )
        conn.commit()
        admin_id = cursor.lastrowid
        print(f"[2/4] Created demo admin '{DEMO_ADMIN['full_name']}' (User ID: {admin_id}).")

    # 2. Seed Patient Accounts
    dataset_images = list(Path("dataset/images").glob("*.jpg"))
    for user_info in DEMO_USERS:
        cursor.execute("SELECT id FROM users WHERE email = ? OR username = ?", (user_info['email'], user_info['username']))
        user_row = cursor.fetchone()
        
        if user_row:
            u_id = user_row['id']
            cursor.execute(
                "UPDATE users SET password_hash = ?, full_name = ?, username = ?, avatar = ?, role = 'patient', updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (generate_password_hash(user_info['password'], method='scrypt'),
                 user_info['full_name'], user_info['username'], user_info['avatar'], u_id)
            )
            conn.commit()
            print(f"[3/4] Verified patient '{user_info['full_name']}' (User ID: {u_id}).")
        else:
            cursor.execute(
                "INSERT INTO users (full_name, email, username, password_hash, role, avatar) VALUES (?, ?, ?, ?, ?, ?)",
                (user_info['full_name'], user_info['email'], user_info['username'],
                 generate_password_hash(user_info['password'], method='scrypt'),
                 user_info['role'], user_info['avatar'])
            )
            conn.commit()
            u_id = cursor.lastrowid
            print(f"[3/4] Created patient '{user_info['full_name']}' (User ID: {u_id}).")
            
        # Synchronize patient medical profile
        med = user_info['medical_profile']
        upsert_patient_medical_profile(
            user_id=u_id,
            medical_history=med['medical_history'],
            skin_concerns=med['skin_concerns'],
            allergies=med['allergies'],
            sun_exposure_level=med['sun_exposure_level'],
            fitzpatrick_skin_type=med['fitzpatrick_skin_type'],
            family_history_skin_cancer=med['family_history_skin_cancer'],
            phone=med['phone'],
            emergency_contact=med['emergency_contact']
        )
        admin_update_patient_profile(
            user_id=u_id,
            admin_id=admin_id,
            verification_status=med['verification_status'],
            admin_notes=med['admin_notes']
        )
        
        # Seed realistic benchmark sample records for Bhavi Doshi and Vidisha Ajmera
        sample_subset = SAMPLE_RECORDS[:3] if user_info['username'] == 'vidisha_ajmera' else SAMPLE_RECORDS
        for idx, rec in enumerate(sample_subset):
            cursor.execute("SELECT id FROM analysis_records WHERE user_id = ? AND original_filename = ?", (u_id, rec['title']))
            existing = cursor.fetchone()
            
            stored_filename = f"demo_{user_info['username']}_sample_{idx+1}.jpg"
            dest_image_path = Config.PATIENT_IMAGES_FOLDER / stored_filename
            
            if idx < len(dataset_images) and dataset_images[idx].exists():
                shutil.copy(dataset_images[idx], dest_image_path)
            elif not dest_image_path.exists():
                from PIL import Image, ImageDraw
                img = Image.new('RGB', (256, 256), color=(235, 215, 195))
                d = ImageDraw.Draw(img)
                d.ellipse([70, 70, 185, 185], fill=(120, 75, 55), outline=(70, 40, 30), width=3)
                img.save(dest_image_path)
                
            file_size = dest_image_path.stat().st_size if dest_image_path.exists() else 10240
            rel_report_path = f"uploads/reports/report_record_{u_id}_{idx+1}.pdf"
            
            if existing:
                cursor.execute("""
                    UPDATE analysis_records 
                    SET lesion_metadata = ?, confidence_score = ?, classification = ?, explanation = ?,
                        file_path = ?, stored_filename = ?, is_demo = 1, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (json.dumps(rec['metadata']), rec['confidence_score'], rec['classification'], rec['explanation'],
                      str(dest_image_path), stored_filename, existing['id']))
            else:
                cursor.execute("""
                    INSERT INTO analysis_records (
                        user_id, original_filename, stored_filename, file_path, file_size,
                        result_status, classification, confidence_score, explanation,
                        is_demo, model_version, lesion_metadata, pdf_report_path, symptoms_noted,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    u_id, rec['title'], stored_filename, str(dest_image_path), file_size,
                    rec['result_status'], rec['classification'], rec['confidence_score'],
                    rec['explanation'], rec['is_demo'], 'HAM10000-Benchmark-Study-Reference',
                    json.dumps(rec['metadata']), rel_report_path, med['skin_concerns'], rec['created_at']
                ))
                
        conn.commit()

    conn.close()
    print("[4/4] Preloaded clinical records and medical profiles synchronized successfully.")
    print("\n" + "="*70)
    print(" DEMO ACCOUNTS READY & SYNCHRONIZED WITH BACKEND DATABASE")
    print("="*70)
    for u in DEMO_USERS:
        print(f" Patient:      {u['full_name']}")
        print(f" Email:        {u['email']}")
        print(f" Username:     {u['username']}")
        print(f" Password:     {u['password']}")
        print(f" Role:         {u['role']}")
        print("-" * 70)
    print(f" Administrator:{DEMO_ADMIN['full_name']}")
    print(f" Email:        {DEMO_ADMIN['email']}")
    print(f" Username:     {DEMO_ADMIN['username']}")
    print(f" Password:     {DEMO_ADMIN['password']}")
    print(f" Role:         {DEMO_ADMIN['role']}")
    print("="*70)

if __name__ == '__main__':
    seed_demo_members()
