from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect

from deeds.config import Config
from flask_migrate import Migrate
from flask_wtf import FlaskForm
import os

from deeds.assets import asset_css_urls, asset_url

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    csrf = CSRFProtect(app)
    # Add the CSRF token context processor



    from deeds.users.routes import users
    from deeds.posts.routes import posts
    from deeds.main.routes import main
    from deeds.goals.routes import goals
    from deeds.errors.handlers import errors
    app.register_blueprint(users)
    app.register_blueprint(goals)
    app.register_blueprint(posts)
    app.register_blueprint(main)
    app.register_blueprint(errors)
    app.jinja_env.globals['asset_url'] = asset_url
    app.jinja_env.globals['asset_css_urls'] = asset_css_urls

    return app
