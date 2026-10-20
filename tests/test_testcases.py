"""
Automated tests verifying that the test case section is retired from the UI
while test cases remain safely preserved in the SQLite database:
- /test-cases route gracefully redirects to index
- 4 Software Engineering test cases remain preserved in database
- Persistence and CSV export functionality remain intact
"""
import pytest
from database.db import get_all_test_cases, update_test_case_execution

def test_test_cases_page_retired_from_ui_and_redirects(client):
    """
    Verify that the user-facing test cases page is retired and redirects to homepage.
    """
    response = client.get('/test-cases', follow_redirects=False)
    assert response.status_code == 302
    assert response.headers['Location'] == '/'

    # Following redirect lands cleanly on homepage
    followed = client.get('/test-cases', follow_redirects=True)
    assert followed.status_code == 200
    assert b"DermaCare AI" in followed.data

def test_test_case_data_preserved_in_database(client):
    """
    Verify that all 4 Software Engineering test cases remain safely stored in the database.
    """
    cases = get_all_test_cases()
    assert len(cases) == 4
    case_ids = [c['test_case_id'] for c in cases]
    assert 'TC-01' in case_ids
    assert 'TC-02' in case_ids
    assert 'TC-03' in case_ids
    assert 'TC-04' in case_ids

def test_save_test_case_execution_persists(client):
    """
    Verify backend execution persistence for test cases in SQLite.
    """
    post_data = {
        'actual_TC-01': 'User successfully registered, logged in with correct email/password, and was immediately redirected to the dashboard.',
        'status_TC-01': 'Pass',
        'comments_TC-01': 'Verified during live pytest run.'
    }

    save_response = client.post('/test-cases/save', data=post_data, follow_redirects=True)
    assert save_response.status_code == 200

    with client.application.app_context():
        cases = {c['test_case_id']: c for c in get_all_test_cases()}
        assert cases['TC-01']['pass_fail'] == 'Pass'
        assert 'Verified during live pytest run.' in cases['TC-01']['comments']

def test_export_test_cases_csv(client):
    """
    Verify that test case CSV export remains operational for documentation.
    """
    csv_response = client.get('/test-cases/export-csv')
    assert csv_response.status_code == 200
    assert 'text/csv' in csv_response.headers.get('Content-Type')
    data = csv_response.data.decode('utf-8')
    assert 'Test case id,Test cases,Priority,Preconditions' in data
    assert 'TC-01' in data
    assert 'TC-02' in data
    assert 'TC-03' in data
    assert 'TC-04' in data

