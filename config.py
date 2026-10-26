import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    BASE_DIR = BASE_DIR
    SECRET_KEY = os.environ.get('SECRET_KEY', 'nmims-se-skin-cancer-detection-secret-key-2026')
    DATABASE_PATH = BASE_DIR / 'instance' / 'skin_cancer.db'
    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    PATIENT_IMAGES_FOLDER = UPLOAD_FOLDER / 'patient_images'
    REPORTS_FOLDER = UPLOAD_FOLDER / 'reports'
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB limit
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
    MODEL_DIR = BASE_DIR / 'ml_models'
    MODEL_PATH = MODEL_DIR / 'skin_cancer_model.h5'
    
    # Session configuration
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
