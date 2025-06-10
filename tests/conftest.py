"""
Pytest configuration and shared fixtures for the flask_pandas project tests.
"""
import pytest, uuid
from pathlib import Path
from testcontainers.postgres import PostgresContainer
from flask import url_for
from parser.app import create_app, db, bcrypt
from parser.models import User, Project, Workload


@pytest.fixture(scope='session', autouse=True)
def postgres_container():
    """Fixture to create the postgres container and generate the schema"""
    postgres = PostgresContainer('postgres:16.4-alpine3.20')
    postgres = postgres.with_env("POSTGRES_DB", "inventorydb")
    script = Path(__file__).parent / 'sql' / 'init-user-db.sh'
    postgres.with_volume_mapping(host=str(script), container=f"/docker-entrypoint-initdb.d/{script.name}")
    with postgres:
        yield postgres


@pytest.fixture(scope='function')
def app(postgres_container: PostgresContainer):
    """Create Flask app configured for testing"""
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': postgres_container.get_connection_url(),
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'WTF_CSRF_ENABLED': False,  # Disable CSRF for testing
        'SECRET_KEY': 'test-secret-key'
    }
    
    app = create_app(config=test_config)
    
    with app.app_context():
        yield app


# @pytest.fixture(scope='function')
# def db_session(app):
#     """Fixture to handle database session and rollback after each test"""
#     with app.app_context():
#         # Create all tables
#         db.create_all()
        
#         conn = db.engine.connect()
#         trans = conn.begin()
#         session = db.session

#         yield session

#         # Rollback after test and cleanup
#         trans.rollback()
#         conn.close()
#         db.session.remove()

@pytest.fixture(scope='function')
def db_session(app):
    """Fixture to handle database session and rollback after each test"""
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create a savepoint we can rollback to
        connection = db.engine.connect()
        transaction = connection.begin()
        
        # Configure session to use our connection
        db.session.configure(bind=connection)
        
        # Create a savepoint
        savepoint = connection.begin_nested()
        
        yield db.session
        
        # Cleanup: rollback to savepoint, then close
        savepoint.rollback()
        transaction.rollback()
        connection.close()
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
    user = User(username=f"testuser_{uuid.uuid4().hex[:8]}", password=hashed_password)
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_project(db_session, test_user):
    """Create a test project"""
    project = Project(userid=test_user.id, projectname="TestProjectFixture")
    db_session.add(project)
    db_session.commit()
    return project
