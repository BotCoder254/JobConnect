from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import mongo, login_manager
from bson.objectid import ObjectId

class User(UserMixin):
    def __init__(self, username, email, role, password=None, profile_picture=None, _id=None):
        self.username = username
        self.email = email
        self.role = role
        self.password_hash = generate_password_hash(password) if password else None
        self.profile_picture = profile_picture
        self._id = _id

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self._id)

    @staticmethod
    def get_by_id(user_id):
        user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if user_data:
            return User(
                username=user_data['username'],
                email=user_data['email'],
                role=user_data['role'],
                profile_picture=user_data.get('profile_picture'),
                _id=user_data['_id']
            )
        return None

    def update_profile(self, data):
        mongo.db.users.update_one(
            {'_id': self._id},
            {'$set': data}
        )

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

class Job:
    def __init__(self, title, description, company_id, requirements=None, salary=None, location=None, _id=None):
        self.title = title
        self.description = description
        self.company_id = company_id
        self.requirements = requirements
        self.salary = salary
        self.location = location
        self._id = _id

    def save(self):
        if not self._id:
            result = mongo.db.jobs.insert_one(self.__dict__)
            self._id = result.inserted_id
        else:
            mongo.db.jobs.update_one({"_id": self._id}, {"$set": self.__dict__})

    @staticmethod
    def get_by_id(job_id):
        job_data = mongo.db.jobs.find_one({"_id": ObjectId(job_id)})
        if job_data:
            return Job(**job_data)
        return None

class Company:
    def __init__(self, name, description, user_id, website=None, location=None, _id=None):
        self.name = name
        self.description = description
        self.user_id = user_id
        self.website = website
        self.location = location
        self._id = _id

    def save(self):
        if not self._id:
            result = mongo.db.companies.insert_one(self.__dict__)
            self._id = result.inserted_id
        else:
            mongo.db.companies.update_one({"_id": self._id}, {"$set": self.__dict__})

    @staticmethod
    def get_by_id(company_id):
        company_data = mongo.db.companies.find_one({"_id": ObjectId(company_id)})
        if company_data:
            return Company(**company_data)
        return None
