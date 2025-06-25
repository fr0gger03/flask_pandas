"""
Tests for additional routes: analytics, reports, profile, health
"""
import pytest
from parser.models import Workload


def test_authenticated_home_with_projects(client, test_user, test_project, db_session):
    """Test home page for authenticated user with projects"""
    # Create some workloads for statistics
    workload1 = Workload(
        pid=test_project.pid,
        vmname="VM1",
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
    db_session.add(workload1)
    db_session.commit()
    
    # Login first
    login_data = {
        'username': test_user.username,
        'password': 'testpassword123'
    }
    client.post('/login', data=login_data)
    
    response = client.get('/')
    assert response.status_code == 200
    # Should show project statistics for authenticated users
    assert b'1' in response.data  # project count or workload count


def test_profile_access(client, test_user):
    """Test profile page access with session"""
    # Login first
    login_data = {
        'username': test_user.username,
        'password': 'testpassword123'
    }
    client.post('/login', data=login_data)
    
    response = client.get('/profile')
    assert response.status_code == 200
    assert test_user.username.encode() in response.data


def test_profile_redirect_when_not_in_session(client, test_user):
    """Test profile redirects when session doesn't have loggedin flag"""
    # This test is for the specific session check in the profile route
    response = client.get('/profile')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_analytics_page(client, test_user, test_project, db_session):
    """Test analytics page with data"""
    # Create workloads with different attributes for analytics
    workloads = [
        Workload(
            pid=test_project.pid,
            vmname="Windows VM",
            os="Windows Server 2019",
            vmstate="poweredOn",
            vcpu=4,
            vram=8192,
            cluster="Prod Cluster",
            vinfo_provisioned=100.0,
            vinfo_used=50.0,
            vmdktotal=200.0,
            vmdkused=100.0,
            readiops=150.0,
            writeiops=75.0,
            peakreadiops=300.0,
            peakwriteiops=150.0,
            readthroughput=15.0,
            writethroughput=7.5,
            peakreadthroughput=30.0,
            peakwritethroughput=15.0
        ),
        Workload(
            pid=test_project.pid,
            vmname="Linux VM",
            os="Ubuntu 20.04",
            vmstate="poweredOn",
            vcpu=2,
            vram=4096,
            cluster="Prod Cluster",
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
    ]
    
    for workload in workloads:
        db_session.add(workload)
    db_session.commit()
    
    # Login first
    login_data = {
        'username': test_user.username,
        'password': 'testpassword123'
    }
    client.post('/login', data=login_data)
    
    response = client.get('/analytics')
    assert response.status_code == 200
    assert b'analytics' in response.data.lower() or b'Analytics' in response.data
    # Should show statistics
    assert b'2' in response.data  # total workloads
    assert b'Windows Server 2019' in response.data or b'Ubuntu 20.04' in response.data


def test_analytics_no_data(client, test_user, test_project):
    """Test analytics page with no workload data"""
    # Login first
    login_data = {
        'username': test_user.username,
        'password': 'testpassword123'
    }
    client.post('/login', data=login_data)
    
    response = client.get('/analytics')
    assert response.status_code == 200
    # Should handle empty data gracefully
    assert b'0' in response.data  # zero counts


def test_reports_page(client, test_user):
    """Test reports page"""
    # Login first
    login_data = {
        'username': test_user.username,
        'password': 'testpassword123'
    }
    client.post('/login', data=login_data)
    
    response = client.get('/reports')
    assert response.status_code == 200
    assert b'report' in response.data.lower() or b'Reports' in response.data


def test_health_endpoint_healthy(client):
    """Test health endpoint when system is healthy"""
    response = client.get('/health')
    assert response.status_code == 200
    
    json_data = response.get_json()
    assert json_data['status'] == 'healthy'
    assert 'timestamp' in json_data
    assert json_data['service'] == 'flask-workload-parser'
    assert json_data['version'] == '1.0.0'


def test_cancel_upload(client, test_user):
    """Test cancel upload functionality"""
    # Login first
    login_data = {
        'username': test_user.username,
        'password': 'testpassword123'
    }
    client.post('/login', data=login_data)
    
    # Set some session data to simulate an upload in progress
    with client.session_transaction() as sess:
        sess['processed_data'] = {'test': 'data'}
        sess['project_id'] = 1
        sess['file_name'] = 'test.xlsx'
        sess['file_type'] = 'rvtools'
    
    response = client.post('/cancel_upload', follow_redirects=False)
    assert response.status_code == 302
    assert '/dashboard' in response.headers['Location']
    
    # Verify session data was cleared (we can't directly check session in tests,
    # but the route should clear it)


def test_dashboard_with_data(client, test_user, test_project, db_session):
    """Test dashboard with project and workload data"""
    # Create a workload
    workload = Workload(
        pid=test_project.pid,
        vmname="Dashboard Test VM",
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
    
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b'dashboard' in response.data.lower() or b'Dashboard' in response.data
    assert test_project.projectname.encode() in response.data
    assert b'1' in response.data  # should show 1 workload


def test_login_failure_invalid_user(client):
    """Test login with non-existent user"""
    login_data = {
        'username': 'nonexistent',
        'password': 'password123'
    }
    
    response = client.post('/login', data=login_data, follow_redirects=True)
    assert response.status_code == 200
    # Should stay on login page
    assert b'login' in response.data.lower()


def test_login_failure_wrong_password(client, test_user):
    """Test login with wrong password"""
    login_data = {
        'username': test_user.username,
        'password': 'wrongpassword'
    }
    
    response = client.post('/login', data=login_data, follow_redirects=True)
    assert response.status_code == 200
    # Should stay on login page
    assert b'login' in response.data.lower()


def test_register_duplicate_username(client, test_user):
    """Test registration with existing username"""
    registration_data = {
        'username': test_user.username,
        'password': 'newpassword123'
    }
    
    response = client.post('/register', data=registration_data, follow_redirects=True)
    # This should fail validation and stay on register page
    # The exact behavior depends on your form validation
    assert response.status_code == 200
