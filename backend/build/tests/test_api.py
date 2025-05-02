"""
Tests for the backend API endpoints
"""
import json
import pytest

# Note: No need for unittest, tempfile, os, or explicit imports of app/db_utils
# Fixtures from conftest.py handle setup and teardown automatically.

# ---- Basic API Tests ----

@pytest.mark.api
def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get('/api/health')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['status'] == 'ok'
    assert data['message'] == 'Flask backend is running'

# ---- User Management Tests ----

@pytest.mark.api
def test_get_users(client):
    """Test getting the list of users"""
    response = client.get('/api/users')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) >= 2  # At least the 2 test users
    
    # Check if the test users are in the response
    usernames = [user['username'] for user in data]
    assert 'test_user1' in usernames
    assert 'test_user2' in usernames

@pytest.mark.api
def test_register_user(client):
    """Test registering a new user"""
    user_data = {'username': 'test_register_user', 'password': 'password123'}
    response = client.post(
        '/api/register',
        data=json.dumps(user_data),
        content_type='application/json'
    )
    data = json.loads(response.data)
    
    assert response.status_code == 201
    assert 'message' in data
    assert 'registered successfully' in data['message']
    
    # Attempt to register the same user (should fail)
    response = client.post(
        '/api/register',
        data=json.dumps(user_data),
        content_type='application/json'
    )
    assert response.status_code == 409  # Conflict - username exists

@pytest.mark.api
def test_login_user(client):
    """Test user login"""
    # Register a user first
    user_data = {'username': 'test_login_user', 'password': 'password123'}
    client.post(
        '/api/register',
        data=json.dumps(user_data),
        content_type='application/json'
    )
    
    # Login with correct credentials
    response = client.post(
        '/api/login',
        data=json.dumps(user_data),
        content_type='application/json'
    )
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert 'token' in data
    
    # Login with incorrect password
    bad_creds = {'username': 'test_login_user', 'password': 'wrong_password'}
    response = client.post(
        '/api/login',
        data=json.dumps(bad_creds),
        content_type='application/json'
    )
    assert response.status_code == 401

# ---- Blog Post Tests ----

@pytest.mark.api
def test_get_posts(client):
    """Test getting all blog posts"""
    response = client.get('/api/posts')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert isinstance(data, list)
    
    # Verify posts have the expected fields
    if len(data) > 0:
        post = data[0]
        assert 'id' in post
        assert 'title' in post
        assert 'content' in post
        assert 'timestamp' in post
        assert 'excerpt' in post

@pytest.mark.api
def test_get_post(client):
    """Test getting a specific post by ID"""
    # First, get all posts to find an ID
    posts_response = client.get('/api/posts')
    posts_data = json.loads(posts_response.data)
    
    # If there are posts, test getting the first one
    if len(posts_data) > 0:
        post_id = posts_data[0]['id']
        response = client.get(f'/api/posts/{post_id}')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['id'] == post_id
        assert 'title' in data
        assert 'content' in data
        assert 'timestamp' in data

@pytest.mark.api
def test_add_post(client):
    """Test adding a new blog post (requires authentication)"""
    # First login to get a token
    login_data = {'username': 'test_user1', 'password': 'password1'}
    login_response = client.post(
        '/api/login',
        data=json.dumps(login_data),
        content_type='application/json'
    )
    token = json.loads(login_response.data)['token']
    
    # Now create a post with the token
    post_data = {'title': 'Test Post', 'content': 'This is a test post content'}
    response = client.post(
        '/api/posts',
        data=json.dumps(post_data),
        headers={'Authorization': f'Bearer {token}'},
        content_type='application/json'
    )
    data = json.loads(response.data)
    
    assert response.status_code == 201
    assert data['title'] == post_data['title']
    assert data['content'] == post_data['content']
    assert 'id' in data
    assert 'message' in data

# ---- Comment Tests ----

@pytest.mark.api
def test_get_comments(client):
    """Test getting comments for a post"""
    response = client.get('/api/posts/1/comments')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert isinstance(data, list)
    
    # Check if there's at least one comment for post 1
    post1_comments = [c for c in data if c['post_id'] == 1]
    assert len(post1_comments) > 0
    assert post1_comments[0]['content'] == 'Test comment for post 1' # From test_db_utils

@pytest.mark.api
def test_add_comment(client):
    """Test adding a comment to a post"""
    comment_data = {'content': 'Test comment from API test'}
    response = client.post(
        '/api/posts/1/comments',
        data=json.dumps(comment_data),
        content_type='application/json'
    )
    data = json.loads(response.data)
    
    assert response.status_code == 201
    assert data['post_id'] == 1
    assert data['content'] == comment_data['content']
    assert 'id' in data
    
    # Verify the comment was actually added
    get_response = client.get('/api/posts/1/comments')
    get_data = json.loads(get_response.data)
    
    comment_contents = [c['content'] for c in get_data]
    assert comment_data['content'] in comment_contents

@pytest.mark.api
def test_delete_comment(client):
    """Test deleting a comment"""
    # First, add a comment to ensure one exists to delete
    # We'll rely on the one added by create_test_db in the fixture for simplicity
    # Get initial comments to find an ID
    get_response_before = client.get('/api/posts/1/comments')
    get_data_before = json.loads(get_response_before.data)
    comment_to_delete = next((c for c in get_data_before if c['post_id'] == 1), None)
    assert comment_to_delete is not None # Make sure the fixture added a comment
    comment_id = comment_to_delete['id']
    
    # Now delete it
    delete_response = client.delete(f'/api/comments/{comment_id}')
    delete_data = json.loads(delete_response.data)
    
    assert delete_response.status_code == 200
    assert 'deleted successfully' in delete_data['message']
    
    # Verify it's gone
    get_response_after = client.get('/api/posts/1/comments')
    get_data_after = json.loads(get_response_after.data)
    
    comment_ids = [c['id'] for c in get_data_after]
    assert comment_id not in comment_ids

# ---- Error Handling Tests ----

@pytest.mark.api
def test_nonexistent_post(client):
    """Test getting a non-existent post"""
    response = client.get('/api/posts/9999')
    data = json.loads(response.data)
    
    assert response.status_code == 404
    assert 'error' in data

@pytest.mark.api
def test_nonexistent_comment(client):
    """Test deleting a non-existent comment"""
    response = client.delete('/api/comments/9999')
    data = json.loads(response.data)
    
    assert response.status_code == 404
    assert 'error' in data

@pytest.mark.api
def test_invalid_comment_data(client):
    """Test adding a comment with invalid data"""
    # Empty content
    response = client.post(
        '/api/posts/1/comments',
        data=json.dumps({}),
        content_type='application/json'
    )
    assert response.status_code == 400

# No need for `if __name__ == '__main__': unittest.main()` when using pytest 