from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app import mongo
from bson import ObjectId
from datetime import datetime
from app.utils import paginate

bp = Blueprint('job', __name__)

@bp.route('/jobs')
def list_jobs():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('JOBS_PER_PAGE', 10)
    
    # Base query
    query = {'status': 'active'}
    
    # Apply filters
    search = request.args.get('search')
    location = request.args.get('location')
    job_type = request.args.get('type')
    
    if search:
        query['$or'] = [
            {'title': {'$regex': search, '$options': 'i'}},
            {'description': {'$regex': search, '$options': 'i'}}
        ]
    if location:
        query['location'] = {'$regex': location, '$options': 'i'}
    if job_type:
        query['type'] = job_type
    
    # Get jobs with pagination
    jobs = mongo.db.jobs.find(query).sort('posted_date', -1)
    pagination = paginate(jobs, page=page, per_page=per_page)
    
    # Get company details for each job
    for job in pagination['items']:
        company = mongo.db.companies.find_one({'_id': ObjectId(job['company_id'])})
        if company:
            job['company'] = company
    
    return render_template('jobs/list.html', 
                         pagination=pagination,
                         search=search,
                         location=location,
                         job_type=job_type)

@bp.route('/job/<job_id>')
def detail(job_id):
    job = mongo.db.jobs.find_one({'_id': ObjectId(job_id)})
    if not job:
        flash('Job not found', 'error')
        return redirect(url_for('job.list_jobs'))
    
    # Get company details
    company = mongo.db.companies.find_one({'_id': ObjectId(job['company_id'])})
    if company:
        job['company'] = company
    
    # Check if user has already applied
    has_applied = False
    if current_user.is_authenticated:
        application = mongo.db.applications.find_one({
            'user_id': str(current_user._id),
            'job_id': job_id
        })
        has_applied = bool(application)
    
    return render_template('jobs/detail.html', job=job, has_applied=has_applied)

@bp.route('/job/create', methods=['GET', 'POST'])
@login_required
def create_job():
    if current_user.role != 'company':
        flash('Only companies can create job listings', 'error')
        return redirect(url_for('job.list_jobs'))
    
    if request.method == 'POST':
        job = {
            'title': request.form.get('title'),
            'company_id': str(current_user._id),
            'location': request.form.get('location'),
            'type': request.form.get('type'),
            'description': request.form.get('description'),
            'requirements': request.form.get('requirements'),
            'salary_range': request.form.get('salary_range'),
            'status': 'active',
            'posted_date': datetime.utcnow(),
            'applications_count': 0
        }
        
        mongo.db.jobs.insert_one(job)
        flash('Job posted successfully!', 'success')
        return redirect(url_for('job.list_jobs'))
    
    return render_template('jobs/create.html')
