from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import mongo
from app.models import User
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, EmailField
from wtforms.validators import DataRequired, Email, EqualTo, Length

bp = Blueprint('auth', __name__)

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')

class RegisterForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=30)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=30)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('job_seeker', 'Job Seeker'), ('company', 'Company')], validators=[DataRequired()])
    accept_terms = BooleanField('I accept the terms and conditions', validators=[DataRequired()])

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('landing.home'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        if mongo.db.users.find_one({"email": form.email.data}):
            flash('Email already registered', 'error')
            return redirect(url_for('auth.register'))

        # Create password hash
        password_hash = generate_password_hash(form.password.data)
        
        # Create user document
        user_data = {
            "username": f"{form.first_name.data} {form.last_name.data}",
            "email": form.email.data,
            "role": form.role.data,
            "password_hash": password_hash,
            "first_name": form.first_name.data,
            "last_name": form.last_name.data
        }
        
        # Insert into database
        mongo.db.users.insert_one(user_data)

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('landing.home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user_data = mongo.db.users.find_one({"email": form.email.data})
        if user_data and check_password_hash(user_data.get('password_hash', ''), form.password.data):
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                role=user_data['role'],
                _id=user_data['_id']
            )
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('landing.home'))
        
        flash('Invalid email or password', 'error')
    
    return render_template('auth/login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('landing.home'))
