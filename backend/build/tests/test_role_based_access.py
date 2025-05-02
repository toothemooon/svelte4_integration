"""
Tests for role-based access control functionality
"""
import json
import pytest
import jwt
from datetime import datetime, timedelta

@pytest.mark.api
@pytest.mark.rbac
def test_get_user_role(client, app_context):
    """Test retrieving user role information"""
    # First login to get a token for admin user
    login_data = {'username': 'test_user1', 'password': 'password1'}
    response = client.post(
        '/api/login',
        data=json.dumps(login_data),
        content_type='application/json'
    )
    data = json.loads(response.data)
    
    # Verify token contains role information
    token = data['token']
    # Import app from conftest to get the SECRET_KEY
    from app import app
    decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
    
    assert 'role' in decoded
    assert decoded['role'] == 'admin'
    
    # Login as regular user
    login_data = {'username': 'test_user2', 'password': 'password2'}
    response = client.post(
        '/api/login',
        data=json.dumps(login_data),
        content_type='application/json'
    )
    data = json.loads(response.data)
    
    # Verify token contains regular user role
    token = data['token']
    decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
    
    assert 'role' in decoded
    assert decoded['role'] == 'user'

@pytest.mark.api
@pytest.mark.rbac
def test_admin_only_endpoint(client, app_context):
    """Test that an admin-only endpoint rejects regular users"""
    # We'll test with the /api/admin/users endpoint that should be protected
    
    # First login as admin
    admin_login = {'username': 'test_user1', 'password': 'password1'}
    response = client.post(
        '/api/login',
        data=json.dumps(admin_login),
        content_type='application/json'
    )
    admin_token = json.loads(response.data)['token']
    
    # Then login as regular user
    user_login = {'username': 'test_user2', 'password': 'password2'}
    response = client.post(
        '/api/login',
        data=json.dumps(user_login),
        content_type='application/json'
    )
    user_token = json.loads(response.data)['token']
    
    # Try to access admin endpoint with admin token - should succeed
    response = client.get(
        '/api/admin/users',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 200
    
    # Try with regular user token - should fail
    response = client.get(
        '/api/admin/users',
        headers={'Authorization': f'Bearer {user_token}'}
    )
    assert response.status_code == 403
    
    # Try with no token - should fail
    response = client.get('/api/admin/users')
    assert response.status_code == 401

@pytest.mark.api
@pytest.mark.rbac
def test_post_ownership_access(client):
    """Test that users can only edit/delete their own posts"""
    # Login as user1 (admin)
    user1_login = {'username': 'test_user1', 'password': 'password1'}
    response = client.post(
        '/api/login',
        data=json.dumps(user1_login),
        content_type='application/json'
    )
    user1_token = json.loads(response.data)['token']
    
    # Login as user2 (regular user)
    user2_login = {'username': 'test_user2', 'password': 'password2'}
    response = client.post(
        '/api/login',
        data=json.dumps(user2_login),
        content_type='application/json'
    )
    user2_token = json.loads(response.data)['token']
    
    # Create first post as admin (user1)
    post_data = {'title': 'Admin Post 1', 'content': 'This post belongs to admin'}
    response = client.post(
        '/api/posts',
        data=json.dumps(post_data),
        headers={'Authorization': f'Bearer {user1_token}'},
        content_type='application/json'
    )
    admin_post1 = json.loads(response.data)
    
    # Create second post as admin (user1)
    post_data = {'title': 'Admin Post 2', 'content': 'This is another admin post'}
    response = client.post(
        '/api/posts',
        data=json.dumps(post_data),
        headers={'Authorization': f'Bearer {user1_token}'},
        content_type='application/json'
    )
    admin_post2 = json.loads(response.data)
    
    # Verify regular user (user2) cannot create posts
    post_data = {'title': 'Regular User Post', 'content': 'This should fail'}
    response = client.post(
        '/api/posts',
        data=json.dumps(post_data),
        headers={'Authorization': f'Bearer {user2_token}'},
        content_type='application/json'
    )
    assert response.status_code == 403
    
    # User1 (admin) should be able to edit their own post
    edit_data = {'title': 'Updated Admin Post', 'content': 'Updated content'}
    response = client.put(
        f'/api/posts/{admin_post1["id"]}',
        data=json.dumps(edit_data),
        headers={'Authorization': f'Bearer {user1_token}'},
        content_type='application/json'
    )
    assert response.status_code == 200
    
    # User2 (regular) should NOT be able to edit admin's post
    edit_data = {'title': 'Hacked Post', 'content': 'Hacked content'}
    response = client.put(
        f'/api/posts/{admin_post1["id"]}',
        data=json.dumps(edit_data),
        headers={'Authorization': f'Bearer {user2_token}'},
        content_type='application/json'
    )
    assert response.status_code == 403
    
    # Admin should be able to edit any post
    edit_data = {'title': 'Admin Edit', 'content': 'Edited by admin'}
    response = client.put(
        f'/api/posts/{admin_post2["id"]}',
        data=json.dumps(edit_data),
        headers={'Authorization': f'Bearer {user1_token}'},
        content_type='application/json'
    )
    assert response.status_code == 200

@pytest.mark.api
@pytest.mark.rbac
def test_create_post_permission(client):
    """Test that only authorized users can create posts"""
    # Login as regular user
    user_login = {'username': 'test_user2', 'password': 'password2'}
    response = client.post(
        '/api/login',
        data=json.dumps(user_login),
        content_type='application/json'
    )
    user_token = json.loads(response.data)['token']
    
    # Regular user should NOT be able to create posts (admin only)
    post_data = {'title': 'Regular User Post', 'content': 'This is a test post from regular user'}
    response = client.post(
        '/api/posts',
        data=json.dumps(post_data),
        headers={'Authorization': f'Bearer {user_token}'},
        content_type='application/json'
    )
    assert response.status_code == 403
    
    # Login as admin user
    admin_login = {'username': 'test_user1', 'password': 'password1'}
    response = client.post(
        '/api/login',
        data=json.dumps(admin_login),
        content_type='application/json'
    )
    admin_token = json.loads(response.data)['token']
    
    # Admin should be able to create posts
    post_data = {'title': 'Admin Post', 'content': 'This is a test post from admin'}
    response = client.post(
        '/api/posts',
        data=json.dumps(post_data),
        headers={'Authorization': f'Bearer {admin_token}'},
        content_type='application/json'
    )
    assert response.status_code == 201
    
    # Now try without authentication
    post_data = {'title': 'Unauthenticated Post', 'content': 'This should fail'}
    response = client.post(
        '/api/posts',
        data=json.dumps(post_data),
        content_type='application/json'
    )
    assert response.status_code == 401

@pytest.mark.api
@pytest.mark.rbac
def test_delete_post_permission(client):
    """Test that only admin users can delete posts"""
    # Login as admin user
    admin_login = {'username': 'test_user1', 'password': 'password1'}
    response = client.post(
        '/api/login',
        data=json.dumps(admin_login),
        content_type='application/json'
    )
    admin_token = json.loads(response.data)['token']
    
    # Login as regular user
    user_login = {'username': 'test_user2', 'password': 'password2'}
    response = client.post(
        '/api/login',
        data=json.dumps(user_login),
        content_type='application/json'
    )
    user_token = json.loads(response.data)['token']
    
    # Create a post as admin
    post_data = {'title': 'Post to Delete', 'content': 'This post will be deleted'}
    response = client.post(
        '/api/posts',
        data=json.dumps(post_data),
        headers={'Authorization': f'Bearer {admin_token}'},
        content_type='application/json'
    )
    post = json.loads(response.data)
    post_id = post['id']
    
    # Regular user should NOT be able to delete the post
    response = client.delete(
        f'/api/posts/{post_id}',
        headers={'Authorization': f'Bearer {user_token}'}
    )
    assert response.status_code == 403
    
    # Verify post still exists
    response = client.get(f'/api/posts/{post_id}')
    assert response.status_code == 200
    
    # Admin should be able to delete the post
    response = client.delete(
        f'/api/posts/{post_id}',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 200
    
    # Verify post is deleted
    response = client.get(f'/api/posts/{post_id}')
    assert response.status_code == 404
    
    # Trying to delete without authentication should fail
    response = client.delete(f'/api/posts/{post_id}')
    assert response.status_code == 401 