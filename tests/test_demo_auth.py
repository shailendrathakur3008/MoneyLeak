"""
Tests for 1-Click Demo Account and Guest Login features.
"""
import pytest
from app.models.user import User
from app.services.seed_demo import seed_demo_user


def test_login_page_renders_demo_options(client):
    """Verify that login page includes the 1-Click Guest Login buttons and Auto-fill Demo pill."""
    response = client.get('/login')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'id="btn-guest-login"' in html
    assert 'Continue as Guest' in html
    assert 'id="btn-guest-login-bottom"' in html
    assert 'id="btn-fill-demo"' in html
    assert 'Auto-fill Demo' in html


def test_demo_login_get_redirects_to_dashboard(client, app):
    """Verify that navigating to /demo or /auth/demo-login creates session and redirects to dashboard."""
    response = client.get('/demo', follow_redirects=False)
    assert response.status_code == 302
    assert '/dashboard' in response.headers.get('Location', '')

    # Follow redirect to dashboard
    dash_response = client.get('/dashboard')
    assert dash_response.status_code == 200
    html = dash_response.get_data(as_text=True)
    assert 'Tanu Sharma' in html
    assert 'DEMO WORKSPACE' in html
    assert 'Reset Sample Data' in html


def test_demo_login_json_post(client, app):
    """Verify AJAX POST /auth/demo-login returns success JSON."""
    response = client.post('/auth/demo-login', json={})
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['redirect'] == '/dashboard'


def test_guest_route_alias(client):
    """Verify that /guest and /auth/guest-login work as aliases."""
    r1 = client.get('/guest', follow_redirects=False)
    assert r1.status_code == 302
    assert '/dashboard' in r1.headers.get('Location', '')

    r2 = client.get('/auth/guest-login', follow_redirects=False)
    assert r2.status_code == 302
    assert '/dashboard' in r2.headers.get('Location', '')


def test_demo_reset_endpoint(client, app):
    """Verify that /auth/demo-reset resets baseline data."""
    # First log into demo
    client.get('/demo')
    reset_res = client.get('/auth/demo-reset', follow_redirects=True)
    assert reset_res.status_code == 200
    html = reset_res.get_data(as_text=True)
    assert 'Demo workspace has been reset' in html
    assert 'Tanu Sharma' in html


def test_traditional_login_with_demo_credentials(client, app):
    """Verify traditional login with demo@moneyleak.app / demo1234."""
    with app.app_context():
        seed_demo_user(force_reseed=False)

    response = client.post('/login', data={
        'email': 'demo@moneyleak.app',
        'password': 'demo1234'
    }, follow_redirects=True)
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'Tanu Sharma' in html
