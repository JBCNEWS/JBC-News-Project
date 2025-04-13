import os
import logging
import json
import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler, ConversationHandler
from app import db, scheduler
from models import User, TelegramChat, News, Support, Role, Country
from utils import generate_unique_id, translate_text, get_random_profile_image
from news_fetcher import fetch_all_news
from datetime import datetime
from werkzeug.security import generate_password_hash

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Telegram Bot tokens from environment
REGISTRATION_BOT_TOKEN = os.environ.get("REGISTRATION_BOT_TOKEN", "")
SUPPORT_BOT_TOKEN = os.environ.get("SUPPORT_BOT_TOKEN", "")
NEWS_BOT_TOKEN = os.environ.get("NEWS_BOT_TOKEN", "")
STAFF_BOT_TOKEN = os.environ.get("STAFF_BOT_TOKEN", "")

# Registration bot states
(
    NAME, 
    EMAIL, 
    PHONE, 
    LOCATION, 
    COUNTRY, 
    PASSWORD,
    CONFIRM_PASSWORD
) = range(7)

class RegistrationBot:
    """Bot for user registration"""
    
    def __init__(self):
        if not REGISTRATION_BOT_TOKEN:
            logger.error("REGISTRATION_BOT_TOKEN is not set")
            return
            
        self.updater = Updater(token=REGISTRATION_BOT_TOKEN)
        self.dispatcher = self.updater.dispatcher
        
        # Add handlers
        self.dispatcher.add_handler(CommandHandler("start", self.start))
        self.dispatcher.add_handler(CommandHandler("help", self.help_command))
        
        # Registration conversation handler
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('register', self.register)],
            states={
                NAME: [MessageHandler(Filters.text & ~Filters.command, self.name)],
                EMAIL: [MessageHandler(Filters.text & ~Filters.command, self.email)],
                PHONE: [MessageHandler(Filters.text & ~Filters.command, self.phone)],
                LOCATION: [MessageHandler(Filters.text & ~Filters.command, self.location)],
                COUNTRY: [CallbackQueryHandler(self.country)],
                PASSWORD: [MessageHandler(Filters.text & ~Filters.command, self.password)],
                CONFIRM_PASSWORD: [MessageHandler(Filters.text & ~Filters.command, self.confirm_password)]
            },
            fallbacks=[CommandHandler('cancel', self.cancel)]
        )
        self.dispatcher.add_handler(conv_handler)
        
        # Error handler
        self.dispatcher.add_error_handler(self.error_handler)
    
    def start(self, update: Update, context: CallbackContext):
        """Start command handler"""
        update.message.reply_text(
            "Welcome to JBC Registration Bot! 🎉\n\n"
            "I can help you register for the JARAR BROADCASTING CORPORATION news system.\n\n"
            "Commands:\n"
            "/register - Start registration process\n"
            "/help - Show help message\n"
            "/cancel - Cancel current operation"
        )
    
    def help_command(self, update: Update, context: CallbackContext):
        """Help command handler"""
        update.message.reply_text(
            "JBC Registration Bot Help 📖\n\n"
            "Commands:\n"
            "/register - Start registration process\n"
            "/help - Show this help message\n"
            "/cancel - Cancel current operation\n\n"
            "During registration, you will be asked to provide:\n"
            "- Username\n"
            "- Email\n"
            "- Phone number\n"
            "- Location\n"
            "- Country\n"
            "- Password\n\n"
            "After registration, you can use the JBC News Bot to receive personalized news."
        )
    
    def register(self, update: Update, context: CallbackContext):
        """Start registration process"""
        chat_id = str(update.effective_chat.id)
        
        # Check if user already exists
        telegram_chat = TelegramChat.query.filter_by(chat_id=chat_id).first()
        if telegram_chat and telegram_chat.is_registered:
            update.message.reply_text(
                "You are already registered! 👍\n"
                "Use the JBC News Bot to receive personalized news."
            )
            return ConversationHandler.END
        
        # Create or update telegram chat record
        if not telegram_chat:
            telegram_chat = TelegramChat(chat_id=chat_id, registration_step="name")
            db.session.add(telegram_chat)
        else:
            telegram_chat.registration_step = "name"
            telegram_chat.temp_data = json.dumps({})
        
        db.session.commit()
        
        update.message.reply_text(
            "Let's start your registration! 📝\n\n"
            "Please enter your username:"
        )
        
        return NAME
    
    def name(self, update: Update, context: CallbackContext):
        """Process username"""
        chat_id = str(update.effective_chat.id)
        username = update.message.text.strip()
        
        # Validate username
        if len(username) < 4:
            update.message.reply_text(
                "Username must be at least 4 characters long. Please try again:"
            )
            return NAME
        
        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            update.message.reply_text(
                "This username is already taken. Please choose another one:"
            )
            return NAME
        
        # Update temp data
        telegram_chat = TelegramChat.query.filter_by(chat_id=chat_id).first()
        temp_data = telegram_chat.get_temp_data()
        temp_data['username'] = username
        telegram_chat.set_temp_data(temp_data)
        telegram_chat.registration_step = "email"
        db.session.commit()
        
        update.message.reply_text(
            f"Great, {username}! 👍\n\n"
            "Now, please enter your email address:"
        )
        
        return EMAIL
    
    def email(self, update: Update, context: CallbackContext):
        """Process email"""
        chat_id = str(update.effective_chat.id)
        email = update.message.text.strip()
        
        # Validate email
        import re
        email_pattern = re.compile(r"[^@]+@[^@]+\.[^@]+")
        if not email_pattern.match(email):
            update.message.reply_text(
                "Please enter a valid email address:"
            )
            return EMAIL
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            update.message.reply_text(
                "This email is already registered. Please use another one:"
            )
            return EMAIL
        
        # Update temp data
        telegram_chat = TelegramChat.query.filter_by(chat_id=chat_id).first()
        temp_data = telegram_chat.get_temp_data()
        temp_data['email'] = email
        telegram_chat.set_temp_data(temp_data)
        telegram_chat.registration_step = "phone"
        db.session.commit()
        
        update.message.reply_text(
            "Great! 📧\n\n"
            "Now, please enter your phone number (include country code):"
        )
        
        return PHONE
    
    def phone(self, update: Update, context: CallbackContext):
        """Process phone number"""
        chat_id = str(update.effective_chat.id)
        phone = update.message.text.strip()
        
        # Validate phone (simple validation)
        import re
        phone_pattern = re.compile(r"^\+?[0-9]{10,15}$")
        if not phone_pattern.match(phone):
            update.message.reply_text(
                "Please enter a valid phone number (10-15 digits, may include + prefix):"
            )
            return PHONE
        
        # Update temp data
        telegram_chat = TelegramChat.query.filter_by(chat_id=chat_id).first()
        temp_data = telegram_chat.get_temp_data()
        temp_data['phone'] = phone
        telegram_chat.set_temp_data(temp_data)
        telegram_chat.registration_step = "location"
        db.session.commit()
        
        update.message.reply_text(
            "Good! 📱\n\n"
            "Now, please enter your city/location:"
        )
        
        return LOCATION
    
    def location(self, update: Update, context: CallbackContext):
        """Process location"""
        chat_id = str(update.effective_chat.id)
        location = update.message.text.strip()
        
        # Update temp data
        telegram_chat = TelegramChat.query.filter_by(chat_id=chat_id).first()
        temp_data = telegram_chat.get_temp_data()
        temp_data['location'] = location
        telegram_chat.set_temp_data(temp_data)
        telegram_chat.registration_step = "country"
        db.session.commit()
        
        # Create keyboard with country options
        countries = Country.query.all()
        keyboard = []
        row = []
        for i, country in enumerate(countries):
            if i > 0 and i % 2 == 0:  # Two countries per row
                keyboard.append(row)
                row = []
            row.append(InlineKeyboardButton(country.name, callback_data=str(country.id)))
        
        if row:  # Add remaining buttons
            keyboard.append(row)
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            "Almost there! 🌍\n\n"
            "Please select your country:",
            reply_markup=reply_markup
        )
        
        return COUNTRY
    
    def country(self, update: Update, context: CallbackContext):
        """Process country selection"""
        query = update.callback_query
        query.answer()
        
        chat_id = str(query.message.chat_id)
        country_id = int(query.data)
        
        # Get country name for display
        country = Country.query.get(country_id)
        
        # Update temp data
        telegram_chat = TelegramChat.query.filter_by(chat_id=chat_id).first()
        temp_data = telegram_chat.get_temp_data()
        temp_data['country_id'] = country_id
        telegram_chat.set_temp_data(temp_data)
        telegram_chat.registration_step = "password"
        db.session.commit()
        
        query.edit_message_text(
            f"Country selected: {country.name} 🏳️\n\n"
            "Now, please enter a secure password (at least 8 characters):"
        )
        
        return PASSWORD
    
    def password(self, update: Update, context: CallbackContext):
        """Process password"""
        chat_id = str(update.effective_chat.id)
        password = update.message.text.strip()
        
        # Delete the message containing the password for security
        context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
        
        # Validate password
        if len(password) < 8:
            update.message.reply_text(
                "Password must be at least 8 characters long. Please try again:"
            )
            return PASSWORD
        
        # Update temp data
        telegram_chat = TelegramChat.query.filter_by(chat_id=chat_id).first()
        temp_data = telegram_chat.get_temp_data()
        temp_data['password'] = password
        telegram_chat.set_temp_data(temp_data)
        telegram_chat.registration_step = "confirm_password"
        db.session.commit()
        
        update.message.reply_text(
            "Good choice! 🔒\n\n"
            "Please confirm your password by entering it again:"
        )
        
        return CONFIRM_PASSWORD
    
    def confirm_password(self, update: Update, context: CallbackContext):
        """Process password confirmation and complete registration"""
        chat_id = str(update.effective_chat.id)
        confirm_password = update.message.text.strip()
        
        # Delete the message containing the password for security
        context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
        
        # Get temp data
        telegram_chat = TelegramChat.query.filter_by(chat_id=chat_id).first()
        temp_data = telegram_chat.get_temp_data()
        
        # Check if passwords match
        if confirm_password != temp_data.get('password'):
            update.message.reply_text(
                "Passwords do not match. Please enter your password again:"
            )
            return PASSWORD
        
        try:
            # Create new user
            user = User(
                username=temp_data.get('username'),
                email=temp_data.get('email'),
                password_hash=generate_password_hash(temp_data.get('password')),
                phone=temp_data.get('phone'),
                location=temp_data.get('location'),
                country_id=temp_data.get('country_id'),
                role=Role.USER,
                profile_photo_url=get_random_profile_image(),
                telegram_id=chat_id,
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.session.add(user)
            
            # Update telegram chat record
            telegram_chat.is_registered = True
            telegram_chat.user_id = user.id
            telegram_chat.temp_data = None  # Clear temp data for security
            
            db.session.commit()
            
            update.message.reply_text(
                f"🎉 Congratulations, {user.username}! 🎉\n\n"
                "Your registration is complete! You can now:\n\n"
                "1. Log in to the JBC website with your email and password\n"
                "2. Use the JBC News Bot to receive personalized news\n"
                "3. Contact support through the Support Bot if needed\n\n"
                "Thank you for joining JARAR BROADCASTING CORPORATION!"
            )
            
            return ConversationHandler.END
            
        except Exception as e:
            logger.error(f"Error during registration: {str(e)}")
            db.session.rollback()
            
            update.message.reply_text(
                "Sorry, there was an error during registration. Please try again later or contact support."
            )
            
            return ConversationHandler.END
    
    def cancel(self, update: Update, context: CallbackContext):
        """Cancel conversation"""
        update.message.reply_text(
            "Registration cancelled. You can start again anytime with /register."
        )
        return ConversationHandler.END
    
    def error_handler(self, update, context):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
        try:
            if update and update.effective_message:
                update.effective_message.reply_text(
                    "Sorry, an error occurred. Please try again later or contact support."
                )
        except:
            pass
    
    def start_bot(self):
        """Start the bot"""
        if not REGISTRATION_BOT_TOKEN:
            logger.error("REGISTRATION_BOT_TOKEN is not set")
            return
            
        self.updater.start_polling()
        logger.info("Registration Bot started")

class SupportBot:
    """Bot for handling support tickets"""
    
    def __init__(self):
        if not SUPPORT_BOT_TOKEN:
            logger.error("SUPPORT_BOT_TOKEN is not set")
            return
            
        self.updater = Updater(token=SUPPORT_BOT_TOKEN)
        self.dispatcher = self.updater.dispatcher
        
        # Add handlers
        self.dispatcher.add_handler(CommandHandler("start", self.start))
        self.dispatcher.add_handler(CommandHandler("help", self.help_command))
        self.dispatcher.add_handler(CommandHandler("faq", self.faq))
        self.dispatcher.add_handler(CommandHandler("ticket", self.create_ticket))
        self.dispatcher.add_handler(CommandHandler("status", self.ticket_status))
        
        # Message handler for ticket creation flow
        self.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.handle_message))
        
        # Error handler
        self.dispatcher.add_error_handler(self.error_handler)
    
    def start(self, update: Update, context: CallbackContext):
        """Start command handler"""
        update.message.reply_text(
            "Welcome to JBC Support Bot! 🎉\n\n"
            "I can help you with frequently asked questions and support tickets.\n\n"
            "Commands:\n"
            "/faq - Show frequently asked questions\n"
            "/ticket - Create a new support ticket\n"
            "/status - Check your ticket status\n"
            "/help - Show help message"
        )
    
    def help_command(self, update: Update, context: CallbackContext):
        """Help command handler"""
        update.message.reply_text(
            "JBC Support Bot Help 📖\n\n"
            "Commands:\n"
            "/start - Start the bot\n"
            "/faq - Show frequently asked questions\n"
            "/ticket - Create a new support ticket\n"
            "/status - Check your ticket status\n"
            "/help - Show this help message\n\n"
            "For any other questions, create a support ticket using /ticket command."
        )
    
    def faq(self, update: Update, context: CallbackContext):
        """Show FAQ"""
        faqs = [
            {
                "question": "How do I register for JBC News?",
                "answer": "You can register using our Registration Bot or through our website."
            },
            {
                "question": "How often is news updated?",
                "answer": "News is updated every 30 minutes from various sources."
            },
            {
                "question": "How can I change my country setting?",
                "answer": "Log in to your account on the website and update your profile settings."
            },
            {
                "question": "Is the service free to use?",
                "answer": "Yes, JBC News is completely free to use."
            },
            {
                "question": "How do I receive breaking news alerts?",
                "answer": "Breaking news alerts are automatically sent to all users through the News Bot."
            }
        ]
        
        message = "📋 Frequently Asked Questions:\n\n"
        for i, faq in enumerate(faqs, 1):
            message += f"{i}. Q: {faq['question']}\n   A: {faq['answer']}\n\n"
        
        message += "If your question isn't answered here, create a support ticket using /ticket command."
        
        update.message.reply_text(message)
    
    def create_ticket(self, update: Update, context: CallbackContext):
        """Start ticket creation process"""
        chat_id = str(update.effective_chat.id)
        
        # Check if user is registered
        telegram_chat = TelegramChat.query.filter_by(chat_id=chat_id).first()
        if not telegram_chat or not telegram_chat.is_registered:
            update.message.reply_text(
                "You need to register first! 📝\n\n"
                "Please use the Registration Bot to create an account."
            )
            return
        
        # Update status to ticket creation
        telegram_chat.registration_step = "ticket_subject"
        db.session.commit()
        
        update.message.reply_text(
            "Let's create a support ticket! 🎫\n\n"
            "First, please enter a brief subject for your ticket:"
        )
    
    def handle_message(self, update: Update, context: CallbackContext):
        """Handle incoming messages based on context"""
        chat_id = str(update.effective_chat.id)
        message = update.message.text
        
        # Check user and registration step
        telegram_chat = TelegramChat.query.filter_by(chat_id=chat_id).first()
        if not telegram_chat:
            update.message.reply_text(
                "You need to register first! 📝\n\n"
                "Please use the Registration Bot to create an account."
            )
            return
        
        step = telegram_chat.registration_step
        
        if step == "ticket_subject":
            # Store ticket subject
            temp_data = telegram_chat.get_temp_data() or {}
            temp_data['ticket_subject'] = message
            telegram_chat.set_temp_data(temp_data)
            telegram_chat.registration_step = "ticket_description"
            db.session.commit()
            
            update.message.reply_text(
                "Great! Now, please provide a detailed description of your issue:"
            )
            
        elif step == "ticket_description":
            # Create support ticket
            try:
                temp_data = telegram_chat.get_temp_data() or {}
                subject = temp_data.get('ticket_subject', 'Support Request')
                
                # Create ticket
                ticket = Support(
                    user_id=telegram_chat.user_id,
                    ticket_id=f"TKT-{generate_unique_id(6)}",
                    subject=subject,
                    message=message,
                    status="open",
                    created_at=datetime.utcnow()
                )
                db.session.add(ticket)
                
                # Reset chat state
                telegram_chat.registration_step = None
                telegram_chat.temp_data = None
                db.session.commit()
                
                update.message.reply_text(
                    f"✅ Support ticket created successfully!\n\n"
                    f"Ticket ID: {ticket.ticket_id}\n"
                    f"Subject: {subject}\n"
                    f"Status: Open\n\n"
                    f"Our support team will get back to you soon. You can check the status of your ticket using /status command."
                )
                
            except Exception as e:
                logger.error(f"Error creating support ticket: {str(e)}")
                db.session.rollback()
                
                update.message.reply_text(
                    "Sorry, there was an error creating your ticket. Please try again later."
                )
                
        else:
            # General message, provide help
            update.message.reply_text(
                "👋 Hi there! Here's what I can help you with:\n\n"
                "/faq - Frequently asked questions\n"
                "/ticket - Create a support ticket\n"
                "/status - Check your ticket status\n"
                "/help - Show all commands"
            )
    
    def ticket_status(self, update: Update, context: CallbackContext):
        """Check ticket status"""
        chat_id = str(update.effective_chat.id)
        
        # Check if user is registered
        telegram_chat = TelegramChat.query.filter_by(chat_id=chat_id).first()
        if not telegram_chat or not telegram_chat.is_registered:
            update.message.reply_text(
                "You need to register first! 📝\n\n"
                "Please use the Registration Bot to create an account."
            )
            return
        
        # Get user's tickets
        tickets = Support.query.filter_by(user_id=telegram_chat.user_id).order_by(Support.created_at.desc()).limit(5).all()
        
        if not tickets:
            update.message.reply_text(
                "You don't have any support tickets. Use /ticket to create one."
            )
            return
        
        message = "🎫 Your support tickets:\n\n"
        for ticket in tickets:
            status_emoji = "🟢" if ticket.status == "open" else "🟡" if ticket.status == "in_progress" else "🔴"
            created_date = ticket.created_at.strftime("%d %b %Y")
            
            message += f"ID: {ticket.ticket_id}\n"
            message += f"Subject: {ticket.subject}\n"
            message += f"Status: {status_emoji} {ticket.status.replace('_', ' ').title()}\n"
            message += f"Created: {created_date}\n\n"
        
        message += "To create a new ticket, use /ticket command."
        
        update.message.reply_text(message)
    
    def error_handler(self, update, context):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
        try:
            if update and update.effective_message:
                update.effective_message.reply_text(
                    "Sorry, an error occurred. Please try again later."
                )
        except:
            pass
    
    def start_bot(self):
        """Start the bot"""
        if not SUPPORT_BOT_TOKEN:
            logger.error("SUPPORT_BOT_TOKEN is not set")
            return
            
        self.updater.start_polling()
        logger.info("Support Bot started")

