#!/usr/bin/env python
"""
JBC News Telegram Bot Service
----------------------------
This is a simplified service module for Telegram bots that will be run by a workflow.
It focuses on stability and uses a thread-based approach to handle multiple bots.
"""

import os
import sys
import logging
import threading
import time
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"telegram_service_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("TelegramService")

# Global variables to track bots
bots_running = True
bot_threads = []

class TelegramBot:
    """Base class for all Telegram bots"""
    def __init__(self, name, token_env_var):
        self.name = name
        self.token_env_var = token_env_var
        self.token = os.environ.get(token_env_var, "")
        self.updater = None
        self.thread = None
        self.running = False
    
    def start(self):
        """Start the bot in a thread"""
        if not self.token:
            logger.error(f"[{self.name}] No token found in environment variable {self.token_env_var}")
            return False
        
        try:
            self.thread = threading.Thread(target=self._run_bot)
            self.thread.daemon = True
            self.thread.start()
            return True
        except Exception as e:
            logger.error(f"[{self.name}] Failed to start thread: {e}")
            return False
    
    def _run_bot(self):
        """Run the bot (to be implemented by subclasses)"""
        raise NotImplementedError("Subclasses must implement this method")

class RegistrationBot(TelegramBot):
    """Bot for handling user registration"""
    def __init__(self):
        super().__init__("Registration Bot", "REGISTRATION_BOT_TOKEN")
    
    def _run_bot(self):
        """Run the registration bot"""
        try:
            # Import telegram modules
            import telegram
            from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
            
            # Set up the Updater
            self.updater = Updater(token=self.token)
            dispatcher = self.updater.dispatcher
            
            # Define command handlers
            def start(update, context):
                """Send a welcome message when the command /start is issued"""
                logger.info(f"[{self.name}] User {update.effective_user.id} started the bot")
                update.message.reply_text(f'Welcome to JBC News Registration Bot! Use /register to create an account.')
            
            def help_command(update, context):
                """Send a help message when the command /help is issued"""
                update.message.reply_text('I can help you register for JBC News. Use /register to begin.')
            
            def register_command(update, context):
                """Start the registration process"""
                update.message.reply_text('To register, please provide your email address:')
                context.user_data['registration_step'] = 'email'
            
            def handle_message(update, context):
                """Handle regular messages during registration process"""
                step = context.user_data.get('registration_step')
                if step == 'email':
                    # This is a simplified version - in reality you'd validate the email
                    email = update.message.text
                    context.user_data['email'] = email
                    update.message.reply_text(f'Email received: {email}\nNow, please provide your preferred username:')
                    context.user_data['registration_step'] = 'username'
                elif step == 'username':
                    username = update.message.text
                    context.user_data['username'] = username
                    update.message.reply_text(f'Thanks, {username}! Registration details have been saved.')
                    # Here you would normally save to database
                    context.user_data['registration_step'] = None
                else:
                    update.message.reply_text('I can help you register for JBC News. Use /register to begin.')
            
            # Add handlers
            dispatcher.add_handler(CommandHandler("start", start))
            dispatcher.add_handler(CommandHandler("help", help_command))
            dispatcher.add_handler(CommandHandler("register", register_command))
            dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
            
            # Start the Bot
            logger.info(f"[{self.name}] Starting polling...")
            self.running = True
            self.updater.start_polling()
            logger.info(f"[{self.name}] Bot is running!")
            
            # Run until bot is stopped manually
            while bots_running:
                time.sleep(1)
            
            logger.info(f"[{self.name}] Stopping the bot...")
            self.updater.stop()
            self.running = False
            
        except Exception as e:
            import traceback
            logger.error(f"[{self.name}] Error: {e}")
            logger.error(traceback.format_exc())
            self.running = False

