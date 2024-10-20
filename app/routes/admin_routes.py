from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.decorators import admin_required
from app import mongo
from bson import ObjectId
from datetime import datetime, timedelta

bp = Blueprint('admin', __name__)

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    user_count = mongo.db.users.count_documents({})
    job_seeker_count = mongo.db.users.count_documents({'role': 'job_seeker'})
    company_count = mongo.db.users.count_documents({'role': 'company'})
    job_count = mongo.db.jobs.count_documents({})
    active_job_count = mongo.db.jobs.count_documents({'status': 'active'})
    application_count = mongo.db.applications.count_documents({})
    
    # User growth data (last 7 days)
    user_growth_labels = []
    user_growth_data = []
    for i in range(6, -1, -1):
        date = datetime.utcnow().date() - timedelta(days=i)
        user_growth_labels.append(date.strftime('%Y-%m-%d'))
        user_growth_data.append(mongo.db.users.count_documents({
            'created_at': {'$lt': date + timedelta(days=1), '$gte': date}
        }))
    
    # Job categories data
    job_categories = mongo.db.jobs.aggregate([
        {'$group': {'_id': '$category', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}},
        {'$limit': 5}
    ])
    job_categories_labels = []
    job_categories_data = []
    for category in job_categories:
        job_categories_labels.append(category['_id'])
        job_categories_data.append(category['count'])
    
    return render_template('profile/admin_dashboard.html',
                           user_count=user_count,
                           job_seeker_count=job_seeker_count,
                           company_count=company_count,
                           job_count=job_count,
                           active_job_count=active_job_count,
                           application_count=application_count,
                           user_growth_labels=user_growth_labels,
                           user_growth_data=user_growth_data,
                           job_categories_labels=job_categories_labels,
                           job_categories_data=job_categories_data)

@bp.route('/manage_users')
@login_required
@admin_required
def manage_users():
    users = list(mongo.db.users.find())
    return render_template('admin/manage_users.html', users=users)

@bp.route('/manage_jobs')
@login_required
@admin_required
def manage_jobs():
    jobs = list(mongo.db.jobs.find())
    return render_template('admin/manage_jobs.html', jobs=jobs)

@bp.route('/manage_companies')
@login_required
@admin_required
def manage_companies():
    companies = list(mongo.db.companies.find())
    return render_template('admin/manage_companies.html', companies=companies)

@bp.route('/delete_user/<user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    mongo.db.users.delete_one({'_id': ObjectId(user_id)})
    flash('User deleted successfully')
    return redirect(url_for('admin.manage_users'))

@bp.route('/delete_job/<job_id>', methods=['POST'])
@login_required
@admin_required
def delete_job(job_id):
    mongo.db.jobs.delete_one({'_id': ObjectId(job_id)})
    flash('Job deleted successfully')
    return redirect(url_for('admin.manage_jobs'))

@bp.route('/delete_company/<company_id>', methods=['POST'])
@login_required
@admin_required
def delete_company(company_id):
    mongo.db.companies.delete_one({'_id': ObjectId(company_id)})
    flash('Company deleted successfully')
    return redirect(url_for('admin.manage_companies'))
