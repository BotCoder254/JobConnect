from flask import Flask
from flask_pymongo import PyMongo
from flask_login import LoginManager
from config import Config
from bson import ObjectId

mongo = PyMongo()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    mongo.init_app(app)
    login_manager.init_app(app)

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        if user_data:
            return User(user_data)
        return None

    from app.routes import auth_routes, landing_routes, job_routes, user_routes
    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(landing_routes.bp)
    app.register_blueprint(job_routes.bp)
    app.register_blueprint(user_routes.bp, url_prefix='/user')

    return app
