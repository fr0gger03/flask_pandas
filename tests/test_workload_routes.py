"""
Tests for workload-related routes: create, view, edit, delete
"""
import pytest
from parser.models import Workload


def test_create_workload_get(client, test_user, test_project):
    """Test GET request to create workload page"""
    # Login first
    login_data = {
        'username': test_user.username,
        'password': 'testpassword123'
    }
    client.post('/login', data=login_data)
    
    response = client.get(f'/create_workload/{test_project.pid}')
    assert response.status_code == 200
    assert b'workload' in response.data.lower() or b'create' in response.data.lower()


def test_create_workload_success(client, test_user, test_project, db_session):
    """Test successful workload creation"""
    # Login first
    login_data = {
        'username': test_user.username,
        'password': 'testpassword123'
    }
    client.post('/login', data=login_data)
    
    # Create workload with minimal required fields
    workload_data = {
        'vmname': 'Test VM',
        'vmstate': 'poweredOn',
        'vcpu': 2,
        'vram': 4096,
        'vinfo_provisioned': 50.0,
        'vinfo_used': 25.0,
        'vmdktotal': 100.0,
        'vmdkused': 50.0,
        'readiops': 100.0,
        'writeiops': 50.0,
        'peakreadiops': 200.0,
        'peakwriteiops': 100.0,
        'readthroughput': 10.0,
        'writethroughput': 5.0,
        'peakreadthroughput': 20.0,
        'peakwritethroughput': 10.0
    }
    
    response = client.post(f'/create_workload/{test_project.pid}', data=workload_data, follow_redirects=False)
    assert response.status_code == 302
    
    # Verify workload was created in database - check by joining to ensure it's in the right project
    workload = Workload.query.filter_by(vmname='Test VM', pid=test_project.pid).first()
    assert workload is not None
    assert workload.pid == test_project.pid


def test_create_workload_with_optional_fields(client, test_user, test_project, db_session):
    """Test creating workload with optional fields"""
    # Login first
    login_data = {
        'username': test_user.username,
        'password': 'testpassword123'
    }
    client.post('/login', data=login_data)
    
    # Create workload with optional fields
    workload_data = {
        'vmname': 'Test VM with Options',
        'mobid': 'vm-123',
        'os': 'Windows Server 2019',
        'os_name': 'testserver.domain.com',
        'vmstate': 'poweredOn',
        'vcpu': 4,
        'vram': 8192,
        'cluster': 'Production Cluster',
        'virtualdatacenter': 'Main DC',
        'ip_addresses': '192.168.1.100',
        'vinfo_provisioned': 100.0,
        'vinfo_used': 50.0,
        'vmdktotal': 200.0,
        'vmdkused': 100.0,
        'readiops': 150.0,
        'writeiops': 75.0,
        'peakreadiops': 300.0,
        'peakwriteiops': 150.0,
        'readthroughput': 15.0,
        'writethroughput': 7.5,
        'peakreadthroughput': 30.0,
        'peakwritethroughput': 15.0
    }
    
    response = client.post(f'/create_workload/{test_project.pid}', data=workload_data, follow_redirects=False)
    assert response.status_code == 302
    
    # Verify workload was created with all fields
    workload = Workload.query.filter_by(vmname='Test VM with Options').first()
    assert workload is not None
    assert workload.mobid == 'vm-123'
    assert workload.os == 'Windows Server 2019'
    assert workload.cluster == 'Production Cluster'


def test_view_workload(client, test_user, test_project, db_session):
    """Test viewing a workload"""
    # Create a test workload
    workload = Workload(
        pid=test_project.pid,
        vmname="Test VM for View",
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
    
    response = client.get(f'/view_workload/{workload.vmid}')
    assert response.status_code == 200
    assert b'Test VM for View' in response.data


def test_view_workload_not_owned(client, test_user, db_session):
    """Test viewing a workload not owned by user"""
    # Create another user and project
    from parser.app import bcrypt
    from parser.models import User, Project
    
    other_user = User(
        username="otheruser2", 
        password=bcrypt.generate_password_hash("password123").decode('utf-8')
    )
    db_session.add(other_user)
    db_session.commit()
    
    other_project = Project(userid=other_user.id, projectname="Other Project 2")
    db_session.add(other_project)
    db_session.commit()
    
    other_workload = Workload(
        pid=other_project.pid,
        vmname="Other VM",
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
    db_session.add(other_workload)
    db_session.commit()
    
    # Login as test_user
    login_data = {
        'username': test_user.username,
        'password': 'testpassword123'
    }
    client.post('/login', data=login_data)
    
    # Try to access other user's workload
    response = client.get(f'/view_workload/{other_workload.vmid}')
    assert response.status_code == 404


def test_edit_workload_get(client, test_user, test_project, db_session):
    """Test GET request to edit workload page"""
    # Create a test workload
    workload = Workload(
        pid=test_project.pid,
        vmname="Test VM for Edit",
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
    
    response = client.get(f'/edit_workload/{workload.vmid}')
    assert response.status_code == 200
    assert b'edit' in response.data.lower() or b'workload' in response.data.lower()
    assert b'Test VM for Edit' in response.data


def test_edit_workload_success(client, test_user, test_project, db_session):
    """Test successful workload editing"""
    # Create a test workload
    workload = Workload(
        pid=test_project.pid,
        vmname="Original VM Name",
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
    
    # Edit workload
    updated_data = {
        'vmname': 'Updated VM Name',
        'vmstate': 'poweredOff',
        'vcpu': 4,
        'vram': 8192,
        'vinfo_provisioned': 100.0,
        'vinfo_used': 50.0,
        'vmdktotal': 200.0,
        'vmdkused': 100.0,
        'readiops': 150.0,
        'writeiops': 75.0,
        'peakreadiops': 300.0,
        'peakwriteiops': 150.0,
        'readthroughput': 15.0,
        'writethroughput': 7.5,
        'peakreadthroughput': 30.0,
        'peakwritethroughput': 15.0
    }
    
    response = client.post(f'/edit_workload/{workload.vmid}', data=updated_data, follow_redirects=False)
    assert response.status_code == 302
    
    # Verify workload was updated
    updated_workload = Workload.query.get(workload.vmid)
    assert updated_workload.vmname == 'Updated VM Name'
    assert updated_workload.vmstate == 'poweredOff'
    assert updated_workload.vcpu == 4


def test_delete_workload(client, test_user, test_project, db_session):
    """Test workload deletion"""
    # Create a test workload
    workload = Workload(
        pid=test_project.pid,
        vmname="VM to Delete",
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
    
    workload_id = workload.vmid
    
    response = client.post(f'/delete_workload/{workload_id}', follow_redirects=False)
    assert response.status_code == 302
    assert f'/view_project/{test_project.pid}' in response.headers['Location']
    
    # Verify workload was deleted
    deleted_workload = Workload.query.get(workload_id)
    assert deleted_workload is None
