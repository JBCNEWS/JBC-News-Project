
import os
import logging
import time
import traceback
import sys
from app import app, db

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

def check_environment():
    """Check if all required environment variables are set"""
    required_tokens = [
        "REGISTRATION_BOT_TOKEN",
        "SUPPORT_BOT_TOKEN", 
        "NEWS_BOT_TOKEN",
        "STAFF_BOT_TOKEN"
    ]
    
    missing = []
    for token in required_tokens:
        if not os.environ.get(token):
            missing.append(token)
    
    if missing:
        logger.error(f"Missing environment variables: {', '.join(missing)}")
        return False
    return True

def init_database():
    """Initialize database tables"""
    try:
        with app.app_context():
            db.create_all()
            logger.info("Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        return False

def run_bot(bot_class, bot_name, token_name):
    """Run a single bot with error handling"""
    try:
        from telegram_bots import RegistrationBot, SupportBot, NewsBot, StaffBot
        token = os.environ.get(token_name)
        
        if not token:
            logger.warning(f"{bot_name} Token not provided.")
            return False
            
        logger.info(f"Starting {bot_name}...")
        bot = bot_class()
        bot.start_bot()
        logger.info(f"{bot_name} started successfully.")
        return True
        
    except Exception as e:
        logger.error(f"Error running {bot_name}: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def main():
    """Main function to run all bots"""
    logger.info("Starting JBC Telegram bots...")
    
    # Check environment variables
    if not check_environment():
        logger.error("Environment check failed")
        return 1
        
    try:
        # Import and check telegram package
        import telegram
        logger.info(f"Python-telegram-bot version: {telegram.__version__}")
        
        # Initialize database
        if not init_database():
            return 1
            
        # Use Flask application context
        with app.app_context():
            from telegram_bots import RegistrationBot, SupportBot, NewsBot, StaffBot
            
            bots = [
                (RegistrationBot, "Registration Bot", "REGISTRATION_BOT_TOKEN"),
                (SupportBot, "Support Bot", "SUPPORT_BOT_TOKEN"),
                (NewsBot, "News Bot", "NEWS_BOT_TOKEN"),
                (StaffBot, "Staff Bot", "STAFF_BOT_TOKEN")
            ]
            
            running_bots = []
            for bot_class, name, token in bots:
                if run_bot(bot_class, name, token):
                    running_bots.append(name)
            
            if not running_bots:
                logger.error("No bots were started successfully")
                return 1
                
            logger.info(f"Successfully started bots: {', '.join(running_bots)}")
            
            # Keep the main thread alive
            while True:
                time.sleep(60)
                logger.info("Bots still running...")
                
    except KeyboardInterrupt:
        logger.info("Telegram bots stopped by user.")
    except Exception as e:
        logger.error(f"Error running Telegram bots: {str(e)}")
        logger.error(traceback.format_exc())
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