class SupportBot(TelegramBot):
    """Bot for handling user support tickets"""
    def __init__(self):
        super().__init__("Support Bot", "SUPPORT_BOT_TOKEN")
    
    def _run_bot(self):
        """Run the support bot"""
        try:
            # Import telegram modules
            import telegram
            from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
            
            # Set up the Updater
            self.updater = Updater(token=self.token)
            dispatcher = self.updater.dispatcher
            
            # Define command handlers
            def start(update, context):
                """Send a welcome message when the command /start is issued"""
                logger.info(f"[{self.name}] User {update.effective_user.id} started the bot")
                update.message.reply_text(f'Welcome to JBC News Support Bot! Use /ticket to create a support ticket.')
            
            def help_command(update, context):
                """Send a help message when the command /help is issued"""
                update.message.reply_text('I can help you with support issues. Use /ticket to create a support ticket.')
            
            def ticket_command(update, context):
                """Start the ticket creation process"""
                update.message.reply_text('To create a support ticket, please provide a brief description of your issue:')
                context.user_data['ticket_step'] = 'description'
            
            def handle_message(update, context):
                """Handle regular messages during ticket creation process"""
                step = context.user_data.get('ticket_step')
                if step == 'description':
                    description = update.message.text
                    context.user_data['description'] = description
                    update.message.reply_text(f'Issue description received. Your ticket number is #ST{datetime.now().strftime("%Y%m%d%H%M")}.\n\nA support agent will contact you shortly.')
                    context.user_data['ticket_step'] = None
                else:
                    update.message.reply_text('I can help with support issues. Use /ticket to create a support ticket.')
            
            # Add handlers
            dispatcher.add_handler(CommandHandler("start", start))
            dispatcher.add_handler(CommandHandler("help", help_command))
            dispatcher.add_handler(CommandHandler("ticket", ticket_command))
            dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
            
            # Start the Bot
            logger.info(f"[{self.name}] Starting polling...")
            self.running = True
            self.updater.start_polling()
            logger.info(f"[{self.name}] Bot is running!")
            
            # Run until bot is stopped manually
            while bots_running:
                time.sleep(1)
            
            logger.info(f"[{self.name}] Stopping the bot...")
            self.updater.stop()
            self.running = False
            
        except Exception as e:
            import traceback
            logger.error(f"[{self.name}] Error: {e}")
            logger.error(traceback.format_exc())
            self.running = False

class NewsBot(TelegramBot):
    """Bot for sending news updates"""
    def __init__(self):
        super().__init__("News Bot", "NEWS_BOT_TOKEN")
    
    def _run_bot(self):
        """Run the news bot"""
        try:
            # Import telegram modules
            import telegram
            from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
            
            # Set up the Updater
            self.updater = Updater(token=self.token)
            dispatcher = self.updater.dispatcher
            
            # Define command handlers
            def start(update, context):
                """Send a welcome message when the command /start is issued"""
                logger.info(f"[{self.name}] User {update.effective_user.id} started the bot")
                update.message.reply_text(f'Welcome to JBC News Bot! Use /news to get the latest news updates.')
            
            def help_command(update, context):
                """Send a help message when the command /help is issued"""
                update.message.reply_text('I can send you news updates. Try the following commands:\n/news - Latest news\n/category - Browse by category\n/subscribe - Get news alerts')
            
            def news_command(update, context):
                """Send latest news"""
                update.message.reply_text('Here are the latest headlines:')
                # In a real implementation, these would be fetched from the database
                update.message.reply_text('1. Global markets rebound after recent slump')
                update.message.reply_text('2. New climate agreement reached at international summit')
                update.message.reply_text('3. Tech company announces breakthrough in AI research')
            
            def category_command(update, context):
                """Browse news by category"""
                keyboard = [
                    ['Politics', 'Business'],
                    ['Technology', 'Sports'],
                    ['Entertainment', 'Science']
                ]
                reply_markup = telegram.ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
                update.message.reply_text('Select a news category:', reply_markup=reply_markup)
            
            def handle_message(update, context):
                """Handle regular messages and category selection"""
                text = update.message.text
                categories = ['Politics', 'Business', 'Technology', 'Sports', 'Entertainment', 'Science']
                if text in categories:
                    update.message.reply_text(f'Here are the latest {text} headlines:')
                    update.message.reply_text(f'1. Sample {text} headline 1')
                    update.message.reply_text(f'2. Sample {text} headline 2')
                    update.message.reply_text(f'3. Sample {text} headline 3')
                else:
                    update.message.reply_text('I can send you news updates. Use /news to get the latest headlines.')
            
            # Add handlers
            dispatcher.add_handler(CommandHandler("start", start))
            dispatcher.add_handler(CommandHandler("help", help_command))
            dispatcher.add_handler(CommandHandler("news", news_command))
            dispatcher.add_handler(CommandHandler("category", category_command))
            dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
            
            # Start the Bot
            logger.info(f"[{self.name}] Starting polling...")
            self.running = True
            self.updater.start_polling()
            logger.info(f"[{self.name}] Bot is running!")
            
            # Run until bot is stopped manually
            while bots_running:
                time.sleep(1)
            
            logger.info(f"[{self.name}] Stopping the bot...")
            self.updater.stop()
            self.running = False
            
        except Exception as e:
            import traceback
            logger.error(f"[{self.name}] Error: {e}")
            logger.error(traceback.format_exc())
            self.running = False

