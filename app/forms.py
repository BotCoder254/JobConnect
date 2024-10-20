from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SelectField, TextAreaField, DecimalField, FieldList, FormField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('job_seeker', 'Job Seeker'), ('company', 'Company')])

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class CustomFieldForm(FlaskForm):
    field_name = StringField('Field Name', validators=[DataRequired()])
    field_type = SelectField('Field Type', choices=[
        ('text', 'Text'),
        ('textarea', 'Text Area'),
        ('email', 'Email'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('file', 'File Upload')
    ], validators=[DataRequired()])
    is_required = BooleanField('Required Field')

class JobPostForm(FlaskForm):
    title = StringField('Job Title', validators=[DataRequired(), Length(min=3, max=100)])
    description = TextAreaField('Job Description', validators=[DataRequired()])
    requirements = TextAreaField('Requirements')
    salary = DecimalField('Salary', places=2)
    location = StringField('Location', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    custom_fields = FieldList(FormField(CustomFieldForm), min_entries=1)

class JobApplicationForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired()])
    cover_letter = TextAreaField('Cover Letter', validators=[DataRequired()])
    resume = FileField('Resume', validators=[FileAllowed(['pdf', 'doc', 'docx'], 'Only PDF and Word documents are allowed.')])
    # Dynamic fields will be added here based on the job's custom fields
