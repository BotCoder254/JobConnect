from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from app import mongo
from app.models import User

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        if mongo.db.users.find_one({"email": email}):
            flash('Email already registered')
            return redirect(url_for('auth.register'))

        new_user = User(username=username, email=email, role=role, password=password)
        mongo.db.users.insert_one({
            "username": new_user.username,
            "email": new_user.email,
            "role": new_user.role,
            "password_hash": new_user.password_hash
        })

        flash('Registration successful')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user_data = mongo.db.users.find_one({"email": email})
        if user_data and User(username=user_data['username'], email=user_data['email'], role=user_data['role'], _id=user_data['_id']).check_password(password):
            user = User(username=user_data['username'], email=user_data['email'], role=user_data['role'], _id=user_data['_id'])
            login_user(user)
            return redirect(url_for('landing.home'))
        
        flash('Invalid email or password')
    
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('landing.home'))