class StaffBot(TelegramBot):
    """Bot for staff operations"""
    def __init__(self):
        super().__init__("Staff Bot", "STAFF_BOT_TOKEN")
    
    def _run_bot(self):
        """Run the staff bot"""
        try:
            # Import telegram modules
            import telegram
            from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
            
            # Set up the Updater
            self.updater = Updater(token=self.token)
            dispatcher = self.updater.dispatcher
            
            # Define conversation states
            TITLE, SUMMARY, CONTENT, CATEGORY, CONFIRM = range(5)
            
            # Define command handlers
            def start(update, context):
                """Send a welcome message when the command /start is issued"""
                logger.info(f"[{self.name}] User {update.effective_user.id} started the bot")
                update.message.reply_text(f'Welcome to JBC News Staff Bot! Use /addnews to add a new article.')
            
            def help_command(update, context):
                """Send a help message when the command /help is issued"""
                update.message.reply_text('I can help staff manage JBC News. Try:\n/addnews - Add a new article\n/stats - View site statistics')
            
            def start_add_news(update, context):
                """Start the add news conversation"""
                update.message.reply_text('Let\'s add a new article. First, what\'s the title?')
                return TITLE
            
            def add_title(update, context):
                """Store title and ask for summary"""
                context.user_data['title'] = update.message.text
                update.message.reply_text('Great! Now, please provide a brief summary:')
                return SUMMARY
            
            def add_summary(update, context):
                """Store summary and ask for content"""
                context.user_data['summary'] = update.message.text
                update.message.reply_text('Now, please provide the full article content:')
                return CONTENT
            
            def add_content(update, context):
                """Store content and ask for category"""
                context.user_data['content'] = update.message.text
                
                # Provide category options
                keyboard = [
                    ['Politics', 'Business'],
                    ['Technology', 'Sports'],
                    ['Entertainment', 'Science']
                ]
                reply_markup = telegram.ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
                update.message.reply_text('Select a category for this article:', reply_markup=reply_markup)
                return CATEGORY
            
            def add_category(update, context):
                """Store category and confirm"""
                context.user_data['category'] = update.message.text
                
                # Show summary of article
                title = context.user_data.get('title', '')
                summary = context.user_data.get('summary', '')
                category = context.user_data.get('category', '')
                
                update.message.reply_text(
                    f"Here's a summary of your article:\n\n"
                    f"Title: {title}\n"
                    f"Category: {category}\n"
                    f"Summary: {summary}\n\n"
                    f"Confirm publication? (yes/no)",
                    reply_markup=telegram.ReplyKeyboardRemove()
                )
                return CONFIRM
            
            def confirm_article(update, context):
                """Confirm and save the article"""
                if update.message.text.lower() in ['yes', 'y']:
                    # Here you would normally save to database
                    update.message.reply_text('Article has been published successfully!')
                else:
                    update.message.reply_text('Article publication cancelled.')
                
                # Clear user data
                context.user_data.clear()
                return ConversationHandler.END
            
            def cancel(update, context):
                """Cancel the conversation"""
                update.message.reply_text('Article creation cancelled.', reply_markup=telegram.ReplyKeyboardRemove())
                context.user_data.clear()
                return ConversationHandler.END
            
            # Add conversation handler
            conv_handler = ConversationHandler(
                entry_points=[CommandHandler('addnews', start_add_news)],
                states={
                    TITLE: [MessageHandler(Filters.text & ~Filters.command, add_title)],
                    SUMMARY: [MessageHandler(Filters.text & ~Filters.command, add_summary)],
                    CONTENT: [MessageHandler(Filters.text & ~Filters.command, add_content)],
                    CATEGORY: [MessageHandler(Filters.text & ~Filters.command, add_category)],
                    CONFIRM: [MessageHandler(Filters.text & ~Filters.command, confirm_article)],
                },
                fallbacks=[CommandHandler('cancel', cancel)],
            )
            
            # Add handlers
            dispatcher.add_handler(conv_handler)
            dispatcher.add_handler(CommandHandler("start", start))
            dispatcher.add_handler(CommandHandler("help", help_command))
            
            # Start the Bot
            logger.info(f"[{self.name}] Starting polling...")
            self.running = True
            self.updater.start_polling()
            logger.info(f"[{self.name}] Bot is running!")
            
            # Run until bot is stopped manually
            while bots_running:
                time.sleep(1)
            
            logger.info(f"[{self.name}] Stopping the bot...")
            self.updater.stop()
            self.running = False
            
        except Exception as e:
            import traceback
            logger.error(f"[{self.name}] Error: {e}")
            logger.error(traceback.format_exc())
            self.running = False

