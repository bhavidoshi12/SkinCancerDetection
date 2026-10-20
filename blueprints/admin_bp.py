import os
import sys
import platform
from pathlib import Path
from flask import Blueprint, render_template, request, redirect, url_for, flash
from config import Config
from services.auth_service import admin_required, get_current_user
from database.db import get_admin_system_stats, get_all_users_summary, get_recent_global_records
from services.model_service import check_model_availability, CLASS_FULL_NAMES, HAM10000_CLASSES_7

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('', strict_slashes=False)
@admin_bp.route('/', strict_slashes=False)
@admin_bp.route('/dashboard', strict_slashes=False)
@admin_required
def dashboard():
    stats = get_admin_system_stats()
    users = get_all_users_summary()
    recent_records = get_recent_global_records(limit=25)
    model_status = check_model_availability()
    
    # Calculate model file size if present
    model_file_size_mb = 0.0
    if Config.MODEL_PATH.exists():
        try:
            model_file_size_mb = round(Config.MODEL_PATH.stat().st_size / (1024 * 1024), 2)
        except Exception:
            model_file_size_mb = 0.0

    # System telemetry
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
        users=users,
        recent_records=recent_records,
        model_status=model_status,
        telemetry=telemetry
    )
