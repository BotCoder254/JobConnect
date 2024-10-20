from flask import Blueprint, render_template, request, current_app, redirect, url_for, flash
from flask_login import current_user, login_required
from app import mongo
from bson import ObjectId
from app.utils import paginate
from app.forms import JobPostForm
from app.decorators import company_required
from werkzeug.utils import secure_filename
import os
from datetime import datetime

bp = Blueprint('job', __name__)

@bp.route('/jobs')
def list_jobs():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    location = request.args.get('location', '')
    category = request.args.get('category', '')
    
    query = {}
    if search:
        query['$or'] = [
            {'title': {'$regex': search, '$options': 'i'}},
            {'description': {'$regex': search, '$options': 'i'}}
        ]
    if location:
        query['location'] = location
    if category:
        query['category'] = category
    
    jobs_cursor = mongo.db.jobs.find(query)
    pagination = paginate(jobs_cursor, page, current_app.config['JOBS_PER_PAGE'])
    
    # Get all unique locations and categories for the dropdowns
    locations = mongo.db.jobs.distinct('location')
    categories = mongo.db.jobs.distinct('category')
    
    # Enhance job data with additional information
    for job in pagination.items:
        company = mongo.db.companies.find_one({'_id': job['company_id']})
        job['company_name'] = company['name'] if company else 'Unknown Company'
        job['applicants_count'] = mongo.db.applications.count_documents({'job_id': job['_id']})
        job['views'] = job.get('views', 0)
        job['rating'] = job.get('rating', {'sum': 0, 'count': 0})
        if job['rating']['count'] > 0:
            job['rating'] = job['rating']['sum'] / job['rating']['count']
        else:
            job['rating'] = 0
    
    return render_template('jobs/job_list.html', jobs=pagination.items, pagination=pagination, locations=locations, categories=categories)

@bp.route('/job/<job_id>')
def detail(job_id):
    job = mongo.db.jobs.find_one_and_update(
        {'_id': ObjectId(job_id)},
        {'$inc': {'views': 1}},
        return_document=True
    )
    if job:
        company = mongo.db.companies.find_one({'_id': job['company_id']})
        job['company_name'] = company['name'] if company else 'Unknown Company'
        job['applicants_count'] = mongo.db.applications.count_documents({'job_id': ObjectId(job_id)})
        if job.get('rating'):
            job['rating'] = job['rating']['sum'] / job['rating']['count']
        else:
            job['rating'] = 0
    return render_template('jobs/job_detail.html', job=job)

@bp.route('/job/create', methods=['GET', 'POST'])
@login_required
@company_required
def create_job():
    form = JobPostForm()
    if form.validate_on_submit():
        company = mongo.db.companies.find_one({'user_id': ObjectId(current_user.get_id())})
        custom_fields = [
            {
                'name': field.field_name.data,
                'type': field.field_type.data,
                'required': field.is_required.data
            } for field in form.custom_fields
        ]
        job = {
            'title': form.title.data,
            'description': form.description.data,
            'requirements': form.requirements.data,
            'salary': form.salary.data,
            'location': form.location.data,
            'category': form.category.data,
            'company_id': company['_id'],
            'status': 'active',
            'created_at': datetime.utcnow(),
            'custom_fields': custom_fields
        }
        
        if 'job_media' in request.files:
            file = request.files['job_media']
            if file and allowed_file(file.filename, {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov'}):
                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'job_media', filename)
                file.save(file_path)
                job['media_filename'] = filename
        
        mongo.db.jobs.insert_one(job)
        flash('Job posted successfully', 'success')
        return redirect(url_for('company.manage_jobs'))
    return render_template('jobs/create_job.html', form=form)

@bp.route('/job/<job_id>/edit', methods=['GET', 'POST'])
@login_required
@company_required
def edit_job(job_id):
    job = mongo.db.jobs.find_one({'_id': ObjectId(job_id)})
    if not job:
        flash('Job not found', 'error')
        return redirect(url_for('company.manage_jobs'))
    
    form = JobPostForm(obj=job)
    if form.validate_on_submit():
        updated_job = {
            'title': form.title.data,
            'description': form.description.data,
            'requirements': form.requirements.data,
            'salary': form.salary.data,
            'location': form.location.data,
        }
        mongo.db.jobs.update_one({'_id': ObjectId(job_id)}, {'$set': updated_job})
        flash('Job updated successfully', 'success')
        return redirect(url_for('company.manage_jobs'))
    return render_template('jobs/edit_job.html', form=form, job=job)

@bp.route('/job/<job_id>/delete', methods=['POST'])
@login_required
@company_required
def delete_job(job_id):
    result = mongo.db.jobs.delete_one({'_id': ObjectId(job_id)})
    if result.deleted_count:
        flash('Job deleted successfully', 'success')
    else:
        flash('Job not found', 'error')
    return redirect(url_for('company.manage_jobs'))

@bp.route('/job/<job_id>/toggle_status', methods=['POST'])
@login_required
@company_required
def toggle_job_status(job_id):
    job = mongo.db.jobs.find_one({'_id': ObjectId(job_id)})
    if job:
        new_status = 'inactive' if job['status'] == 'active' else 'active'
        mongo.db.jobs.update_one({'_id': ObjectId(job_id)}, {'$set': {'status': new_status}})
        flash(f'Job status updated to {new_status}', 'success')
    else:
        flash('Job not found', 'error')
    return redirect(url_for('company.manage_jobs'))

@bp.route('/job/<job_id>/rate', methods=['POST'])
@login_required
def rate_job(job_id):
    rating = int(request.form.get('rating', 0))
    if 1 <= rating <= 5:
        mongo.db.jobs.update_one(
            {'_id': ObjectId(job_id)},
            {
                '$inc': {
                    'rating.sum': rating,
                    'rating.count': 1
                }
            }
        )
        flash('Thank you for rating this job!', 'success')
    else:
        flash('Invalid rating value', 'error')
    return redirect(url_for('job.detail', job_id=job_id))

@bp.route('/job-recommendations')
@login_required
def job_recommendations():
    user_id = current_user.get_id()
    user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    
    # Get user's skills and interests
    skills = user.get('skills', [])
    interests = user.get('interests', [])
    
    # Find jobs that match user's skills and interests
    recommended_jobs = list(mongo.db.jobs.find({
        '$or': [
            {'required_skills': {'$in': skills}},
            {'category': {'$in': interests}}
        ]
    }).limit(10))
    
    return render_template('jobs/recommendations.html', jobs=recommended_jobs)

def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions
