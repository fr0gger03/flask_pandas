"""
Tests for project-related routes: create, view, edit, delete, export
"""
import pytest
import os
from flask import url_for
from parser.models import Project, Workload


def test_create_project_get(client, test_user):
    """Test GET request to create project page"""
    # Login first
    login_data = {
        'username': test_user.username,
        'password': 'testpassword123'
    }
    client.post('/login', data=login_data)
    
    response = client.get('/create_project')
    assert response.status_code == 200
    assert b'create' in response.data.lower() or b'project' in response.data.lower()


def test_create_project_success(client, test_user, db_session):
    """Test successful project creation"""
    import uuid
    
    # Login first
    login_data = {
        'username': test_user.username,
        'password': 'testpassword123'
    }
    client.post('/login', data=login_data)
    
    # Create project with unique name
    unique_name = f'TestProject{uuid.uuid4().hex[:8]}'
    project_data = {
        'projectname': unique_name
    }
    
    response = client.post('/create_project', data=project_data, follow_redirects=False)
    assert response.status_code == 302
    
    # Verify project was created in database
    project = Project.query.filter_by(projectname=unique_name).first()
    assert project is not None
    assert project.userid == test_user.id


def test_create_project_duplicate_name(client, test_user, test_project):
    """Test creating project with duplicate name"""
    # Login first
    login_data = {
        'username': test_user.username,
        'password': 'testpassword123'
    }
    client.post('/login', data=login_data)
    
    # Try to create project with same name
    project_data = {
        'projectname': test_project.projectname
    }
    
    response = client.post('/create_project', data=project_data, follow_redirects=True)
    assert response.status_code == 200
    # Should show error and stay on create page
    assert b'create' in response.data.lower() or b'project' in response.data.lower()


def test_view_project(client, test_user, test_project):
    """Test viewing a project"""
    # Login first
    login_data = {
        'username': test_user.username,
        'password': 'testpassword123'
    }
    client.post('/login', data=login_data)
    
    response = client.get(f'/view_project/{test_project.pid}')
    assert response.status_code == 200
    assert test_project.projectname.encode() in response.data


def test_view_project_not_owned(client, test_user, db_session):
    """Test viewing a project not owned by user"""
    # Create another user and project
    from parser.app import bcrypt
    from parser.models import User
    
    other_user = User(
        username="otheruser", 
        password=bcrypt.generate_password_hash("password123").decode('utf-8')
    )
    db_session.add(other_user)
    db_session.commit()
    
    other_project = Project(userid=other_user.id, projectname="Other Project")
    db_session.add(other_project)
    db_session.commit()
    
    # Login as test_user
    login_data = {
        'username': test_user.username,
        'password': 'testpassword123'
    }
    client.post('/login', data=login_data)
    
    # Try to access other user's project
    response = client.get(f'/view_project/{other_project.pid}')
    assert response.status_code == 404


def test_edit_project_get(client, test_user, test_project):
    """Test GET request to edit project page"""
    # Login first
    login_data = {
        'username': test_user.username,
        'password': 'testpassword123'
    }
    client.post('/login', data=login_data)
    
    response = client.get(f'/edit_project/{test_project.pid}')
    assert response.status_code == 200
    assert b'edit' in response.data.lower() or b'project' in response.data.lower()
    assert test_project.projectname.encode() in response.data


def test_edit_project_success(client, test_user, test_project):
    """Test successful project editing"""
    # Login first
    login_data = {
        'username': test_user.username,
        'password': 'testpassword123'
    }
    client.post('/login', data=login_data)
    
    # Edit project
    new_name = "Updated Project Name"
    project_data = {
        'projectname': new_name
    }
    
    response = client.post(f'/edit_project/{test_project.pid}', data=project_data, follow_redirects=False)
    assert response.status_code == 302
    
    # Verify project was updated
    updated_project = Project.query.get(test_project.pid)
    assert updated_project.projectname == new_name


def test_delete_project(client, test_user, test_project):
    """Test project deletion"""
    # Login first
    login_data = {
        'username': test_user.username,
        'password': 'testpassword123'
    }
    client.post('/login', data=login_data)
    
    project_id = test_project.pid
    
    response = client.post(f'/delete_project/{project_id}', follow_redirects=False)
    assert response.status_code == 302
    assert '/dashboard' in response.headers['Location']
    
    # Verify project was deleted
    deleted_project = Project.query.get(project_id)
    assert deleted_project is None


def test_export_project_empty(client, test_user, test_project):
    """Test exporting project with no workloads"""
    # Login first
    login_data = {
        'username': test_user.username,
        'password': 'testpassword123'
    }
    client.post('/login', data=login_data)
    
    response = client.get(f'/export_project/{test_project.pid}', follow_redirects=False)
    assert response.status_code == 302
    # Should redirect back to project view with warning


def test_export_project_with_workloads(client, test_user, test_project, db_session):
    """Test exporting project with workloads"""
    # Create a test workload
    workload = Workload(
        pid=test_project.pid,
        vmname="Test VM",
        vmstate="poweredOn",
        vcpu=2,
        vram=4096,
        vinfo_provisioned=50.0,
        vinfo_used=25.0,
        vmdktotal=100.0,
        vmdkused=50.0,
        readiops=100.0,
        writeiops=50.0,
        peakreadiops=200.0,
        peakwriteiops=100.0,
        readthroughput=10.0,
        writethroughput=5.0,
        peakreadthroughput=20.0,
        peakwritethroughput=10.0
    )
    db_session.add(workload)
    db_session.commit()
    
    # Login first
    login_data = {
        'username': test_user.username,
        'password': 'testpassword123'
    }
    client.post('/login', data=login_data)
    
    response = client.get(f'/export_project/{test_project.pid}')
    assert response.status_code == 200
    assert 'text/csv' in response.headers['Content-Type']
    assert f'{test_project.projectname}_workloads.csv' in response.headers['Content-Disposition']
    assert b'Test VM' in response.data
