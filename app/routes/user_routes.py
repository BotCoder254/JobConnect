from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import mongo
from bson import ObjectId
import os
from datetime import datetime
from typing import Optional
from wtforms import Form, StringField, TextAreaField, DecimalField, SelectField, FieldList, FormField, BooleanField, FileField
from wtforms.validators import DataRequired, Email, Length
from flask_wtf.file import FileAllowed
from app.forms import JobApplicationForm

bp = Blueprint('user', __name__)

@bp.route('/profile')
@login_required
def profile():
    user_data = mongo.db.users.find_one({'_id': ObjectId(current_user.get_id())})
    applications = list(mongo.db.applications.find({'user_id': ObjectId(current_user.get_id())}))
    return render_template('profile/user_profile.html', user=user_data, applications=applications)

@bp.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    if 'profile_picture' in request.files:
        file = request.files['profile_picture']
        if file and allowed_file(file.filename, {'png', 'jpg', 'jpeg', 'gif'}):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'profile_pictures', filename)
            file.save(file_path)
            mongo.db.users.update_one(
                {'_id': ObjectId(current_user.get_id())},
                {'$set': {'profile_picture': filename}}
            )
            flash('Profile picture updated successfully', 'success')
    return redirect(url_for('user.profile'))

@bp.route('/upload_resume', methods=['POST'])
@login_required
def upload_resume():
    if 'resume' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('user.profile'))
    file = request.files['resume']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('user.profile'))
    if file and allowed_file(file.filename, {'pdf', 'doc', 'docx'}):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'resumes', filename)
        file.save(file_path)
        mongo.db.users.update_one(
            {'_id': ObjectId(current_user.get_id())},
            {'$set': {'resume_filename': filename}}
        )
        flash('Resume uploaded successfully', 'success')
    return redirect(url_for('user.profile'))

@bp.route('/download_resume')
@login_required
def download_resume():
    user = mongo.db.users.find_one({'_id': ObjectId(current_user.get_id())})
    if user and user.get('resume_filename'):
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'resumes', user['resume_filename'])
        return send_file(file_path, as_attachment=True)
    flash('Resume not found', 'error')
    return redirect(url_for('user.profile'))

@bp.route('/job/<job_id>/apply', methods=['GET', 'POST'])
@login_required
def apply_job(job_id):
    # Check if already applied
    existing_application = mongo.db.applications.find_one({
        "user_id": str(current_user._id),
        "job_id": job_id
    })
    
    if existing_application:
        flash('You have already applied for this job.', 'warning')
        return redirect(url_for('job.detail', job_id=job_id))

    job = mongo.db.jobs.find_one({'_id': ObjectId(job_id)})
    if not job:
        flash('Job not found', 'error')
        return redirect(url_for('job.list_jobs'))

    if request.method == 'POST':
        # Create application
        application = {
            "user_id": str(current_user._id),
            "job_id": job_id,
            "status": "pending",
            "applied_date": datetime.utcnow(),
            "resume_url": request.form.get('resume_url'),
            "cover_letter": request.form.get('cover_letter')
        }
        
        mongo.db.applications.insert_one(application)
        flash('Application submitted successfully!', 'success')
        return redirect(url_for('user.applications'))
    
    return render_template('user/apply.html', job=job)

@bp.route('/applications')
@login_required
def applications():
    # Get user's job applications
    applications = list(mongo.db.applications.find({"user_id": str(current_user._id)}))
    
    # Get job details for each application
    for app in applications:
        job = mongo.db.jobs.find_one({"_id": ObjectId(app['job_id'])})
        if job:
            app['job'] = job
            # Get company details
            company = mongo.db.companies.find_one({"_id": ObjectId(job['company_id'])})
            if company:
                app['company'] = company
    
    return render_template('user/applications.html', applications=applications)

def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions
