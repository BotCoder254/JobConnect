from flask import Flask
from flask_pymongo import PyMongo
from flask_login import LoginManager
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from config import Config

mongo = PyMongo()
login_manager = LoginManager()
mail = Mail()
limiter = Limiter(key_func=get_remote_address)
csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    mongo.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    mail.init_app(app)
    limiter.init_app(app)
    csrf.init_app(app)

    from app.routes import auth_routes, user_routes, company_routes, job_routes, admin_routes, landing_routes
    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(user_routes.bp)
    app.register_blueprint(company_routes.bp)
    app.register_blueprint(job_routes.bp)
    app.register_blueprint(admin_routes.bp)
    app.register_blueprint(landing_routes.bp)

    return app
