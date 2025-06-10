"""
Integration tests for login, registration, and authenticated routes.
"""
import pytest
import os
from flask import url_for
from parser.app import bcrypt, db
from parser.models import User


def test_user_registration(client, db_session):
    """Test user registration functionality"""
    registration_data = {
        'username': 'newuser',
        'password': 'newpassword123'
    }
    
    response = client.post('/register', data=registration_data, follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.headers['Location']
    
    # Verify user was created in database
    user = User.query.filter_by(username='newuser').first()
    assert user is not None
    assert bcrypt.check_password_hash(user.password, 'newpassword123')


def test_user_login_success(client, test_user):
    """Test successful user login"""
    login_data = {
        'username': test_user.username,
        'password': 'testpassword123'
    }
    
    response = client.post('/login', data=login_data, follow_redirects=False)
    assert response.status_code == 302
    assert '/dashboard' in response.headers['Location']


def test_user_login_invalid_credentials(client, test_user):
    """Test login with invalid credentials"""
    login_data = {
        'username': test_user.username,
        'password': 'wrongpassword'
    }
    
    response = client.post('/login', data=login_data, follow_redirects=True)
    assert response.status_code == 200
    # Should remain on login page
    assert b'login' in response.data.lower() or b'Login' in response.data


def test_user_login_nonexistent_user(client):
    """Test login with non-existent user"""
    login_data = {
        'username': 'nonexistent',
        'password': 'password123'
    }
    
    response = client.post('/login', data=login_data, follow_redirects=True)
    assert response.status_code == 200
    # Should remain on login page
    assert b'login' in response.data.lower() or b'Login' in response.data


def test_authenticated_dashboard_access(client, test_user):
    """Test accessing dashboard after login"""
    # First login
    login_data = {
        'username': test_user.username,
        'password': 'testpassword123'
    }
    client.post('/login', data=login_data)
    
    # Then access dashboard
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b'dashboard' in response.data.lower() or b'Dashboard' in response.data


def test_authenticated_upload_access(client, test_user):
    """Test accessing upload page after login"""
    # First login
    login_data = {
        'username': test_user.username,
        'password': 'testpassword123'
    }
    client.post('/login', data=login_data)
    
    # Then access upload
    response = client.get('/upload')
    assert response.status_code == 200
    assert b'upload' in response.data.lower() or b'Upload' in response.data


def test_authenticated_profile_access(client, test_user):
    """Test accessing profile page after login"""
    # First login
    login_data = {
        'username': test_user.username,
        'password': 'testpassword123'
    }
    client.post('/login', data=login_data)
    
    # Then access profile
    response = client.get('/profile')
    assert response.status_code == 200
    assert b'profile' in response.data.lower() or b'Profile' in response.data


def test_logout_functionality(client, test_user):
    """Test user logout functionality"""
    # First login
    login_data = {
        'username': test_user.username,
        'password': 'testpassword123'
    }
    client.post('/login', data=login_data)
    
    # Verify we can access protected route
    response = client.get('/dashboard')
    assert response.status_code == 200
    
    # Logout
    response = client.get('/logout', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.headers['Location']
    
    # Verify we can no longer access protected route
    response = client.get('/dashboard')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_file_upload_authentication_required(client):
    """Test that file upload requires authentication"""
    # Create a dummy file for upload
    data = {
        'file': (os.path.join(os.path.dirname(__file__), 'test_files', 'rvtools_file_sample.xlsx'), 'test.xlsx')
    }
    
    response = client.post('/upload', data=data, content_type='multipart/form-data')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_file_upload_with_authentication(client, test_user):
    """Test file upload functionality with authenticated user"""
    # First login
    login_data = {
        'username': test_user.username,
        'password': 'testpassword123'
    }
    client.post('/login', data=login_data)
    
    # Note: This test would need actual Excel test files to work properly
    # For now, we'll just test the authenticated access to the upload route
    response = client.get('/upload')
    assert response.status_code == 200
    assert b'upload' in response.data.lower() or b'Upload' in response.data


def test_duplicate_username_registration(client, test_user):
    """Test that duplicate usernames are not allowed"""
    registration_data = {
        'username': test_user.username,  # Use existing username
        'password': 'anotherpassword123'
    }
    
    response = client.post('/register', data=registration_data, follow_redirects=True)
    assert response.status_code == 200
    # Should remain on registration page with error
    assert b'register' in response.data.lower() or b'Register' in response.data
