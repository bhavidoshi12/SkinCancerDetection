from flask import Blueprint, render_template
from services.model_service import check_model_availability

main_bp = Blueprint('main', __name__, url_prefix='')

@main_bp.route('/')
def index():
    model_status = check_model_availability()
    return render_template('index.html', model_status=model_status)

@main_bp.route('/how-it-works')
def how_it_works():
    return render_template('how_it_works.html')

@main_bp.route('/skin-health')
def skin_health():
    return render_template('skin_health.html')
