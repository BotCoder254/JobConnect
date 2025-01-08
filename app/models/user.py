from flask_login import UserMixin
from bson import ObjectId

class User(UserMixin):
    def __init__(self, user_data):
        self.user_data = user_data
        self.id = str(user_data.get('_id'))
        self.email = user_data.get('email')
        self.name = user_data.get('name')
        self.role = user_data.get('role', 'job_seeker')
        self.profile_picture = user_data.get('profile_picture')
        self.resume_filename = user_data.get('resume_filename')
        self.is_active = user_data.get('is_active', True)
        self.company_id = user_data.get('company_id')
        
    def get_id(self):
        return str(self.id)
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def __repr__(self):
        return f'<User {self.email}>' 