import os
import uuid
import io
import json
from pathlib import Path
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash,
    session, send_file, abort, current_app
)
from services.auth_service import login_required, get_current_user
from services.model_service import (
    validate_and_inspect_image, analyze_skin_lesion,
    check_model_availability, get_educational_sample_records
)
from services.pdf_service import generate_screening_report_pdf, save_screening_report_pdf
from database.db import (
    create_analysis_record, get_user_analysis_records,
    get_analysis_record_by_id, get_user_analysis_stats, get_db_connection,
    get_patient_medical_profile, upsert_patient_medical_profile, get_user_by_id
)
from config import Config

analysis_bp = Blueprint('analysis', __name__, url_prefix='')

@analysis_bp.route('/dashboard')
@login_required
def dashboard():
    user = get_current_user()
    stats = get_user_analysis_stats(user['id'])
    recent_records = get_user_analysis_records(user['id'], limit=10)
    model_status = check_model_availability()
    samples = get_educational_sample_records()
    patient_profile = get_patient_medical_profile(user['id'])
    
    return render_template(
        'dashboard.html',
        user=user,
        stats=stats,
        recent_records=recent_records,
        model_status=model_status,
        samples=samples,
        profile=patient_profile
    )

@analysis_bp.route('/upload')
@login_required
def upload():
    model_status = check_model_availability()
    samples = get_educational_sample_records()
    return render_template('upload.html', model_status=model_status, samples=samples)

@analysis_bp.route('/analyze', methods=['POST'])
@login_required
def analyze():
    user = get_current_user()
    
    if 'image' not in request.files:
        flash("No file was uploaded. Please choose an image to analyze.", "danger")
        return redirect(url_for('analysis.upload'))
        
    file = request.files['image']
    if not file or file.filename == '':
        flash("No image file was selected. Please select a valid JPG, JPEG, or PNG file.", "danger")
        return redirect(url_for('analysis.upload'))
        
    # Backend strict file validation (independent of frontend validation)
    is_valid, error_msg, image_obj, metadata = validate_and_inspect_image(file.stream, file.filename)
    if not is_valid:
        flash(f"Upload rejected: {error_msg}", "danger")
        return redirect(url_for('analysis.upload'))
        
    # Generate unique stored filename in dedicated patient_images directory
    ext = file.filename.rsplit('.', 1)[-1].lower()
    unique_filename = f"user_{user['id']}_{uuid.uuid4().hex[:12]}.{ext}"
    patient_images_dir = Path(current_app.config.get('PATIENT_IMAGES_FOLDER', Config.PATIENT_IMAGES_FOLDER))
    patient_images_dir.mkdir(parents=True, exist_ok=True)
    file_path = patient_images_dir / unique_filename
    
    # Save the verified image
    try:
        image_obj.save(str(file_path))
        file_size = os.path.getsize(file_path)
    except Exception as e:
        flash("Failed to securely store the uploaded image. Please try again.", "danger")
        return redirect(url_for('analysis.upload'))
        
    # Capture optional symptoms voluntarily noted by patient
    symptoms_noted = request.form.get('symptoms', '').strip()

    # Perform analysis (Genuine ML or honest transparent demo mode)
    force_demo = request.form.get('force_demo') == '1'
    analysis_result = analyze_skin_lesion(image_obj, metadata, force_demo=force_demo)
    
    if analysis_result.get('all_class_scores'):
        metadata['all_class_scores'] = analysis_result['all_class_scores']
    
    # Persist record in backend database
    record_id = create_analysis_record(
        user_id=user['id'],
        original_filename=file.filename,
        stored_filename=unique_filename,
        file_path=str(file_path),
        file_size=file_size,
        result_status=analysis_result['result_status'],
        classification=analysis_result['classification'],
        confidence_score=analysis_result['confidence_score'],
        explanation=analysis_result['explanation'],
        is_demo=analysis_result['is_demo'],
        model_version=analysis_result['model_version'],
        lesion_metadata=metadata,
        symptoms_noted=symptoms_noted
    )
    
    flash("Image processed successfully.", "success")
    return redirect(url_for('analysis.view_result', record_id=record_id))

