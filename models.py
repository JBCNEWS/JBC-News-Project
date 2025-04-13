from app import db
from flask_login import UserMixin
from datetime import datetime
from enum import Enum
import uuid
import json

class Role(Enum):
    USER = "user"
    STAFF = "staff"
    ADMIN = "admin"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.Enum(Role), default=Role.USER)
    phone = db.Column(db.String(20), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    profile_photo_url = db.Column(db.String(512), nullable=True)
    country_id = db.Column(db.Integer, db.ForeignKey('country.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    telegram_id = db.Column(db.String(50), nullable=True, unique=True)
    
    # Relationships
    country = db.relationship('Country', backref='users')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role.value,
            'phone': self.phone,
            'location': self.location,
            'profile_photo_url': self.profile_photo_url,
            'country': self.country.name if self.country else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    staff_id = db.Column(db.String(8), unique=True, nullable=False)
    department = db.Column(db.String(50), nullable=True)
    
    # Relationships
    user = db.relationship('User', backref='staff_profile')
    
    def __init__(self, *args, **kwargs):
        super(Staff, self).__init__(*args, **kwargs)
        if not self.staff_id:
            self.staff_id = str(uuid.uuid4().hex[:8].upper())
    
    def __repr__(self):
        return f'<Staff {self.staff_id}>'

class Country(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(2), nullable=False)
    timezone = db.Column(db.String(50), nullable=False)
    
    def __repr__(self):
        return f'<Country {self.name}>'

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    
    def __repr__(self):
        return f'<Category {self.name}>'

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    summary = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(512), nullable=True)
    source_url = db.Column(db.String(512), nullable=True)
    source_name = db.Column(db.String(100), nullable=True)
    published_at = db.Column(db.DateTime, default=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    country_id = db.Column(db.Integer, db.ForeignKey('country.id'), nullable=True)
    is_breaking = db.Column(db.Boolean, default=False)
    is_auto_generated = db.Column(db.Boolean, default=True)
    is_published = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    translations = db.Column(db.Text, nullable=True)  # JSON field to store translated content
    
    # Relationships
    category = db.relationship('Category', backref='news')
    country = db.relationship('Country', backref='news')
    author = db.relationship('User', backref='created_news')
    
    def __repr__(self):
        return f'<News {self.title}>'
    
    def get_translation(self, language_code):
        if not self.translations:
            return None
        translations = json.loads(self.translations)
        return translations.get(language_code)
    
    def add_translation(self, language_code, translation_data):
        translations = json.loads(self.translations) if self.translations else {}
        translations[language_code] = translation_data
        self.translations = json.dumps(translations)

class Support(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ticket_id = db.Column(db.String(10), unique=True, nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="open")  # open, in_progress, closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    closed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    user = db.relationship('User', backref='support_tickets')
    
    def __init__(self, *args, **kwargs):
        super(Support, self).__init__(*args, **kwargs)
        if not self.ticket_id:
            self.ticket_id = f"TKT-{str(uuid.uuid4().hex[:6].upper())}"
    
    def __repr__(self):
        return f'<Support {self.ticket_id}>'

class SupportResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('support.id'), nullable=False)
    responder_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    ticket = db.relationship('Support', backref='responses')
    responder = db.relationship('User', backref='support_responses')
    
    def __repr__(self):
        return f'<SupportResponse {self.id}>'

class TelegramChat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.String(50), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    is_registered = db.Column(db.Boolean, default=False)
    registration_step = db.Column(db.String(50), nullable=True)
    temp_data = db.Column(db.Text, nullable=True)  # JSON field to store temporary user data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='telegram_chats')
    
    def __repr__(self):
        return f'<TelegramChat {self.chat_id}>'
    
    def set_temp_data(self, data):
        self.temp_data = json.dumps(data)
    
    def get_temp_data(self):
        if not self.temp_data:
            return {}
        return json.loads(self.temp_data)
