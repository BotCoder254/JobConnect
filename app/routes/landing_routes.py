from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from datetime import datetime
from app import mongo
from bson import ObjectId

bp = Blueprint('landing', __name__)

@bp.route('/')
def home():
    # If user is authenticated, redirect to their role-specific dashboard
    if current_user.is_authenticated:
        if current_user.role == 'job_seeker':
            # Get user stats
            stats = {
                'applications_count': mongo.db.applications.count_documents({'user_id': str(current_user.id)}),
                'profile_views': 0,  # This will be updated when profile view tracking is implemented
                'interviews_count': mongo.db.applications.count_documents({
                    'user_id': str(current_user.id),
                    'status': 'interview'
                })
            }
            
            # Get recent applications
            recent_applications = list(mongo.db.applications.find(
                {'user_id': str(current_user.id)}
            ).sort('applied_date', -1).limit(5))
            
            # Get job and company details for applications
            for app in recent_applications:
                job = mongo.db.jobs.find_one({'_id': ObjectId(app['job_id'])})
                if job:
                    app['job'] = job
                    company = mongo.db.companies.find_one({'_id': ObjectId(job['company_id'])})
                    if company:
                        app['company'] = company
            
            # Get recommended jobs
            recommended_jobs = list(mongo.db.jobs.find(
                {'status': 'active'},
                {'title': 1, 'company_id': 1, 'location': 1, 'posted_date': 1}
            ).sort('posted_date', -1).limit(4))
            
            # Get company details for recommended jobs
            for job in recommended_jobs:
                company = mongo.db.companies.find_one({'_id': ObjectId(job['company_id'])})
                if company:
                    job['company'] = company
            
            return render_template('user/dashboard.html',
                                stats=stats,
                                recent_applications=recent_applications,
                                recommended_jobs=recommended_jobs,
                                now=datetime.now())
        
        elif current_user.role == 'company':
            # Get company details
            company = mongo.db.companies.find_one({'_id': ObjectId(current_user.company_id)}) if current_user.company_id else None
            if not company:
                return redirect(url_for('company.setup'))
            
            # Get company stats
            stats = {
                'active_jobs': mongo.db.jobs.count_documents({
                    'company_id': str(current_user.company_id),
                    'status': 'active'
                }),
                'total_applications': mongo.db.applications.count_documents({
                    'job_id': {'$in': [str(job['_id']) for job in mongo.db.jobs.find({'company_id': str(current_user.company_id)})]}
                }),
                'total_views': 0,  # This will be updated when view tracking is implemented
                'hired_count': mongo.db.applications.count_documents({
                    'job_id': {'$in': [str(job['_id']) for job in mongo.db.jobs.find({'company_id': str(current_user.company_id)})]},
                    'status': 'hired'
                })
            }
            
            # Get active jobs
            jobs = list(mongo.db.jobs.find({
                'company_id': str(current_user.company_id),
                'status': 'active'
            }).sort('posted_date', -1))
            
            # Get recent applications
            recent_applications = list(mongo.db.applications.find({
                'job_id': {'$in': [str(job['_id']) for job in jobs]}
            }).sort('applied_date', -1).limit(5))
            
            # Get user and job details for applications
            for app in recent_applications:
                user = mongo.db.users.find_one({'_id': ObjectId(app['user_id'])})
                if user:
                    app['user'] = user
                job = mongo.db.jobs.find_one({'_id': ObjectId(app['job_id'])})
                if job:
                    app['job'] = job
            
            return render_template('company/dashboard.html',
                                company=company,
                                stats=stats,
                                jobs=jobs,
                                recent_applications=recent_applications,
                                now=datetime.now())
        
        elif current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
    
    # For non-authenticated users, show the landing page
    featured_jobs = list(mongo.db.jobs.find(
        {'status': 'active', 'is_featured': True},
        {'title': 1, 'company_id': 1, 'location': 1, 'posted_date': 1}
    ).limit(6))
    
    # Get company details for each featured job
    for job in featured_jobs:
        company = mongo.db.companies.find_one({'_id': ObjectId(job['company_id'])})
        if company:
            job['company'] = company
    
    return render_template('landing/landing_page.html', jobs=featured_jobs, now=datetime.now())

@bp.route('/about')
def about():
    return render_template('landing/about.html')

@bp.route('/features')
def features():
    return render_template('landing/features.html')
