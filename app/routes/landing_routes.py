from flask import Blueprint, render_template
from app import mongo

bp = Blueprint('landing', __name__)

@bp.route('/')
def home():
    featured_jobs = list(mongo.db.jobs.find().limit(5))
    return render_template('landing/landing_page.html', featured_jobs=featured_jobs)

@bp.route('/about')
def about():
    return render_template('landing/about.html')

@bp.route('/features')
def features():
    return render_template('landing/features.html')
