import csv
import io
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response
from database.db import get_all_test_cases, update_test_case_execution, reset_test_cases

testing_bp = Blueprint('testing', __name__, url_prefix='')

@testing_bp.route('/test-cases')
def test_cases_view():
    """
    Retired from user-facing website navigation.
    Gracefully redirects to homepage.
    """
    return redirect(url_for('main.index'))

@testing_bp.route('/test-cases/save', methods=['POST'])
def save_test_cases():
    # Supports both regular form submission and AJAX JSON
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json
    
    cases = get_all_test_cases()
    for c in cases:
        tc_id = c['test_case_id']
        actual = request.form.get(f'actual_{tc_id}', c['actual_results']).strip()
        status = request.form.get(f'status_{tc_id}', c['pass_fail']).strip()
        comment = request.form.get(f'comments_{tc_id}', c['comments']).strip()
        
        # Validate status choice
        if status not in ['Not Run', 'Pass', 'Fail']:
            status = 'Not Run'
            
        update_test_case_execution(tc_id, actual, status, comment)
        
    if is_ajax:
        return jsonify({'success': True, 'message': 'Test case execution results saved successfully!'})
        
    flash("Test case execution results have been saved persistently to the database.", "success")
    return redirect(url_for('main.index'))

@testing_bp.route('/test-cases/export-csv')
def export_csv():
    cases = get_all_test_cases()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # 10 Column Headers matching the reference image specification
    headers = [
        'Test case id',
        'Test cases',
        'Priority',
        'Preconditions',
        'Input test data',
        'Steps to be executed',
        'Expected results',
        'Actual results',
        'Pass/fail',
        'Comments'
    ]
    writer.writerow(headers)
    
    for c in cases:
        writer.writerow([
            c['test_case_id'],
            c['test_cases'],
            c['priority'],
            c['preconditions'],
            c['input_test_data'],
            c['steps_to_be_executed'],
            c['expected_results'],
            c['actual_results'],
            c['pass_fail'],
            c['comments']
        ])
        
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=Skin_Cancer_System_Functional_Test_Cases.csv"}
    )

@testing_bp.route('/test-cases/reset', methods=['POST'])
def reset_cases():
    reset_test_cases()
    flash("Test case results have been reset to 'Not Run' initial state.", "info")
    return redirect(url_for('testing.test_cases_view'))
