"""
Tests for the authentication functionality
"""
import json
import pytest
import jwt
import os
import sys
from datetime import datetime, timedelta
import time

# Add the backend directory to the path so we can import app
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(backend_dir)

# --- Token Tests ---

@pytest.mark.unit
def test_token_generation(client, app_context):
    """Test that JWT tokens are generated correctly"""
    # Register and login a test user
    username = 'token_test_user'
    password = 'token_test_pass'
    
    # Register
    client.post(
        '/api/register',
        data=json.dumps({'username': username, 'password': password}),
        content_type='application/json'
    )
    
    # Login
    response = client.post(
        '/api/login',
        data=json.dumps({'username': username, 'password': password}),
        content_type='application/json'
    )
    
    data = json.loads(response.data)
    token = data['token']
    
    # Import the app to get the secret key
    from app import app
    
    # Decode the token and verify its contents
    decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
    
    assert 'user_id' in decoded
    assert 'username' in decoded
    assert decoded['username'] == username
    assert 'exp' in decoded
    
    # Check that expiration is set ~24 hours in the future
    exp_time = datetime.fromtimestamp(decoded['exp'])
    now_timestamp = datetime.now().timestamp()
    
    # Token should expire in ~24 hours (with a reasonable margin)
    seconds_in_day = 24 * 60 * 60
    assert decoded['exp'] > now_timestamp  # Token expires in the future
    assert decoded['exp'] < now_timestamp + seconds_in_day + (60 * 60)  # Not more than 25 hours from now

@pytest.mark.unit
def test_invalid_token_access(client):
    """Test that invalid tokens are rejected"""
    # Try to access a protected endpoint with an invalid token
    invalid_token = "invalid.token.string"
    response = client.post(
        '/api/posts',
        data=json.dumps({'title': 'Test', 'content': 'Content'}),
        headers={'Authorization': f'Bearer {invalid_token}'},
        content_type='application/json'
    )
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'Token is invalid' in data['message']

@pytest.mark.unit
def test_missing_token_access(client):
    """Test that requests without tokens are rejected"""
    # Try to access a protected endpoint without a token
    response = client.post(
        '/api/posts',
        data=json.dumps({'title': 'Test', 'content': 'Content'}),
        content_type='application/json'
    )
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'Token is missing' in data['message']

@pytest.mark.unit
@pytest.mark.slow
def test_expired_token(client, app_context):
    """Test that expired tokens are rejected"""
    # Create a token that expires very quickly (1 second)
    # Import what we need from app
    from app import app
    
    # Create a user and get their ID
    username = 'expired_token_user'
    password = 'password'
    
    # Register
    client.post(
        '/api/register',
        data=json.dumps({'username': username, 'password': password}),
        content_type='application/json'
    )
    
    # Login to get user_id
    response = client.post(
        '/api/login',
        data=json.dumps({'username': username, 'password': password}),
        content_type='application/json'
    )
    
    # Get user ID from token
    token = json.loads(response.data)['token']
    decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
    user_id = decoded['user_id']
    
    # Create a token that expires in 1 second
    token = jwt.encode({
        'user_id': user_id,
        'username': username,
        'exp': datetime.utcnow() + timedelta(seconds=1)
    }, app.config['SECRET_KEY'], algorithm="HS256")
    
    # Wait for token to expire
    time.sleep(2)
    
    # Try to use the expired token
    response = client.post(
        '/api/posts',
        data=json.dumps({'title': 'Test', 'content': 'Content'}),
        headers={'Authorization': f'Bearer {token}'},
        content_type='application/json'
    )
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'expired' in data['message'].lower() 