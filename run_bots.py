import os
import logging
import time
import traceback
import sys
from app import app

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("telegram_bots.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def run_registration_bot():
    """Run the registration bot separately for debugging"""
    try:
        from telegram_bots import REGISTRATION_BOT_TOKEN, RegistrationBot
        logger.info(f"Registration Bot Token present: {bool(REGISTRATION_BOT_TOKEN)}")
        
        if REGISTRATION_BOT_TOKEN:
            logger.info("Starting Registration Bot...")
            registration_bot = RegistrationBot()
            registration_bot.start_bot()
            logger.info("Registration Bot started successfully.")
        else:
            logger.warning("Registration Bot Token not provided.")
    except Exception as e:
        logger.error(f"Error running Registration Bot: {str(e)}")
        logger.error(traceback.format_exc())

def run_support_bot():
    """Run the support bot separately for debugging"""
    try:
        from telegram_bots import SUPPORT_BOT_TOKEN, SupportBot
        logger.info(f"Support Bot Token present: {bool(SUPPORT_BOT_TOKEN)}")
        
        if SUPPORT_BOT_TOKEN:
            logger.info("Starting Support Bot...")
            support_bot = SupportBot()
            support_bot.start_bot()
            logger.info("Support Bot started successfully.")
        else:
            logger.warning("Support Bot Token not provided.")
    except Exception as e:
        logger.error(f"Error running Support Bot: {str(e)}")
        logger.error(traceback.format_exc())

def run_news_bot():
    """Run the news bot separately for debugging"""
    try:
        from telegram_bots import NEWS_BOT_TOKEN, NewsBot
        logger.info(f"News Bot Token present: {bool(NEWS_BOT_TOKEN)}")
        
        if NEWS_BOT_TOKEN:
            logger.info("Starting News Bot...")
            news_bot = NewsBot()
            news_bot.start_bot()
            logger.info("News Bot started successfully.")
        else:
            logger.warning("News Bot Token not provided.")
    except Exception as e:
        logger.error(f"Error running News Bot: {str(e)}")
        logger.error(traceback.format_exc())

def run_staff_bot():
    """Run the staff bot separately for debugging"""
    try:
        from telegram_bots import STAFF_BOT_TOKEN, StaffBot
        logger.info(f"Staff Bot Token present: {bool(STAFF_BOT_TOKEN)}")
        
        if STAFF_BOT_TOKEN:
            logger.info("Starting Staff Bot...")
            staff_bot = StaffBot()
            staff_bot.start_bot()
            logger.info("Staff Bot started successfully.")
        else:
            logger.warning("Staff Bot Token not provided.")
    except Exception as e:
        logger.error(f"Error running Staff Bot: {str(e)}")
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    logger.info("Starting JBC Telegram bots...")
    
    try:
        # Use Flask application context
        with app.app_context():
            logger.info("Checking Python version and telegram package...")
            logger.info(f"Python version: {sys.version}")
            
            try:
                import telegram
                logger.info(f"Python-telegram-bot version: {telegram.__version__}")
            except ImportError:
                logger.error("Failed to import telegram package. Please install it with: pip install python-telegram-bot==13.7")
                sys.exit(1)
            except Exception as e:
                logger.error(f"Error importing telegram: {str(e)}")
                logger.error(traceback.format_exc())
            
            # Run each bot separately for better error isolation
            run_registration_bot()
            run_support_bot()
            run_news_bot()
            run_staff_bot()
            
            # Keep the main thread alive
            logger.info("Bots are running. Press Ctrl+C to exit.")
            while True:
                time.sleep(60)
                
    except KeyboardInterrupt:
        logger.info("Telegram bots stopped by user.")
    except Exception as e:
        logger.error(f"Error running Telegram bots: {str(e)}")
        logger.error(traceback.format_exc())