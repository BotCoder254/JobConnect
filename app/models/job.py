from bson import ObjectId

class Job:
    def __init__(self, job_data):
        self.id = str(job_data.get('_id'))
        self.title = job_data.get('title')
        self.description = job_data.get('description')
        self.company_id = job_data.get('company_id')
        self.location = job_data.get('location')
        self.type = job_data.get('type')
        self.salary_range = job_data.get('salary_range')
        self.requirements = job_data.get('requirements', [])
        self.status = job_data.get('status', 'active')
        self.is_featured = job_data.get('is_featured', False)
        self.posted_date = job_data.get('posted_date')
        self.applications_count = job_data.get('applications_count', 0)
        self.views = job_data.get('views', 0)
    
    def __repr__(self):
        return f'<Job {self.title}>' 