@analysis_bp.route('/sample-analysis', methods=['POST'])
@login_required
def sample_analysis():
    """
    Simulates testing with a verified HAM10000 reference case study for educational demonstration.
    """
    user = get_current_user()
    sample_id = request.form.get('sample_id', 'HAM_BENIGN_01')
    samples = get_educational_sample_records()
    chosen = next((s for s in samples if s['sample_id'] == sample_id), samples[0])
    
    upload_dir = Path(current_app.config.get('UPLOAD_FOLDER', Config.UPLOAD_FOLDER))
    upload_dir.mkdir(parents=True, exist_ok=True)
    sample_filename = f"sample_{sample_id.lower()}.png"
    sample_path = upload_dir / sample_filename
    
    if not sample_path.exists():
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (224, 224), color=(230, 205, 185))
        d = ImageDraw.Draw(img)
        # Draw simulated lesion
        if 'BENIGN' in sample_id:
            d.ellipse([70, 70, 150, 150], fill=(120, 80, 60), outline=(90, 60, 45), width=2)
        else:
            d.polygon([(60, 75), (140, 60), (165, 130), (120, 170), (70, 140)], fill=(70, 45, 40), outline=(40, 20, 20))
        img.save(str(sample_path))
        
    metadata = {
        'width': 224,
        'height': 224,
        'aspect_ratio': 1.0,
        'avg_brightness': 160.0,
        'contrast_metric': 35.5,
        'channels': 3,
        'format': 'PNG',
        'is_reference_sample': True
    }
    
    record_id = create_analysis_record(
        user_id=user['id'],
        original_filename=f"{chosen['title']}.png",
        stored_filename=sample_filename,
        file_path=str(sample_path),
        file_size=os.path.getsize(sample_path),
        result_status=chosen['result_status'],
        classification=chosen['classification'],
        confidence_score=chosen['confidence_score'],
        explanation=chosen['explanation'],
        is_demo=chosen['is_demo'],
        model_version='HAM10000-Benchmark-Study-Reference',
        lesion_metadata=metadata
    )
    
    flash("Educational reference case loaded for workflow demonstration.", "info")
    return redirect(url_for('analysis.view_result', record_id=record_id))

@analysis_bp.route('/results/<int:record_id>')
@login_required
def view_result(record_id):
    user = get_current_user()
    record = get_analysis_record_by_id(record_id, user_id=user['id'])
    if not record:
        flash("Record not found or access denied.", "danger")
        return redirect(url_for('analysis.dashboard'))
        
    metadata = {}
    if record['lesion_metadata']:
        try:
            metadata = json.loads(record['lesion_metadata'])
        except Exception:
            pass
            
    return render_template('results.html', record=record, metadata=metadata, user=user)

@analysis_bp.route('/history')
@login_required
def history():
    user = get_current_user()
    status_filter = request.args.get('status', 'all')
    search_query = request.args.get('q', '').strip()
    
    records = get_user_analysis_records(
        user_id=user['id'],
        status_filter=status_filter,
        search_query=search_query
    )
    return render_template(
        'history.html',
        records=records,
        status_filter=status_filter,
        search_query=search_query,
        user=user
    )

@analysis_bp.route('/record/<int:record_id>')
@login_required
def record_detail(record_id):
    user = get_current_user()
    record = get_analysis_record_by_id(record_id, user_id=user['id'])
    if not record:
        flash("Record not found or access denied.", "danger")
        return redirect(url_for('analysis.history'))
        
    metadata = {}
    if record['lesion_metadata']:
        try:
            metadata = json.loads(record['lesion_metadata'])
        except Exception:
            pass
            
    return render_template('record_detail.html', record=record, metadata=metadata, user=user)

