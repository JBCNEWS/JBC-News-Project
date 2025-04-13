import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_apscheduler import APScheduler
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
migrate = Migrate()
scheduler = APScheduler()

# Create the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-jbc-news")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///jbc_news.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions with the app
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
migrate.init_app(app, db)
scheduler.init_app(app)
scheduler.start()

# Create database tables
with app.app_context():
    from models import User, Staff, News, Category, Country, Support
    db.create_all()
    logger.info("Database tables created successfully")

    # Create default admin if doesn't exist
    from werkzeug.security import generate_password_hash
    from models import User, Role
    
    admin_exists = User.query.filter_by(email='ayyan@toxai.com.pk').first()
    if not admin_exists:
        admin = User(
            username='admin',
            email='ayyan@toxai.com.pk',
            password_hash=generate_password_hash('9045CcF2'),
            role=Role.ADMIN,
            is_active=True
        )
        db.session.add(admin)
        
        # Add default countries
        countries = [
            Country(name='India', code='IN', timezone='Asia/Kolkata'),
            Country(name='Pakistan', code='PK', timezone='Asia/Karachi'),
            Country(name='USA', code='US', timezone='America/New_York'),
            Country(name='Saudi Arabia', code='SA', timezone='Asia/Riyadh'),
            Country(name='Sri Lanka', code='LK', timezone='Asia/Colombo')
        ]
        db.session.add_all(countries)
        
        # Add default news categories
        categories = [
            Category(name='Politics'),
            Category(name='Business'),
            Category(name='Technology'),
            Category(name='Sports'),
            Category(name='Entertainment'),
            Category(name='Health'),
            Category(name='Science'),
            Category(name='World')
        ]
        db.session.add_all(categories)
        
        db.session.commit()
        logger.info("Default admin user created")
        logger.info("Default countries and categories created")

# Load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Schedule news fetching task
from news_fetcher import fetch_all_news
with app.app_context():
    # Schedule news fetching every 30 minutes
    scheduler.add_job(id='fetch_news', func=fetch_all_news, trigger='interval', minutes=30)
    logger.info("News fetching scheduler started")
