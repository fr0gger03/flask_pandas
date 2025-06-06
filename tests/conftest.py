"""
Pytest configuration and shared fixtures for the flask_pandas project tests.
"""
import pytest
from pathlib import Path
from testcontainers.postgres import PostgresContainer
from flask import url_for
from app import create_app, db, bcrypt
from models import User, Project, Workload


@pytest.fixture(scope='session', autouse=True)
def postgres_container():
    """Fixture to create the postgres container and generate the schema"""
    postgres = PostgresContainer('postgres:16.4-alpine3.20')
    script = Path(__file__).parent / 'sql' / 'init-user-db.sh'
    postgres.with_volume_mapping(host=str(script), container=f"/docker-entrypoint-initdb.d/{script.name}")
    with postgres:
        yield postgres


@pytest.fixture(scope='function')
def app(postgres_container: PostgresContainer):
    """Create Flask app configured for testing"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = postgres_container.get_connection_url()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    with app.app_context():
        yield app


@pytest.fixture(scope='function')
def db_session(app):
    """Fixture to handle database session and rollback after each test"""
    with app.app_context():
        conn = db.engine.connect()
        trans = conn.begin()
        session = db.session

        yield session

        # Rollback after test and cleanup
        trans.rollback()
        conn.close()
        db.session.remove()


@pytest.fixture(scope='function')
def client(app):
    """Flask test client to make HTTP requests"""
    with app.test_client() as client:
        yield client


@pytest.fixture
def test_user(db_session):
    """Create a test user for authentication tests"""
    hashed_password = bcrypt.generate_password_hash("testpassword123").decode('utf-8')
    user = User(username="testuser", password=hashed_password)
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_project(db_session, test_user):
    """Create a test project"""
    project = Project(userid=test_user.id, projectname="TestProject")
    db_session.add(project)
    db_session.commit()
    return project
