from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import mongo
from app.forms import JobPostForm
from bson import ObjectId
import os

bp = Blueprint('company', __name__)

@bp.route('/profile')
@login_required
def profile():
    company_data = mongo.db.companies.find_one({'user_id': ObjectId(current_user.get_id())})
    jobs = list(mongo.db.jobs.find({'company_id': company_data['_id']}))
    return render_template('profile/company_profile.html', company=company_data, jobs=jobs)

@bp.route('/upload_logo', methods=['POST'])
@login_required
def upload_logo():
    if 'logo' not in request.files:
        flash('No file part')
        return redirect(url_for('company.profile'))
    file = request.files['logo']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('company.profile'))
    if file and allowed_file(file.filename, {'png', 'jpg', 'jpeg', 'gif'}):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'company_logos', filename)
        file.save(file_path)
        mongo.db.companies.update_one(
            {'user_id': ObjectId(current_user.get_id())},
            {'$set': {'logo_filename': filename}}
        )
        flash('Logo uploaded successfully')
    return redirect(url_for('company.profile'))

@bp.route('/post_job', methods=['GET', 'POST'])
@login_required
def post_job():
    form = JobPostForm()
    if form.validate_on_submit():
        company = mongo.db.companies.find_one({'user_id': ObjectId(current_user.get_id())})
        job = {
            'title': form.title.data,
            'description': form.description.data,
            'requirements': form.requirements.data,
            'salary': form.salary.data,
            'location': form.location.data,
            'company_id': company['_id']
        }
        mongo.db.jobs.insert_one(job)
        flash('Job posted successfully')
        return redirect(url_for('company.profile'))
    return render_template('jobs/post_job.html', form=form)

@bp.route('/manage_jobs')
@login_required
def manage_jobs():
    company = mongo.db.companies.find_one({'user_id': ObjectId(current_user.get_id())})
    jobs = list(mongo.db.jobs.find({'company_id': company['_id']}))
    return render_template('jobs/manage_jobs.html', jobs=jobs)

def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions
