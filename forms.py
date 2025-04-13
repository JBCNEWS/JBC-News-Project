from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SelectField, FileField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, URL, Optional
from models import Country, Category

class LoginForm(FlaskForm):
    """Form for user login"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class StaffLoginForm(FlaskForm):
    """Form for staff login"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    staff_id = StringField('Staff ID', validators=[DataRequired(), Length(min=8, max=8)])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Staff Sign In')

class RegistrationForm(FlaskForm):
    """Form for user registration"""
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    location = StringField('Location', validators=[DataRequired()])
    country = SelectField('Country', validators=[DataRequired()], coerce=int)
    profile_photo = StringField('Profile Photo URL', validators=[Optional(), URL()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        from app import db
        self.country.choices = [(c.id, c.name) for c in Country.query.order_by(Country.name).all()]

class NewsForm(FlaskForm):
    """Form for adding/editing news"""
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    summary = TextAreaField('Summary', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[Optional()])
    image_url = StringField('Image URL', validators=[Optional(), URL()])
    source_url = StringField('Source URL', validators=[Optional(), URL()])
    source_name = StringField('Source Name', validators=[Optional(), Length(max=100)])
    category = SelectField('Category', validators=[DataRequired()], coerce=int)
    country = SelectField('Country', validators=[DataRequired()], coerce=int)
    is_breaking = BooleanField('Breaking News')
    is_published = BooleanField('Publish Now', default=True)
    submit = SubmitField('Save News')
    
    def __init__(self, *args, **kwargs):
        super(NewsForm, self).__init__(*args, **kwargs)
        from app import db
        self.category.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]
        self.country.choices = [(c.id, c.name) for c in Country.query.order_by(Country.name).all()]

class ProfileForm(FlaskForm):
    """Form for editing user profile"""
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    location = StringField('Location', validators=[DataRequired()])
    country = SelectField('Country', validators=[DataRequired()], coerce=int)
    profile_photo = StringField('Profile Photo URL', validators=[Optional(), URL()])
    current_password = PasswordField('Current Password', validators=[Optional()])
    new_password = PasswordField('New Password', validators=[Optional(), Length(min=8)])
    confirm_password = PasswordField('Confirm New Password', validators=[EqualTo('new_password')])
    submit = SubmitField('Update Profile')
    
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        from app import db
        self.country.choices = [(c.id, c.name) for c in Country.query.order_by(Country.name).all()]

class SupportTicketForm(FlaskForm):
    """Form for creating a support ticket"""
    subject = StringField('Subject', validators=[DataRequired(), Length(max=100)])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Submit Ticket')

class SupportResponseForm(FlaskForm):
    """Form for responding to a support ticket"""
    message = TextAreaField('Response', validators=[DataRequired()])
    status = SelectField('Status', choices=[
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed')
    ], validators=[DataRequired()])
    submit = SubmitField('Send Response')

class StaffCreationForm(FlaskForm):
    """Form for creating staff users"""
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    department = StringField('Department', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Create Staff')

class BroadcastForm(FlaskForm):
    """Form for broadcasting messages"""
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    message = TextAreaField('Message', validators=[DataRequired()])
    countries = SelectField('Countries', choices=[
        ('all', 'All Countries'),
        ('IN', 'India'),
        ('PK', 'Pakistan'),
        ('US', 'USA'),
        ('SA', 'Saudi Arabia'),
        ('LK', 'Sri Lanka')
    ], validators=[DataRequired()])
    submit = SubmitField('Send Broadcast')
