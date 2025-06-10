import os
from dotenv import load_dotenv

# Get the directory where this config.py file is located
basedir = os.path.abspath(os.path.dirname(__file__))
# Load .env from the same directory as config.py
load_dotenv()

# debug to assess env variables
# these should be set in a .env file if running locally, or in a compose file if run in a container
print("Environment variables loaded:")
print(f"SECRET_KEY: {os.getenv('SECRET_KEY')}")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")
print(f"UPLOAD_FOLDER: {os.getenv('UPLOAD_FOLDER')}")

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = os.getenv('SECRET_KEY') 
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = None  # Will be set by test fixtures
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'