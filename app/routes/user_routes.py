from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import mongo
from bson import ObjectId
import os
from datetime import datetime
from wtforms import Form, StringField, TextAreaField, DecimalField, SelectField, FieldList, FormField, BooleanField, Optional, FileField
from wtforms.validators import DataRequired, Email, Length, FileAllowed
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

@bp.route('/apply/<job_id>', methods=['GET', 'POST'])
@login_required
def apply_job(job_id):
    job = mongo.db.jobs.find_one({'_id': ObjectId(job_id)})
    if not job:
        flash('Job not found', 'error')
        return redirect(url_for('job.list_jobs'))

    form = JobApplicationForm()

    # Add dynamic fields based on job's custom fields
    for field in job.get('custom_fields', []):
        if field['type'] == 'file':
            setattr(form, field['name'], FileField(field['name'], validators=[FileAllowed(['pdf', 'doc', 'docx'])]))
        else:
            setattr(form, field['name'], StringField(field['name'], validators=[DataRequired() if field['required'] else Optional()]))

    if form.validate_on_submit():
        application = {
            'user_id': ObjectId(current_user.get_id()),
            'job_id': ObjectId(job_id),
            'name': form.name.data,
            'email': form.email.data,
            'phone': form.phone.data,
            'cover_letter': form.cover_letter.data,
            'status': 'pending',
            'applied_at': datetime.utcnow()
        }

        # Handle resume upload
        if form.resume.data:
            resume_filename = secure_filename(form.resume.data.filename)
            resume_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'resumes', resume_filename)
            form.resume.data.save(resume_path)
            application['resume_filename'] = resume_filename

        # Handle custom field data
        for field in job.get('custom_fields', []):
            field_name = field['name']
            if field['type'] == 'file':
                if getattr(form, field_name).data:
                    filename = secure_filename(getattr(form, field_name).data.filename)
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'application_files', filename)
                    getattr(form, field_name).data.save(file_path)
                    application[field_name] = filename
            else:
                application[field_name] = getattr(form, field_name).data

        mongo.db.applications.insert_one(application)
        flash('Application submitted successfully', 'success')
        return redirect(url_for('job.detail', job_id=job_id))

    return render_template('jobs/apply.html', form=form, job=job)

def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions
