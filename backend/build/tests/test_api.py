"""
Tests for the backend API endpoints
"""
import json

# Note: No need for unittest, tempfile, os, or explicit imports of app/db_utils
# Fixtures from conftest.py handle setup and teardown automatically.


def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get('/api/health')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['status'] == 'ok'
    assert data['message'] == 'Flask backend is running'


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

# No need for `if __name__ == '__main__': unittest.main()` when using pytest 