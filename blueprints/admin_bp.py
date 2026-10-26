import os
import sys
import io
import csv
import platform
from datetime import datetime
from pathlib import Path
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, abort
from config import Config
from services.auth_service import admin_required, get_current_user
from database.db import (
    get_admin_system_stats, get_all_users_summary, get_recent_global_records,
    search_patients, get_patient_full_details, admin_update_patient_profile,
    get_all_audit_logs, get_patient_medical_profile
)
from services.model_service import check_model_availability, CLASS_FULL_NAMES, HAM10000_CLASSES_7

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def sanitize_csv_cell(value):
    """
    Prevents CSV / Spreadsheet Formula Injection (CWE-1236).
    Prepends a single quote if the string begins with =, +, -, @, tab, or carriage return.
    """
    if value is None:
        return ""
    text = str(value).strip()
    if text and text[0] in ('=', '+', '-', '@', '\t', '\r'):
        return "'" + text
    return text

@admin_bp.route('', strict_slashes=False)
@admin_bp.route('/', strict_slashes=False)
@admin_bp.route('/dashboard', strict_slashes=False)
@admin_required
def dashboard():
    search_query = request.args.get('q', '').strip()
    stats = get_admin_system_stats()
    patients = search_patients(search_query)
    recent_records = get_recent_global_records(limit=25)
    model_status = check_model_availability()
    recent_audits = get_all_audit_logs(limit=10)
    
    # Calculate model file size if present
    model_file_size_mb = 0.0
    if Config.MODEL_PATH.exists():
        try:
            model_file_size_mb = round(Config.MODEL_PATH.stat().st_size / (1024 * 1024), 2)
        except Exception:
            model_file_size_mb = 0.0

    telemetry = {
        'python_version': platform.python_version(),
        'platform': platform.platform(),
        'model_path': str(Config.MODEL_PATH),
        'model_size_mb': model_file_size_mb,
        'model_loaded': model_status.get('is_available', False),
        'model_architecture': 'MobileNetV2 Transfer Learning Architecture',
        'classes_count': len(CLASS_FULL_NAMES),
        'classes_list': list(CLASS_FULL_NAMES.values()),
        'database_path': str(Config.DATABASE_PATH),
        'upload_folder': str(Config.UPLOAD_FOLDER)
    }

    return render_template(
        'admin/dashboard.html',
        stats=stats,
        users=patients,
        search_query=search_query,
        recent_records=recent_records,
        model_status=model_status,
        telemetry=telemetry,
        recent_audits=recent_audits
    )

@admin_bp.route('/patient/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def patient_detail(user_id):
    """
    Administrator view of synchronized patient medical details, history, uploaded images, and reports.
    Permits authorized administrative updates to verification status and clinical notes.
    """
    current_admin = get_current_user()
    patient_data = get_patient_full_details(user_id)
    if not patient_data:
        flash(f"Patient record #{user_id} was not found in the database.", "danger")
        return redirect(url_for('admin.dashboard'))
        
    if request.method == 'POST':
        verification_status = request.form.get('verification_status', 'Unverified').strip()
        admin_notes = request.form.get('admin_notes', '').strip()
        phone = request.form.get('phone', '').strip()
        emergency_contact = request.form.get('emergency_contact', '').strip()
        
        # Validate verification status choices
        valid_statuses = {'Unverified', 'Pending Review', 'Verified by Physician', 'Follow-up Recommended'}
        if verification_status not in valid_statuses:
            verification_status = 'Unverified'
            
        admin_update_patient_profile(
            user_id=user_id,
            admin_id=current_admin['id'],
            verification_status=verification_status,
            admin_notes=admin_notes,
            phone=phone,
            emergency_contact=emergency_contact
        )
        
        flash("Authorized patient updates have been saved and synchronized to the backend database.", "success")
        return redirect(url_for('admin.patient_detail', user_id=user_id))
        
    return render_template(
        'admin/patient_detail.html',
        patient=patient_data['user'],
        profile=patient_data['profile'],
        records=patient_data['records'],
        stats=patient_data['stats'],
        audit_logs=patient_data['audit_logs']
    )

@admin_bp.route('/export-patients-csv')
@admin_required
def export_patients_csv():
    """
    Authorized Administrator-only CSV export of patient records.
    Applies formula-injection defense and strictly authorized fields.
    """
    patients = search_patients()
    output = io.StringIO()
    writer = csv.writer(output)
    
    headers = [
        'Patient ID',
        'Full Name',
        'Email Address',
        'Username',
        'Role',
        'Verification Status',
        'Total Scans',
        'Skin Concerns',
        'Self-Reported Medical History',
        'Allergies',
        'Sun Exposure Level',
        'Fitzpatrick Skin Type',
        'Family Cancer History',
        'Phone',
        'Emergency Contact',
        'Clinical Admin Notes',
        'Account Registered',
        'Profile Last Updated'
    ]
    writer.writerow(headers)
    
    for p in patients:
        writer.writerow([
            sanitize_csv_cell(p['id']),
            sanitize_csv_cell(p['full_name']),
            sanitize_csv_cell(p['email']),
            sanitize_csv_cell(p['username'] or ''),
            sanitize_csv_cell(p['role']),
            sanitize_csv_cell(p['verification_status'] or 'Unverified'),
            sanitize_csv_cell(p['analysis_count']),
            sanitize_csv_cell(p['skin_concerns'] or ''),
            sanitize_csv_cell(p['medical_history'] or ''),
            sanitize_csv_cell(p['allergies'] or ''),
            sanitize_csv_cell(p['sun_exposure_level'] or 'Moderate'),
            sanitize_csv_cell(p['fitzpatrick_skin_type'] or 'Type II'),
            sanitize_csv_cell(p['family_history_skin_cancer'] or 'None'),
            sanitize_csv_cell(p['patient_phone'] or ''),
            sanitize_csv_cell(p['emergency_contact'] or ''),
            sanitize_csv_cell(p['admin_notes'] or ''),
            sanitize_csv_cell(p['created_at'][:19] if p['created_at'] else ''),
            sanitize_csv_cell(p['profile_updated_at'][:19] if p['profile_updated_at'] else '')
        ])
        
    output.seek(0)
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"DermaCare_Patient_Records_{timestamp_str}.csv"
    
    return Response(
        output.getvalue().encode('utf-8-sig'),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )
