import os
import json
import logging
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, jsonify, session, abort
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from models import User, Staff, News, Category, Country, Support, SupportResponse, Role
from forms import LoginForm, StaffLoginForm, RegistrationForm, ProfileForm, NewsForm, SupportTicketForm, SupportResponseForm, StaffCreationForm, BroadcastForm
from news_fetcher import fetch_all_news
from utils import get_local_time_for_country, format_datetime, flash_form_errors, get_random_profile_image, get_random_news_image

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Homepage route"""
    # Get breaking news
    breaking_news = News.query.filter_by(is_breaking=True, is_published=True).order_by(News.published_at.desc()).limit(3).all()
    
    # Get latest news from each country
    countries = Country.query.all()
    country_news = {}
    
    for country in countries:
        news = News.query.filter_by(country_id=country.id, is_published=True).order_by(News.published_at.desc()).limit(4).all()
        country_news[country.name] = news
    
    # Get categories
    categories = Category.query.all()
    
    return render_template(
        'index.html',
        breaking_news=breaking_news,
        country_news=country_news,
        countries=countries,
        categories=categories
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login route"""
    if current_user.is_authenticated:
        if current_user.role == Role.ADMIN:
            return redirect(url_for('admin_dashboard'))
        elif current_user.role == Role.STAFF:
            return redirect(url_for('staff_dashboard'))
        else:
            return redirect(url_for('user_dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and check_password_hash(user.password_hash, form.password.data):
            if not user.is_active:
                flash('This account has been disabled. Please contact support.', 'danger')
                return redirect(url_for('login'))
            
            login_user(user, remember=form.remember_me.data)
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            
            if user.role == Role.ADMIN:
                return redirect(next_page or url_for('admin_dashboard'))
            elif user.role == Role.STAFF:
                return redirect(next_page or url_for('staff_dashboard'))
            else:
                return redirect(next_page or url_for('user_dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html', form=form, title='Login')

@app.route('/staff_login', methods=['GET', 'POST'])
def staff_login():
    """Staff login route with staff ID verification"""
    if current_user.is_authenticated:
        if current_user.role == Role.STAFF or current_user.role == Role.ADMIN:
            return redirect(url_for('staff_dashboard'))
        else:
            return redirect(url_for('user_dashboard'))
    
    form = StaffLoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and check_password_hash(user.password_hash, form.password.data):
            # Verify staff ID
            staff = Staff.query.filter_by(user_id=user.id).first()
            
            if not staff or staff.staff_id != form.staff_id.data:
                flash('Invalid staff ID', 'danger')
                return redirect(url_for('staff_login'))
            
            if not user.is_active:
                flash('This account has been disabled. Please contact support.', 'danger')
                return redirect(url_for('staff_login'))
            
            login_user(user, remember=form.remember_me.data)
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            return redirect(next_page or url_for('staff_dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html', form=form, title='Staff Login', staff_login=True)

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    """Admin login route"""
    if current_user.is_authenticated and current_user.role == Role.ADMIN:
        return redirect(url_for('admin_dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and check_password_hash(user.password_hash, form.password.data) and user.role == Role.ADMIN:
            login_user(user, remember=form.remember_me.data)
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials', 'danger')
    
    return render_template('login.html', form=form, title='Admin Login', admin_login=True)

@app.route('/logout')
def logout():
    """Logout route"""
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        # Check if username or email already exists
        existing_username = User.query.filter_by(username=form.username.data).first()
        existing_email = User.query.filter_by(email=form.email.data).first()
        
        if existing_username:
            flash('Username already taken', 'danger')
            return render_template('register.html', form=form)
        
        if existing_email:
            flash('Email already registered', 'danger')
            return render_template('register.html', form=form)
        
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
            phone=form.phone.data,
            location=form.location.data,
            country_id=form.country.data,
            role=Role.USER,
            profile_photo_url=form.profile_photo.data or get_random_profile_image(),
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    # If form validation fails, show errors
    if form.errors:
        flash_form_errors(form)
    
    return render_template('register.html', form=form)

@app.route('/user/dashboard')
@login_required
def user_dashboard():
    """User dashboard route"""
    if current_user.role != Role.USER:
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    # Get user's country news
    user_country_news = []
    if current_user.country:
        user_country_news = News.query.filter_by(
            country_id=current_user.country.id,
            is_published=True
        ).order_by(News.published_at.desc()).limit(10).all()
    
    # Get breaking news
    breaking_news = News.query.filter_by(
        is_breaking=True,
        is_published=True
    ).order_by(News.published_at.desc()).limit(5).all()
    
    # Get categories
    categories = Category.query.all()
    
    return render_template(
        'user/dashboard.html',
        user_country_news=user_country_news,
        breaking_news=breaking_news,
        categories=categories
    )

@app.route('/user/profile', methods=['GET', 'POST'])
@login_required
def user_profile():
    """User profile route"""
    if current_user.role != Role.USER:
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    form = ProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        # Validate current password if changing password
        if form.new_password.data:
            if not form.current_password.data or not check_password_hash(current_user.password_hash, form.current_password.data):
                flash('Current password is incorrect', 'danger')
                return render_template('user/profile.html', form=form)
        
        # Update user data
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data
        current_user.location = form.location.data
        current_user.country_id = form.country.data
        
        if form.profile_photo.data:
            current_user.profile_photo_url = form.profile_photo.data
        
        # Update password if provided
        if form.new_password.data:
            current_user.password_hash = generate_password_hash(form.new_password.data)
        
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('user_profile'))
    
    return render_template('user/profile.html', form=form)

@app.route('/user/support', methods=['GET', 'POST'])
@login_required
def user_support():
    """User support ticket route"""
    if current_user.role != Role.USER:
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    form = SupportTicketForm()
    
    if form.validate_on_submit():
        # Create support ticket
        from utils import generate_unique_id
        
        ticket = Support(
            user_id=current_user.id,
            ticket_id=f"TKT-{generate_unique_id(6)}",
            subject=form.subject.data,
            message=form.message.data,
            status="open",
            created_at=datetime.utcnow()
        )
        
        db.session.add(ticket)
        db.session.commit()
        
        flash('Support ticket submitted successfully', 'success')
        return redirect(url_for('user_support'))
    
    # Get user's tickets
    tickets = Support.query.filter_by(user_id=current_user.id).order_by(Support.created_at.desc()).all()
    
    return render_template('user/support.html', form=form, tickets=tickets)

@app.route('/user/support/<ticket_id>', methods=['GET'])
@login_required
def view_ticket(ticket_id):
    """View support ticket route"""
    if current_user.role != Role.USER:
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    ticket = Support.query.filter_by(ticket_id=ticket_id, user_id=current_user.id).first_or_404()
    responses = SupportResponse.query.filter_by(ticket_id=ticket.id).order_by(SupportResponse.created_at).all()
    
    return render_template('user/ticket.html', ticket=ticket, responses=responses)

@app.route('/staff/dashboard')
@login_required
def staff_dashboard():
    """Staff dashboard route"""
    if current_user.role != Role.STAFF and current_user.role != Role.ADMIN:
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    # Get staff info
    staff = Staff.query.filter_by(user_id=current_user.id).first()
    
    # Get recent news created by staff
    staff_news = News.query.filter_by(created_by=current_user.id).order_by(News.published_at.desc()).limit(5).all()
    
    # Get breaking news
    breaking_news = News.query.filter_by(is_breaking=True).order_by(News.published_at.desc()).limit(5).all()
    
    # Get pending support tickets
    open_tickets = Support.query.filter_by(status="open").order_by(Support.created_at.desc()).limit(5).all()
    
    return render_template(
        'staff/dashboard.html',
        staff=staff,
        staff_news=staff_news,
        breaking_news=breaking_news,
        open_tickets=open_tickets
    )

@app.route('/staff/news', methods=['GET'])
@login_required
def staff_news():
    """Staff news management route"""
    if current_user.role != Role.STAFF and current_user.role != Role.ADMIN:
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    # Get all news, with filter options
    filter_country = request.args.get('country', type=int)
    filter_category = request.args.get('category', type=int)
    filter_status = request.args.get('status')
    
    query = News.query
    
    if filter_country:
        query = query.filter_by(country_id=filter_country)
    
    if filter_category:
        query = query.filter_by(category_id=filter_category)
    
    if filter_status == 'published':
        query = query.filter_by(is_published=True)
    elif filter_status == 'unpublished':
        query = query.filter_by(is_published=False)
    elif filter_status == 'breaking':
        query = query.filter_by(is_breaking=True)
    
    news = query.order_by(News.published_at.desc()).paginate(page=request.args.get('page', 1, type=int), per_page=10)
    
    # Get countries and categories for filters
    countries = Country.query.all()
    categories = Category.query.all()
    
    return render_template(
        'staff/news.html',
        news=news,
        countries=countries,
        categories=categories,
        filter_country=filter_country,
        filter_category=filter_category,
        filter_status=filter_status
    )

@app.route('/staff/news/add', methods=['GET', 'POST'])
@login_required
def add_news():
    """Add news route"""
    if current_user.role != Role.STAFF and current_user.role != Role.ADMIN:
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    form = NewsForm()
    
    if form.validate_on_submit():
        news = News(
            title=form.title.data,
            summary=form.summary.data,
            content=form.content.data,
            image_url=form.image_url.data or get_random_news_image(),
            source_url=form.source_url.data,
            source_name=form.source_name.data,
            category_id=form.category.data,
            country_id=form.country.data,
            is_breaking=form.is_breaking.data,
            is_published=form.is_published.data,
            is_auto_generated=False,
            created_by=current_user.id,
            published_at=datetime.utcnow()
        )
        
        db.session.add(news)
        db.session.commit()
        
        flash('News article added successfully', 'success')
        return redirect(url_for('staff_news'))
    
    # If form validation fails, show errors
    if form.errors:
        flash_form_errors(form)
    
    return render_template('staff/add_news.html', form=form)

@app.route('/staff/news/edit/<int:news_id>', methods=['GET', 'POST'])
@login_required
def edit_news(news_id):
    """Edit news route"""
    if current_user.role != Role.STAFF and current_user.role != Role.ADMIN:
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    news = News.query.get_or_404(news_id)
    form = NewsForm(obj=news)
    
    if form.validate_on_submit():
        news.title = form.title.data
        news.summary = form.summary.data
        news.content = form.content.data
        news.image_url = form.image_url.data
        news.source_url = form.source_url.data
        news.source_name = form.source_name.data
        news.category_id = form.category.data
        news.country_id = form.country.data
        news.is_breaking = form.is_breaking.data
        news.is_published = form.is_published.data
        
        db.session.commit()
        
        flash('News article updated successfully', 'success')
        return redirect(url_for('staff_news'))
    
    # If form validation fails, show errors
    if form.errors:
        flash_form_errors(form)
    
    return render_template('staff/edit_news.html', form=form, news=news)

@app.route('/staff/support', methods=['GET'])
@login_required
def staff_support():
    """Staff support management route"""
    if current_user.role != Role.STAFF and current_user.role != Role.ADMIN:
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    # Get support tickets, with filter options
    filter_status = request.args.get('status')
    
    query = Support.query
    
    if filter_status:
        query = query.filter_by(status=filter_status)
    
    tickets = query.order_by(Support.created_at.desc()).paginate(page=request.args.get('page', 1, type=int), per_page=10)
    
    return render_template(
        'staff/support.html',
        tickets=tickets,
        filter_status=filter_status
    )

@app.route('/staff/support/<ticket_id>', methods=['GET', 'POST'])
@login_required
def staff_view_ticket(ticket_id):
    """Staff view/respond to ticket route"""
    if current_user.role != Role.STAFF and current_user.role != Role.ADMIN:
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    ticket = Support.query.filter_by(ticket_id=ticket_id).first_or_404()
    user = User.query.get(ticket.user_id)
    responses = SupportResponse.query.filter_by(ticket_id=ticket.id).order_by(SupportResponse.created_at).all()
    
    form = SupportResponseForm()
    
    if form.validate_on_submit():
        # Add response
        response = SupportResponse(
            ticket_id=ticket.id,
            responder_id=current_user.id,
            message=form.message.data,
            created_at=datetime.utcnow()
        )
        
        db.session.add(response)
        
        # Update ticket status
        ticket.status = form.status.data
        if form.status.data == "closed":
            ticket.closed_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('Response added successfully', 'success')
        return redirect(url_for('staff_view_ticket', ticket_id=ticket_id))
    
    form.status.data = ticket.status
    
    return render_template('staff/view_ticket.html', ticket=ticket, user=user, responses=responses, form=form)

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard route"""
    if current_user.role != Role.ADMIN:
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    # Count statistics
    total_users = User.query.filter_by(role=Role.USER).count()
    total_staff = User.query.filter_by(role=Role.STAFF).count()
    total_news = News.query.count()
    open_tickets = Support.query.filter_by(status="open").count()
    
    # Get recent activities
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_news = News.query.order_by(News.published_at.desc()).limit(5).all()
    recent_tickets = Support.query.order_by(Support.created_at.desc()).limit(5).all()
    
    return render_template(
        'admin/dashboard.html',
        total_users=total_users,
        total_staff=total_staff,
        total_news=total_news,
        open_tickets=open_tickets,
        recent_users=recent_users,
        recent_news=recent_news,
        recent_tickets=recent_tickets
    )

@app.route('/admin/users')
@login_required
def admin_users():
    """Admin users management route"""
    if current_user.role != Role.ADMIN:
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    # Get users, with filter options
    filter_role = request.args.get('role')
    filter_status = request.args.get('status')
    filter_country = request.args.get('country', type=int)
    
    query = User.query
    
    if filter_role:
        query = query.filter_by(role=Role(filter_role))
    
    if filter_status:
        is_active = filter_status == 'active'
        query = query.filter_by(is_active=is_active)
    
    if filter_country:
        query = query.filter_by(country_id=filter_country)
    
    users = query.order_by(User.created_at.desc()).paginate(page=request.args.get('page', 1, type=int), per_page=10)
    
    # Get countries for filters
    countries = Country.query.all()
    
    return render_template(
        'admin/users.html',
        users=users,
        countries=countries,
        filter_role=filter_role,
        filter_status=filter_status,
        filter_country=filter_country
    )

@app.route('/admin/users/<int:user_id>/toggle_status', methods=['POST'])
@login_required
def toggle_user_status(user_id):
    """Toggle user active status route"""
    if current_user.role != Role.ADMIN:
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    
    # Prevent disabling yourself
    if user.id == current_user.id:
        flash('You cannot disable your own account', 'danger')
        return redirect(url_for('admin_users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.username} has been {status}', 'success')
    
    return redirect(url_for('admin_users'))

@app.route('/admin/staff/add', methods=['GET', 'POST'])
@login_required
def add_staff():
    """Add staff user route"""
    if current_user.role != Role.ADMIN:
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    form = StaffCreationForm()
    
    if form.validate_on_submit():
        # Check if username or email already exists
        existing_username = User.query.filter_by(username=form.username.data).first()
        existing_email = User.query.filter_by(email=form.email.data).first()
        
        if existing_username:
            flash('Username already taken', 'danger')
            return render_template('admin/add_staff.html', form=form)
        
        if existing_email:
            flash('Email already registered', 'danger')
            return render_template('admin/add_staff.html', form=form)
        
        # Create new user with staff role
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
            role=Role.STAFF,
            profile_photo_url=get_random_profile_image(),
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db.session.add(user)
        db.session.flush()  # Flush to get user.id
        
        # Create staff profile
        staff = Staff(
            user_id=user.id,
            department=form.department.data
        )
        
        db.session.add(staff)
        db.session.commit()
        
        flash(f'Staff user created successfully with ID: {staff.staff_id}', 'success')
        return redirect(url_for('admin_users'))
    
    # If form validation fails, show errors
    if form.errors:
        flash_form_errors(form)
    
    return render_template('admin/add_staff.html', form=form)

@app.route('/admin/news')
@login_required
def admin_news():
    """Admin news management route"""
    if current_user.role != Role.ADMIN:
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    # Get all news, with filter options
    filter_country = request.args.get('country', type=int)
    filter_category = request.args.get('category', type=int)
    filter_status = request.args.get('status')
    filter_source = request.args.get('source')
    
    query = News.query
    
    if filter_country:
        query = query.filter_by(country_id=filter_country)
    
    if filter_category:
        query = query.filter_by(category_id=filter_category)
    
    if filter_status == 'published':
        query = query.filter_by(is_published=True)
    elif filter_status == 'unpublished':
        query = query.filter_by(is_published=False)
    elif filter_status == 'breaking':
        query = query.filter_by(is_breaking=True)
    
    if filter_source == 'auto':
        query = query.filter_by(is_auto_generated=True)
    elif filter_source == 'manual':
        query = query.filter_by(is_auto_generated=False)
    
    news = query.order_by(News.published_at.desc()).paginate(page=request.args.get('page', 1, type=int), per_page=10)
    
    # Get countries and categories for filters
    countries = Country.query.all()
    categories = Category.query.all()
    
    return render_template(
        'admin/news.html',
        news=news,
        countries=countries,
        categories=categories,
        filter_country=filter_country,
        filter_category=filter_category,
        filter_status=filter_status,
        filter_source=filter_source
    )

@app.route('/admin/fetch_news', methods=['POST'])
@login_required
def admin_fetch_news():
    """Admin trigger news fetch route"""
    if current_user.role != Role.ADMIN:
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    try:
        count = fetch_all_news()
        flash(f'Successfully fetched {count} news articles', 'success')
    except Exception as e:
        logger.error(f"Error fetching news: {str(e)}")
        flash(f'Error fetching news: {str(e)}', 'danger')
    
    return redirect(url_for('admin_news'))

@app.route('/admin/broadcast', methods=['GET', 'POST'])
@login_required
def admin_broadcast():
    """Admin broadcast message route"""
    if current_user.role != Role.ADMIN:
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    form = BroadcastForm()
    
    if form.validate_on_submit():
        # Logic for broadcasting message
        # This would integrate with the Telegram bots in a real implementation
        country_filter = form.countries.data
        
        # Get count of users who would receive the message
        if country_filter == 'all':
            user_count = User.query.filter_by(role=Role.USER, is_active=True).count()
        else:
            country = Country.query.filter_by(code=country_filter).first()
            if country:
                user_count = User.query.filter_by(role=Role.USER, is_active=True, country_id=country.id).count()
            else:
                user_count = 0
        
        flash(f'Broadcast message "{form.title.data}" sent to {user_count} users', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/broadcast.html', form=form)

@app.route('/admin/tickets')
@login_required
def admin_tickets():
    """Admin support tickets management route"""
    if current_user.role != Role.ADMIN:
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    # Get support tickets, with filter options
    filter_status = request.args.get('status')
    
    query = Support.query
    
    if filter_status:
        query = query.filter_by(status=filter_status)
    
    tickets = query.order_by(Support.created_at.desc()).paginate(page=request.args.get('page', 1, type=int), per_page=10)
    
    return render_template(
        'admin/tickets.html',
        tickets=tickets,
        filter_status=filter_status
    )

@app.route('/news/<int:news_id>')
def view_news(news_id):
    """View single news article"""
    news = News.query.filter_by(id=news_id, is_published=True).first_or_404()
    
    # Get related news from same category
    related_news = News.query.filter_by(
        category_id=news.category_id,
        is_published=True
    ).filter(News.id != news.id).order_by(News.published_at.desc()).limit(3).all()
    
    return render_template('view_news.html', news=news, related_news=related_news)

@app.route('/news/category/<int:category_id>')
def news_by_category(category_id):
    """View news by category"""
    category = Category.query.get_or_404(category_id)
    
    news = News.query.filter_by(
        category_id=category_id,
        is_published=True
    ).order_by(News.published_at.desc()).paginate(page=request.args.get('page', 1, type=int), per_page=10)
    
    return render_template('news_category.html', category=category, news=news)

@app.route('/news/country/<int:country_id>')
def news_by_country(country_id):
    """View news by country"""
    country = Country.query.get_or_404(country_id)
    
    news = News.query.filter_by(
        country_id=country_id,
        is_published=True
    ).order_by(News.published_at.desc()).paginate(page=request.args.get('page', 1, type=int), per_page=10)
    
    return render_template('news_country.html', country=country, news=news)

@app.route('/search')
def search_news():
    """Search news articles"""
    query = request.args.get('q', '')
    
    if not query:
        return render_template('search.html', query=query, results=None)
    
    # Search in title and summary
    results = News.query.filter(
        (News.title.like(f'%{query}%') | News.summary.like(f'%{query}%')),
        News.is_published == True
    ).order_by(News.published_at.desc()).paginate(page=request.args.get('page', 1, type=int), per_page=10)
    
    return render_template('search.html', query=query, results=results)

@app.template_filter('format_datetime')
def format_datetime_filter(value, format='%d %b %Y, %H:%M'):
    """Template filter to format datetime"""
    if value is None:
        return ""
    return format_datetime(value, format)

@app.context_processor
def utility_processor():
    """Add utility functions to templates"""
    return dict(
        get_local_time_for_country=get_local_time_for_country,
        format_datetime=format_datetime,
        get_categories=lambda: Category.query.all(),
        get_countries=lambda: Country.query.all(),
        get_random_news_image=lambda: "https://source.unsplash.com/random/800x600/?news",
        now=datetime.utcnow()
    )

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

@app.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403