def start_bots():
    """Start all bots"""
    global bot_threads
    
    print("Starting Telegram bot service...")
    logger.info("=" * 50)
    logger.info("Starting JBC News Telegram Bot Service")
    logger.info("=" * 50)
    
    # Create bot instances
    registration_bot = RegistrationBot()
    support_bot = SupportBot()
    news_bot = NewsBot()
    staff_bot = StaffBot()
    
    # List of bots
    bots = [registration_bot, support_bot, news_bot, staff_bot]
    
    # Start each bot
    for bot in bots:
        logger.info(f"Starting {bot.name}...")
        if bot.start():
            bot_threads.append(bot)
            logger.info(f"{bot.name} started successfully!")
        else:
            logger.error(f"Failed to start {bot.name}")
    
    logger.info(f"Started {len(bot_threads)} out of {len(bots)} bots")
    
    if not bot_threads:
        logger.error("No bots were started successfully")
        return False
    
    logger.info("All bots are running")
    return True

def stop_bots():
    """Stop all bots"""
    global bots_running, bot_threads
    
    logger.info("Stopping all bots...")
    bots_running = False
    
    # Wait for all threads to finish
    for bot in bot_threads:
        if bot.thread:
            bot.thread.join(timeout=5.0)
            logger.info(f"{bot.name} stopped")
    
    logger.info("All bots stopped")

def main():
    """Main function"""
    try:
        # Start the bots
        if not start_bots():
            return 1
        
        # Keep the script running
        print("Press Ctrl+C to stop the bots")
        while True:
            time.sleep(1)
            
            # Check if all bots are still running
            active_bots = [bot for bot in bot_threads if bot.running]
            if not active_bots:
                logger.error("All bots have stopped running")
                break
            
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        import traceback
        logger.error(f"Error in main function: {e}")
        logger.error(traceback.format_exc())
    finally:
        # Stop the bots
        stop_bots()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())