class NewsBot:
    """Bot for delivering personalized news"""
    
    def __init__(self):
        if not NEWS_BOT_TOKEN:
            logger.error("NEWS_BOT_TOKEN is not set")
            return
            
        self.updater = Updater(token=NEWS_BOT_TOKEN)
        self.dispatcher = self.updater.dispatcher
        
        # Add handlers
        self.dispatcher.add_handler(CommandHandler("start", self.start))
        self.dispatcher.add_handler(CommandHandler("help", self.help_command))
        self.dispatcher.add_handler(CommandHandler("news", self.get_latest_news))
        self.dispatcher.add_handler(CommandHandler("breaking", self.get_breaking_news))
        self.dispatcher.add_handler(CommandHandler("category", self.select_category))
        self.dispatcher.add_handler(CommandHandler("profile", self.show_profile))
        
        # Callback handlers
        self.dispatcher.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Error handler
        self.dispatcher.add_error_handler(self.error_handler)
        
        # Schedule job to send daily news digest
        scheduler.add_job(id='daily_news_digest', func=self.send_daily_digest, trigger='cron', hour=8, minute=0)
    
    def start(self, update: Update, context: CallbackContext):
        """Start command handler"""
        chat_id = str(update.effective_chat.id)
        
        # Check if user is registered
        telegram_chat = TelegramChat.query.filter_by(chat_id=chat_id).first()
        if not telegram_chat or not telegram_chat.is_registered:
            keyboard = [
                [InlineKeyboardButton("Register Now", url="https://t.me/jbc_registration_bot")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            update.message.reply_text(
                "Welcome to JBC News Bot! 📰\n\n"
                "You're not registered yet. Please register to receive personalized news.",
                reply_markup=reply_markup
            )
            return
        
        # Get user
        user = User.query.get(telegram_chat.user_id)
        if not user:
            update.message.reply_text(
                "Sorry, there seems to be an issue with your account. Please contact support."
            )
            return
        
        # Send welcome message
        update.message.reply_text(
            f"Welcome to JBC News Bot, {user.username}! 📰\n\n"
            f"You will receive personalized news based on your country ({user.country.name if user.country else 'Global'}).\n\n"
            "Commands:\n"
            "/news - Get latest news\n"
            "/breaking - Get breaking news\n"
            "/category - Browse news by category\n"
            "/profile - View your profile\n"
            "/help - Show help message"
        )
        
        # Send latest news after welcome message
        self.send_latest_news(chat_id, limit=3)
    
    def help_command(self, update: Update, context: CallbackContext):
        """Help command handler"""
        update.message.reply_text(
            "JBC News Bot Help 📖\n\n"
            "Commands:\n"
            "/start - Start the bot\n"
            "/news - Get latest news\n"
            "/breaking - Get breaking news\n"
            "/category - Browse news by category\n"
            "/profile - View your profile\n"
            "/help - Show this help message\n\n"
            "You will automatically receive breaking news alerts and a daily news digest."
        )
    
    def get_latest_news(self, update: Update, context: CallbackContext):
        """Get latest news command handler"""
        chat_id = str(update.effective_chat.id)
        
        # Check if user is registered
        telegram_chat = TelegramChat.query.filter_by(chat_id=chat_id).first()
        if not telegram_chat or not telegram_chat.is_registered:
            update.message.reply_text(
                "You need to register first to get personalized news! Please use the Registration Bot."
            )
            return
        
        # Send news
        update.message.reply_text("Fetching your latest news... 🔍")
        count = self.send_latest_news(chat_id)
        
        if count == 0:
            update.message.reply_text(
                "No news articles found. Please try again later or change your preferences."
            )
    
    def get_breaking_news(self, update: Update, context: CallbackContext):
        """Get breaking news command handler"""
        chat_id = str(update.effective_chat.id)
        
        # Check if user is registered
        telegram_chat = TelegramChat.query.filter_by(chat_id=chat_id).first()
        if not telegram_chat or not telegram_chat.is_registered:
            update.message.reply_text(
                "You need to register first to get breaking news! Please use the Registration Bot."
            )
            return
        
        # Get user
        user = User.query.get(telegram_chat.user_id)
        
        # Query breaking news
        breaking_news = News.query.filter_by(
            is_breaking=True,
            is_published=True
        ).order_by(News.published_at.desc()).limit(5).all()
        
        if not breaking_news:
            update.message.reply_text("No breaking news at the moment. Check back later!")
            return
        
        update.message.reply_text("🔴 BREAKING NEWS 🔴")
        
        # Send breaking news
        count = 0
        for news in breaking_news:
            try:
                # Get translation if available and user is not from news country
                translated = None
                if user.country and news.country and user.country.id != news.country.id:
                    if news.translations:
                        translations = json.loads(news.translations)
                        if user.country.code == 'IN':
                            translated = translations.get('hi')  # Hindi
                        elif user.country.code == 'PK':
                            translated = translations.get('ur')  # Urdu
                        elif user.country.code == 'SA':
                            translated = translations.get('ar')  # Arabic
                        elif user.country.code == 'LK':
                            translated = translations.get('si')  # Sinhala
                
                # Prepare message
                title = translated.get('title') if translated else news.title
                summary = translated.get('summary') if translated else news.summary
                
                message = f"*{title}*\n\n{summary}\n\n"
                if news.source_url:
                    message += f"[Read more]({news.source_url})"
                
                # Send with image if available
                if news.image_url:
                    context.bot.send_photo(
                        chat_id=chat_id,
                        photo=news.image_url,
                        caption=message,
                        parse_mode=telegram.ParseMode.MARKDOWN
                    )
                else:
                    context.bot.send_message(
                        chat_id=chat_id,
                        text=message,
                        parse_mode=telegram.ParseMode.MARKDOWN,
                        disable_web_page_preview=False
                    )
                
                count += 1
            except Exception as e:
                logger.error(f"Error sending breaking news: {str(e)}")
        
        if count == 0:
            update.message.reply_text("Failed to retrieve breaking news. Please try again later.")
    
    def select_category(self, update: Update, context: CallbackContext):
        """Select news category"""
        # Get all categories
        categories = Category.query.order_by(Category.name).all()
        
        # Create inline keyboard
        keyboard = []
        row = []
        for i, category in enumerate(categories):
            if i > 0 and i % 2 == 0:  # Two categories per row
                keyboard.append(row)
                row = []
            row.append(InlineKeyboardButton(category.name, callback_data=f"category_{category.id}"))
        
        if row:  # Add remaining buttons
            keyboard.append(row)
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            "📂 Select a news category:",
            reply_markup=reply_markup
        )
    
    def show_profile(self, update: Update, context: CallbackContext):
        """Show user profile"""
        chat_id = str(update.effective_chat.id)
        
        # Check if user is registered
        telegram_chat = TelegramChat.query.filter_by(chat_id=chat_id).first()
        if not telegram_chat or not telegram_chat.is_registered:
            update.message.reply_text(
                "You need to register first! Please use the Registration Bot."
            )
            return
        
        # Get user
        user = User.query.get(telegram_chat.user_id)
        if not user:
            update.message.reply_text(
                "Sorry, there seems to be an issue with your account. Please contact support."
            )
            return
        
        # Format profile information
        profile = f"👤 *Your Profile*\n\n"
        profile += f"*Username:* {user.username}\n"
        profile += f"*Email:* {user.email}\n"
        profile += f"*Phone:* {user.phone}\n"
        profile += f"*Location:* {user.location}\n"
        profile += f"*Country:* {user.country.name if user.country else 'Not set'}\n"
        profile += f"*Joined:* {user.created_at.strftime('%d %b %Y')}\n\n"
        
        profile += "To update your profile, please visit the JBC website."
        
        # Send profile
        if user.profile_photo_url:
            context.bot.send_photo(
                chat_id=chat_id,
                photo=user.profile_photo_url,
                caption=profile,
                parse_mode=telegram.ParseMode.MARKDOWN
            )
        else:
            update.message.reply_text(
                profile,
                parse_mode=telegram.ParseMode.MARKDOWN
            )
    
    def send_latest_news(self, chat_id, limit=5):
        """Send latest news to a chat"""
        try:
            # Get user
            telegram_chat = TelegramChat.query.filter_by(chat_id=chat_id).first()
            if not telegram_chat or not telegram_chat.is_registered:
                return 0
            
            user = User.query.get(telegram_chat.user_id)
            if not user or not user.country:
                return 0
            
            # Query latest news for user's country
            country_news = News.query.filter_by(
                country_id=user.country.id,
                is_published=True
            ).order_by(News.published_at.desc()).limit(limit).all()
            
            # Send news
            count = 0
            for news in country_news:
                try:
                    # Get translation if available
                    translated = None
                    if news.translations:
                        translations = json.loads(news.translations)
                        if user.country.code == 'IN':
                            translated = translations.get('hi')  # Hindi
                        elif user.country.code == 'PK':
                            translated = translations.get('ur')  # Urdu
                        elif user.country.code == 'SA':
                            translated = translations.get('ar')  # Arabic
                        elif user.country.code == 'LK':
                            translated = translations.get('si')  # Sinhala
                    
                    # Prepare message
                    title = translated.get('title') if translated else news.title
                    summary = translated.get('summary') if translated else news.summary
                    
                    message = f"*{title}*\n\n{summary}\n\n"
                    if news.source_url:
                        message += f"[Read more]({news.source_url})"
                    
                    # Send with image if available
                    bot = telegram.Bot(token=NEWS_BOT_TOKEN)
                    if news.image_url:
                        bot.send_photo(
                            chat_id=chat_id,
                            photo=news.image_url,
                            caption=message,
                            parse_mode=telegram.ParseMode.MARKDOWN
                        )
                    else:
                        bot.send_message(
                            chat_id=chat_id,
                            text=message,
                            parse_mode=telegram.ParseMode.MARKDOWN,
                            disable_web_page_preview=False
                        )
                    
                    count += 1
                except Exception as e:
                    logger.error(f"Error sending news: {str(e)}")
            
            return count
            
        except Exception as e:
            logger.error(f"Error in send_latest_news: {str(e)}")
            return 0
    
    def send_news_by_category(self, chat_id, category_id):
        """Send news of a specific category"""
        try:
            # Get user
            telegram_chat = TelegramChat.query.filter_by(chat_id=chat_id).first()
            if not telegram_chat or not telegram_chat.is_registered:
                return 0
            
            user = User.query.get(telegram_chat.user_id)
            
            # Query news for category
            category_news = News.query.filter_by(
                category_id=category_id,
                is_published=True
            ).order_by(News.published_at.desc()).limit(5).all()
            
            if not category_news:
                bot = telegram.Bot(token=NEWS_BOT_TOKEN)
                bot.send_message(chat_id=chat_id, text="No news found in this category. Please try another category.")
                return 0
            
            # Get category name
            category = Category.query.get(category_id)
            
            # Send category header
            bot = telegram.Bot(token=NEWS_BOT_TOKEN)
            bot.send_message(
                chat_id=chat_id,
                text=f"📂 *{category.name} News*",
                parse_mode=telegram.ParseMode.MARKDOWN
            )
            
            # Send news
            count = 0
            for news in category_news:
                try:
                    # Get translation if available and user is not from news country
                    translated = None
                    if user.country and news.country and user.country.id != news.country.id:
                        if news.translations:
                            translations = json.loads(news.translations)
                            if user.country.code == 'IN':
                                translated = translations.get('hi')  # Hindi
                            elif user.country.code == 'PK':
                                translated = translations.get('ur')  # Urdu
                            elif user.country.code == 'SA':
                                translated = translations.get('ar')  # Arabic
                            elif user.country.code == 'LK':
                                translated = translations.get('si')  # Sinhala
                    
                    # Prepare message
                    title = translated.get('title') if translated else news.title
                    summary = translated.get('summary') if translated else news.summary
                    
                    message = f"*{title}*\n\n{summary}\n\n"
                    if news.source_url:
                        message += f"[Read more]({news.source_url})"
                    
                    # Send with image if available
                    if news.image_url:
                        bot.send_photo(
                            chat_id=chat_id,
                            photo=news.image_url,
                            caption=message,
                            parse_mode=telegram.ParseMode.MARKDOWN
                        )
                    else:
                        bot.send_message(
                            chat_id=chat_id,
                            text=message,
                            parse_mode=telegram.ParseMode.MARKDOWN,
                            disable_web_page_preview=False
                        )
                    
                    count += 1
                except Exception as e:
                    logger.error(f"Error sending category news: {str(e)}")
            
            return count
            
        except Exception as e:
            logger.error(f"Error in send_news_by_category: {str(e)}")
            return 0
    
    def send_daily_digest(self):
        """Send daily news digest to all users"""
        try:
            logger.info("Sending daily news digest")
            
            # Update news database first
            fetch_all_news()
            
            # Get all registered users with telegram ID
            telegram_chats = TelegramChat.query.filter(
                TelegramChat.is_registered == True,
                TelegramChat.user_id.isnot(None)
            ).all()
            
            bot = telegram.Bot(token=NEWS_BOT_TOKEN)
            
            for chat in telegram_chats:
                try:
                    # Get user
                    user = User.query.get(chat.user_id)
                    if not user or not user.is_active:
                        continue
                    
                    # Send greeting with digest
                    current_time = datetime.utcnow()
                    greeting = "Good morning" if 5 <= current_time.hour < 12 else "Good afternoon" if 12 <= current_time.hour < 18 else "Good evening"
                    
                    bot.send_message(
                        chat_id=chat.chat_id,
                        text=f"📰 *{greeting}, {user.username}!*\n\nHere's your daily news digest from JBC News:",
                        parse_mode=telegram.ParseMode.MARKDOWN
                    )
                    
                    # Send news
                    self.send_latest_news(chat.chat_id, limit=3)
                    
                except Exception as e:
                    logger.error(f"Error sending digest to {chat.chat_id}: {str(e)}")
            
            logger.info("Daily news digest sent successfully")
            
        except Exception as e:
            logger.error(f"Error in send_daily_digest: {str(e)}")
    
    def button_callback(self, update: Update, context: CallbackContext):
        """Handle button callbacks"""
        query = update.callback_query
        query.answer()
        
        # Get callback data
        data = query.data
        chat_id = str(query.message.chat_id)
        
        if data.startswith("category_"):
            # Extract category ID from callback data
            category_id = int(data.split("_")[1])
            
            # Send news for this category
            query.edit_message_text(text=f"Fetching news for the selected category... 🔍")
            count = self.send_news_by_category(chat_id, category_id)
            
            if count == 0:
                context.bot.send_message(
                    chat_id=chat_id,
                    text="No news found in this category. Please try another category."
                )
    
    def error_handler(self, update, context):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
        try:
            if update and update.effective_message:
                update.effective_message.reply_text(
                    "Sorry, an error occurred. Please try again later."
                )
        except:
            pass
    
    def start_bot(self):
        """Start the bot"""
        if not NEWS_BOT_TOKEN:
            logger.error("NEWS_BOT_TOKEN is not set")
            return
            
        self.updater.start_polling()
        logger.info("News Bot started")

class StaffBot:
    """Bot for staff management and news posting"""
    
    def __init__(self):
        if not STAFF_BOT_TOKEN:
            logger.error("STAFF_BOT_TOKEN is not set")
            return
            
        self.updater = Updater(token=STAFF_BOT_TOKEN)
        self.dispatcher = self.updater.dispatcher
        
        # Add handlers
        self.dispatcher.add_handler(CommandHandler("start", self.start))
        self.dispatcher.add_handler(CommandHandler("help", self.help_command))
        self.dispatcher.add_handler(CommandHandler("login", self.login))
        self.dispatcher.add_handler(CommandHandler("addnews", self.add_news))
        self.dispatcher.add_handler(CommandHandler("newslist", self.news_list))
        self.dispatcher.add_handler(CommandHandler("breaking", self.breaking_news))
        self.dispatcher.add_handler(CommandHandler("translate", self.translate_news))
        self.dispatcher.add_handler(CommandHandler("publish", self.publish_news))
        self.dispatcher.add_handler(CommandHandler("unpublish", self.unpublish_news))
        
        # Message handlers for conversation flows
        self.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.handle_message))
        
        # Error handler
        self.dispatcher.add_error_handler(self.error_handler)
    
    def start(self, update: Update, context: CallbackContext):
        """Start command handler"""
        update.message.reply_text(
            "Welcome to JBC Staff Bot! 👔\n\n"
            "This bot is for JBC staff members to manage news content.\n\n"
            "Commands:\n"
            "/login - Authenticate as staff\n"
            "/addnews - Add new article\n"
            "/newslist - List recent news\n"
            "/breaking - Mark news as breaking\n"
            "/translate - Translate news\n"
            "/help - Show help message"
        )
    
    def help_command(self, update: Update, context: CallbackContext):
        """Help command handler"""
        update.message.reply_text(
            "JBC Staff Bot Help 📖\n\n"
            "Commands:\n"
            "/start - Start the bot\n"
            "/login - Authenticate as staff\n"
            "/addnews - Add new article\n"
            "/newslist - List recent news\n"
            "/breaking - Mark news as breaking\n"
            "/translate - Translate news\n"
            "/publish - Publish a news article\n"
            "/unpublish - Unpublish a news article\n"
            "/help - Show this help message\n\n"
            "This bot is only for authorized JBC staff members."
        )
    
    def login(self, update: Update, context: CallbackContext):
        """Staff login handler"""
        # Implementation for staff login would go here
        pass
    
    def add_news(self, update: Update, context: CallbackContext):
        """Add news command handler"""
        # Implementation for adding news would go here
        pass
    
    def news_list(self, update: Update, context: CallbackContext):
        """List news command handler"""
        # Implementation for listing news would go here
        pass
    
    def breaking_news(self, update: Update, context: CallbackContext):
        """Breaking news command handler"""
        # Implementation for breaking news would go here
        pass
    
    def translate_news(self, update: Update, context: CallbackContext):
        """Translate news command handler"""
        # Implementation for translating news would go here
        pass
    
    def publish_news(self, update: Update, context: CallbackContext):
        """Publish news command handler"""
        # Implementation for publishing news would go here
        pass
    
    def unpublish_news(self, update: Update, context: CallbackContext):
        """Unpublish news command handler"""
        # Implementation for unpublishing news would go here
        pass
    
    def handle_message(self, update: Update, context: CallbackContext):
        """Handle incoming messages based on context"""
        # Implementation for handling messages would go here
        pass
    
    def error_handler(self, update, context):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
        try:
            if update and update.effective_message:
                update.effective_message.reply_text(
                    "Sorry, an error occurred. Please try again later."
                )
        except:
            pass
    
    def start_bot(self):
        """Start the bot"""
        if not STAFF_BOT_TOKEN:
            logger.error("STAFF_BOT_TOKEN is not set")
            return
            
        self.updater.start_polling()
        logger.info("Staff Bot started")

def init_telegram_bots():
    """Initialize and start all Telegram bots"""
    try:
        # Initialize bots
        registration_bot = RegistrationBot()
        support_bot = SupportBot()
        news_bot = NewsBot()
        staff_bot = StaffBot()
        
        # Start bots
        if REGISTRATION_BOT_TOKEN:
            registration_bot.start_bot()
        if SUPPORT_BOT_TOKEN:
            support_bot.start_bot()
        if NEWS_BOT_TOKEN:
            news_bot.start_bot()
        if STAFF_BOT_TOKEN:
            staff_bot.start_bot()
            
        logger.info("Telegram bots initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing Telegram bots: {str(e)}")

# Initialize bots when imported
if __name__ != "__main__":
    # Only initialize bots if any token is set
    if any([REGISTRATION_BOT_TOKEN, SUPPORT_BOT_TOKEN, NEWS_BOT_TOKEN, STAFF_BOT_TOKEN]):
        init_telegram_bots()