@analysis_bp.route('/report/<int:record_id>')
@analysis_bp.route('/report/<int:record_id>/download')
@login_required
def download_report(record_id):
    """
    Generates, stores, and downloads a clinical screening report PDF.
    Enforces authorization: Patients can only download their own reports;
    administrators can download reports according to administrative permissions.
    """
    current_u = get_current_user()
    is_admin = session.get('user_role') == 'admin'
    
    if is_admin:
        record = get_analysis_record_by_id(record_id)
    else:
        record = get_analysis_record_by_id(record_id, user_id=current_u['id'])
        
    if not record:
        abort(403)
        
    target_user = get_user_by_id(record['user_id']) or current_u
    
    try:
        report_file, rel_path = save_screening_report_pdf(record, target_user)
        safe_filename = f"Skin_Cancer_Screening_Report_RPT_{record['id']:05d}.pdf"
        return send_file(
            str(report_file),
            as_attachment=True,
            download_name=safe_filename,
            mimetype='application/pdf'
        )
    except Exception:
        pdf_buffer = io.BytesIO()
        generate_screening_report_pdf(record, target_user, pdf_buffer)
        pdf_buffer.seek(0)
        safe_filename = f"Skin_Cancer_Screening_Report_RPT_{record['id']:05d}.pdf"
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=safe_filename,
            mimetype='application/pdf'
        )

@analysis_bp.route('/patient/medical-profile/update', methods=['POST'])
@login_required
def update_patient_medical_profile_view():
    """
    Saves patient-provided medical history, skin concerns, and allergies to the backend database.
    Immediately synchronized with both patient and administrator dashboards.
    """
    user = get_current_user()
    
    medical_history = request.form.get('medical_history', '').strip()
    skin_concerns = request.form.get('skin_concerns', '').strip()
    allergies = request.form.get('allergies', '').strip()
    sun_exposure_level = request.form.get('sun_exposure_level', 'Moderate').strip()
    fitzpatrick_skin_type = request.form.get('fitzpatrick_skin_type', 'Type II').strip()
    family_history_skin_cancer = request.form.get('family_history_skin_cancer', 'None').strip()
    phone = request.form.get('phone', '').strip()
    emergency_contact = request.form.get('emergency_contact', '').strip()
    
    upsert_patient_medical_profile(
        user_id=user['id'],
        medical_history=medical_history,
        skin_concerns=skin_concerns,
        allergies=allergies,
        sun_exposure_level=sun_exposure_level,
        fitzpatrick_skin_type=fitzpatrick_skin_type,
        family_history_skin_cancer=family_history_skin_cancer,
        phone=phone,
        emergency_contact=emergency_contact
    )
    
    flash("Your personal medical history and skin concerns have been saved to the backend database.", "success")
    return redirect(url_for('analysis.dashboard'))

@analysis_bp.route('/protected-uploads/<path:filename>')
@analysis_bp.route('/uploads/<path:filename>')
@login_required
def serve_upload(filename):
    """
    Secure file endpoint ensuring uploads are not exposed to unauthorized users.
    Patients can only view their own images; admins can view according to permissions.
    """
    current_u = get_current_user()
    is_admin = session.get('user_role') == 'admin'
    base_name = os.path.basename(filename)
    
    conn = get_db_connection()
    if is_admin:
        row = conn.execute(
            "SELECT id FROM analysis_records WHERE stored_filename = ? OR stored_filename LIKE ?",
            (base_name, f"%{base_name}")
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT id FROM analysis_records WHERE (stored_filename = ? OR stored_filename LIKE ?) AND user_id = ?",
            (base_name, f"%{base_name}", current_u['id'])
        ).fetchone()
    conn.close()
    
    is_sample = base_name.startswith('demo_') or base_name.startswith('sample_') or 'ISIC' in base_name
    if not row and not is_sample:
        abort(403)
        
    upload_root = Path(current_app.config.get('UPLOAD_FOLDER', Config.UPLOAD_FOLDER))
    candidates = [
        Path(current_app.config.get('PATIENT_IMAGES_FOLDER', Config.PATIENT_IMAGES_FOLDER)) / base_name,
        Path(current_app.config.get('REPORTS_FOLDER', Config.REPORTS_FOLDER)) / base_name,
        upload_root / base_name,
        upload_root / filename
    ]
    for c in candidates:
        if c.exists() and c.is_file():
            return send_file(str(c))
            
    abort(404)
