import os
from datetime import datetime
from flask import Flask, render_template
from config import Config
from database.db import init_db
from services.auth_service import get_current_user
from services.model_service import check_model_availability
from blueprints import auth_bp, main_bp, analysis_bp, testing_bp, admin_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Ensure necessary folders exist
    Config.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    Config.PATIENT_IMAGES_FOLDER.mkdir(parents=True, exist_ok=True)
    Config.REPORTS_FOLDER.mkdir(parents=True, exist_ok=True)
    Config.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    Config.MODEL_DIR.mkdir(parents=True, exist_ok=True)
    
    # Initialize SQLite Database & seed test cases
    with app.app_context():
        init_db()
        
    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(testing_bp)
    app.register_blueprint(admin_bp)
    
    # Global context processors for templates
    @app.context_processor
    def inject_globals():
        return {
            'current_user': get_current_user(),
            'current_year': datetime.now().year,
            'project_name': 'Skin Cancer Detection System',
            'affiliation': "SVKM's NMIMS MPSTME — Computer Engineering Department",
            'authors': 'Vivaan Sanghvi (C063), Bhavi Doshi (C078), Vidisha Ajmera (C084)',
            'global_model_status': check_model_availability()
        }
        
    # Error Handlers
    @app.errorhandler(400)
    def bad_request_error(e):
        return render_template('errors/400.html', error=e), 400
        
    @app.errorhandler(403)
    def forbidden_error(e):
        return render_template('errors/403.html', error=e), 403
        
    @app.errorhandler(404)
    def not_found_error(e):
        return render_template('errors/404.html', error=e), 404
        
    @app.errorhandler(413)
    def file_too_large_error(e):
        return render_template('errors/413.html', error="The uploaded image exceeds the maximum permitted limit of 10 MB."), 413
        
    @app.errorhandler(500)
    def internal_error(e):
        return render_template('errors/500.html', error=e), 500

    return app

app = create_app()

if __name__ == '__main__':
    # Cloud (Render) or local development port
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    app.run(host=host, port=port, debug=False)
