"""
Tests for Appearance Settings (Light, Dark, and System Theme Preference).
"""
from app.models.user import User


def test_appearance_settings_default(client, test_user):
    """Test default appearance setting is 'system'."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    res = client.get('/api/settings/appearance')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['theme'] == 'system'


def test_appearance_settings_update_dark_and_light(client, test_user):
    """Test updating appearance to 'dark' and 'light'."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    # Update to dark
    res_dark = client.post('/api/settings/appearance', json={'theme': 'dark'})
    assert res_dark.status_code == 200
    assert res_dark.get_json()['success'] is True
    assert res_dark.get_json()['theme'] == 'dark'

    # Check persistence via GET
    res_get = client.get('/api/settings/appearance')
    assert res_get.get_json()['theme'] == 'dark'

    # Verify DB
    u = User.query.get(test_user.id)
    assert u.theme_preference == 'dark'

    # Update to light
    res_light = client.post('/api/settings/appearance', json={'theme': 'light'})
    assert res_light.status_code == 200
    assert res_light.get_json()['theme'] == 'light'
    assert User.query.get(test_user.id).theme_preference == 'light'

    # Update back to system
    res_sys = client.post('/api/settings/appearance', json={'theme': 'system'})
    assert res_sys.status_code == 200
    assert res_sys.get_json()['theme'] == 'system'
    assert User.query.get(test_user.id).theme_preference == 'system'


def test_appearance_settings_validation(client, test_user):
    """Test rejecting invalid appearance values."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    res_invalid = client.post('/api/settings/appearance', json={'theme': 'neon-green'})
    assert res_invalid.status_code == 400
    assert res_invalid.get_json()['success'] is False


def test_appearance_user_isolation(client, test_user, second_user):
    """Test that one user's appearance setting does not affect another."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    client.post('/api/settings/appearance', json={'theme': 'dark'})

    # Second user
    with client.session_transaction() as sess:
        sess['user_id'] = second_user.id

    res_sec = client.get('/api/settings/appearance')
    assert res_sec.get_json()['theme'] == 'system'
