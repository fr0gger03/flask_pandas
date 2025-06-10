"""
Database integration tests using testcontainers for PostgreSQL.
"""
import pytest
from sqlalchemy import text
from flask import url_for
from parser.app import db, bcrypt
from parser.models import User, Project, Workload


def test_postgres_connection(db_session):
    """Test PostgreSQL connection and version"""
    result = db_session.execute(text('SELECT version()'))
    row = result.fetchone()
    
    assert row is not None
    assert row[0].lower().startswith("postgresql 16.4")


def test_user_creation(db_session):
    """Test user creation via SQLAlchemy model"""
    hashed_password = bcrypt.generate_password_hash("testpassword123").decode('utf-8')
    user = User(username="testuser", password=hashed_password)
    db_session.add(user)
    db_session.commit()
    
    # Query the database for the user
    user_in_db = User.query.filter_by(username="testuser").first()
    
    assert user_in_db is not None
    assert user_in_db.username == "testuser"
    assert bcrypt.check_password_hash(user_in_db.password, "testpassword123")


def test_project_creation(db_session, test_user):
    """Test project creation with foreign key relationship"""
    project = Project(userid=test_user.id, projectname="TestProject")
    db_session.add(project)
    db_session.commit()
    
    project_in_db = Project.query.filter_by(projectname="TestProject").first()
    
    assert project_in_db is not None
    assert project_in_db.projectname == "TestProject"
    assert project_in_db.userid == test_user.id


def test_workload_creation(db_session, test_project):
    """Test workload creation with foreign key relationship"""
    workload = Workload(
        pid=test_project.pid,
        mobid="vm-001",
        cluster="TestCluster",
        virtualdatacenter="TestDC",
        os="Linux",
        os_name="test-vm",
        vmstate="poweredOn",
        vcpu=2,
        vmname="test-vm",
        vram=4,
        ip_addresses="192.168.1.100",
        vinfo_provisioned=50.0,
        vinfo_used=25.0,
        vmdktotal=100.0,
        vmdkused=50.0
    )
    db_session.add(workload)
    db_session.commit()
    
    workload_in_db = Workload.query.filter_by(mobid="vm-001").first()
    
    assert workload_in_db is not None
    assert workload_in_db.mobid == "vm-001"
    assert workload_in_db.pid == test_project.pid
    assert workload_in_db.cluster == "TestCluster"
    assert workload_in_db.vcpu == 2


def test_database_relationships(db_session, test_user):
    """Test database relationships between User, Project, and Workload"""
    # Create project
    project = Project(userid=test_user.id, projectname="RelationshipTest")
    db_session.add(project)
    db_session.commit()
    
    # Create workload
    workload = Workload(
        pid=project.pid,
        mobid="vm-rel-001",
        vmname="relationship-test-vm",
        vcpu=1,
        vram=2
    )
    db_session.add(workload)
    db_session.commit()
    
    # Verify relationships
    project_from_db = Project.query.filter_by(projectname="RelationshipTest").first()
    workload_from_db = Workload.query.filter_by(mobid="vm-rel-001").first()
    
    assert project_from_db.userid == test_user.id
    assert workload_from_db.pid == project_from_db.pid
