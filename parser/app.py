from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_wtf import CSRFProtect
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    app.config ['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
    app.config ['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
    app.config ['SECRET_KEY'] = Config.SECRET_KEY
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.session_protection = "strong"
    login_manager.login_view = "pages.login" # this is the endpoint for the login page
    login_manager.login_message = "Please log in to access this page." # this is the message that will be displayed when a user tries to access a protected page without being logged in
    login_manager.login_message_category = "info"
    login_manager.init_app(app)
    csrf = CSRFProtect(app)  # Enable CSRF Protection

    from models import User, Workload, Project
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    bcrypt.init_app(app)

    from pages import bp
    app.register_blueprint(bp)

    # log all the routes to console
    # for rule in app.url_map.iter_rules():
    #     print(f"Rule: {rule}")
    #     print(f"Endpoint: {rule.endpoint}")
    #     print(f"Methods: {rule.methods}")
    #     print("-" * 20)

    return app