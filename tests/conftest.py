import os
import tempfile
import pytest
from pathlib import Path
from app import create_app
from config import Config
from database.db import init_db

@pytest.fixture
def app():
    # Use temporary database and upload directory for tests
    temp_dir = tempfile.mkdtemp()
    temp_db_path = Path(temp_dir) / 'test_skin_cancer.db'
    temp_upload_path = Path(temp_dir) / 'test_uploads'
    temp_upload_path.mkdir(parents=True, exist_ok=True)
    
    class TestConfig(Config):
        TESTING = True
        WTF_CSRF_ENABLED = False
        DATABASE_PATH = temp_db_path
        UPLOAD_FOLDER = temp_upload_path
        SECRET_KEY = 'test-secret-key-1234'
        
    app = create_app(TestConfig)
    
    with app.app_context():
        init_db()
        
    yield app
    
    # Clean up temp files if possible
    try:
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    except Exception:
        pass

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()
