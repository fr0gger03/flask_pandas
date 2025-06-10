"""
Unit tests for the main Flask application routes and functionality.
"""
import pytest
from flask import url_for


def test_home_route(client):
    """Test the home page route"""
    response = client.get('/')
    assert response.status_code == 200
    # Update this based on actual home page content
    assert b'Flask' in response.data or b'home' in response.data.lower()


def test_about_route(client):
    """Test the about page route"""
    response = client.get('/about')
    assert response.status_code == 200


def test_register_get(client):
    """Test GET request to register page"""
    response = client.get('/register')
    assert response.status_code == 200
    assert b'register' in response.data.lower() or b'Register' in response.data


def test_login_get(client):
    """Test GET request to login page"""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'login' in response.data.lower() or b'Login' in response.data


def test_logout_redirect(client):
    """Test logout redirects to login"""
    response = client.get('/logout')
    assert response.status_code == 302  # Redirect to login
    assert '/login' in response.headers['Location']


def test_dashboard_requires_auth(client):
    """Test that dashboard requires authentication"""
    response = client.get('/dashboard')
    assert response.status_code == 302  # Redirect to login
    assert '/login' in response.headers['Location']


def test_upload_requires_auth(client):
    """Test that upload page requires authentication"""
    response = client.get('/upload')
    assert response.status_code == 302  # Redirect to login
    assert '/login' in response.headers['Location']


def test_profile_requires_auth(client):
    """Test that profile page requires authentication"""
    response = client.get('/profile')
    assert response.status_code == 302  # Redirect to login
    assert '/login' in response.headers['Location']
