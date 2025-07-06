from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from .config import Config
from flask_mail import Mail
from flask_cors import CORS
db = None
migrate = None
login = None
mail = None



def create_app():
    global db,migrate,login,mail
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, supports_credentials=True)
    db = SQLAlchemy()
    migrate = Migrate()
    login = LoginManager()
    mail = Mail(app)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    # Import and register your routes here
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    return app
