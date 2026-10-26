import sqlite3
import json

conn = sqlite3.connect('instance/skin_cancer.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=" * 60)
print("1. DATABASE TABLES FOUND")
print("=" * 60)
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [row['name'] for row in cursor.fetchall()]
for t in tables:
    cursor.execute(f"SELECT COUNT(*) as cnt FROM {t}")
    cnt = cursor.fetchone()['cnt']
    print(f" - {t:<28} ({cnt} rows)")

print("\n" + "=" * 60)
print("2. REGISTERED USERS (`users` table)")
print("=" * 60)
cursor.execute("SELECT id, full_name, email, username, role, phone, created_at FROM users")
for u in cursor.fetchall():
    print(f"ID #{u['id']:<2} | {u['full_name']:<22} | {u['email']:<28} | Role: {u['role']:<10} | @{u['username'] or '—'}")

print("\n" + "=" * 60)
print("3. SYNCHRONIZED MEDICAL PROFILES (`patient_medical_profiles` table)")
print("=" * 60)
cursor.execute("""
    SELECT p.user_id, u.full_name, p.verification_status, p.fitzpatrick_skin_type, 
           p.sun_exposure_level, p.skin_concerns, p.medical_history, p.admin_notes
    FROM patient_medical_profiles p
    JOIN users u ON u.id = p.user_id
""")
for p in cursor.fetchall():
    print(f"\n[Patient #{p['user_id']} — {p['full_name']}] Status: {p['verification_status']}")
    print(f"  • Skin Concerns:   {p['skin_concerns']}")
    print(f"  • Medical History: {p['medical_history']}")
    print(f"  • Fitzpatrick:     {p['fitzpatrick_skin_type']} | Sun: {p['sun_exposure_level']}")
    if p['admin_notes']:
        print(f"  • Physician Notes: {p['admin_notes']}")

print("\n" + "=" * 60)
print("4. LESION ANALYSIS RECORDS (`analysis_records` table)")
print("=" * 60)
cursor.execute("""
    SELECT a.id, a.user_id, u.full_name, a.original_filename, a.classification, 
           a.confidence_score, a.is_demo, a.symptoms_noted, a.pdf_report_path
    FROM analysis_records a
    LEFT JOIN users u ON u.id = a.user_id
    ORDER BY a.id
""")
for r in cursor.fetchall():
    score = f"{r['confidence_score']:.1f}%" if r['confidence_score'] is not None else "N/A (Demo)"
    mode = "Demo Record" if r['is_demo'] else "Genuine DL"
    print(f"Scan #{r['id']} | Patient: {r['full_name']} | File: {r['original_filename']}")
    print(f"   Finding: {r['classification']} ({score}) [{mode}]")
    if r['symptoms_noted']:
        print(f"   Symptoms: {r['symptoms_noted']}")
    if r['pdf_report_path']:
        print(f"   Report PDF: {r['pdf_report_path']}")

print("\n" + "=" * 60)
print("5. CLINICAL AUDIT TRAIL (`audit_logs` table)")
print("=" * 60)
cursor.execute("SELECT id, record_type, record_id, action, timestamp, details FROM audit_logs")
audits = cursor.fetchall()
if audits:
    for a in audits:
        print(f"Audit #{a['id']} [{a['timestamp']}] {a['action']} on {a['record_type']} #{a['record_id']}: {a['details']}")
else:
    print("No audit logs yet.")

conn.close()
