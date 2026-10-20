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
from services.pdf_service import generate_screening_report_pdf
from database.db import (
    create_analysis_record, get_user_analysis_records,
    get_analysis_record_by_id, get_user_analysis_stats, get_db_connection
)
from config import Config

analysis_bp = Blueprint('analysis', __name__, url_prefix='')

@analysis_bp.route('/dashboard')
@login_required
def dashboard():
    user = get_current_user()
    stats = get_user_analysis_stats(user['id'])
    recent_records = get_user_analysis_records(user['id'], limit=5)
    model_status = check_model_availability()
    samples = get_educational_sample_records()
    
    return render_template(
        'dashboard.html',
        user=user,
        stats=stats,
        recent_records=recent_records,
        model_status=model_status,
        samples=samples
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
        
    # Generate unique stored filename
    ext = file.filename.rsplit('.', 1)[-1].lower()
    unique_filename = f"user_{user['id']}_{uuid.uuid4().hex[:12]}.{ext}"
    upload_dir = Path(current_app.config.get('UPLOAD_FOLDER', Config.UPLOAD_FOLDER))
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / unique_filename
    
    # Save the verified image
    try:
        image_obj.save(str(file_path))
        file_size = os.path.getsize(file_path)
    except Exception as e:
        flash("Failed to securely store the uploaded image. Please try again.", "danger")
        return redirect(url_for('analysis.upload'))
        
    # Perform analysis (Genuine ML or honest transparent demo mode)
    force_demo = request.form.get('force_demo') == '1'
    analysis_result = analyze_skin_lesion(image_obj, metadata, force_demo=force_demo)
    
    if analysis_result.get('all_class_scores'):
        metadata['all_class_scores'] = analysis_result['all_class_scores']
    
    # Persist record in database
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
        lesion_metadata=metadata
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

@analysis_bp.route('/report/<int:record_id>/download')
@login_required
def download_report(record_id):
    """
    Generates and downloads a clinical screening report PDF.
    Enforces strict user isolation: Users can ONLY download their own reports!
    """
    user = get_current_user()
    record = get_analysis_record_by_id(record_id, user_id=user['id'])
    
    if not record:
        abort(403)  # Forbidden if record belongs to someone else or does not exist
        
    pdf_buffer = io.BytesIO()
    generate_screening_report_pdf(record, user, pdf_buffer)
    pdf_buffer.seek(0)
    
    safe_filename = f"Skin_Cancer_Screening_Report_RPT_{record['id']:05d}.pdf"
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=safe_filename,
        mimetype='application/pdf'
    )

@analysis_bp.route('/protected-uploads/<filename>')
@login_required
def serve_upload(filename):
    """
    Secure file endpoint ensuring uploads are not exposed to unauthorized users or search engines.
    """
    user = get_current_user()
    # Check if this filename belongs to a record of the authenticated user
    conn = get_db_connection()
    row = conn.execute(
        "SELECT id FROM analysis_records WHERE stored_filename = ? AND user_id = ?",
        (filename, user['id'])
    ).fetchone()
    conn.close()
    
    if not row:
        abort(403)
        
    upload_folder = Path(current_app.config.get('UPLOAD_FOLDER', Config.UPLOAD_FOLDER))
    file_path = upload_folder / filename
    if not file_path.exists():
        abort(404)
        
    return send_file(str(file_path))
