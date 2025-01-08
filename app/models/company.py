from bson import ObjectId

class Company:
    def __init__(self, company_data):
        self.id = str(company_data.get('_id'))
        self.name = company_data.get('name')
        self.description = company_data.get('description')
        self.website = company_data.get('website')
        self.location = company_data.get('location')
        self.logo = company_data.get('logo')
        self.user_id = company_data.get('user_id')
        self.is_verified = company_data.get('is_verified', False)
        self.created_at = company_data.get('created_at')
        self.updated_at = company_data.get('updated_at')
    
    def __repr__(self):
        return f'<Company {self.name}>' 