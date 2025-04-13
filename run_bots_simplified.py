import os
import sys
import logging
import time
import traceback
from app import app

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bots_simplified.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def create_and_run_registration_bot():
    """Create and run a simplified registration bot"""
    try:
        import telegram
        from telegram.ext import Updater, CommandHandler
        
        token = os.environ.get("REGISTRATION_BOT_TOKEN", "")
        if not token:
            logger.error("REGISTRATION_BOT_TOKEN is not set")
            return False
            
        logger.info(f"Creating Registration bot with token: {bool(token)}")
        
        # Define command handlers
        def start_command(update, context):
            update.message.reply_text("Welcome to the JBC Registration Bot!")
        
        def help_command(update, context):
            update.message.reply_text("This is the help message.")
        
        # Create the bot
        updater = Updater(token=token)
        dispatcher = updater.dispatcher
        
        # Add handlers
        dispatcher.add_handler(CommandHandler("start", start_command))
        dispatcher.add_handler(CommandHandler("help", help_command))
        
        # Start the bot
        updater.start_polling()
        logger.info("Registration Bot started successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error creating Registration bot: {str(e)}")
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    logger.info("Starting simplified JBC Telegram bot...")
    
    try:
        # Use Flask application context
        with app.app_context():
            logger.info("Checking Python version and telegram package...")
            logger.info(f"Python version: {sys.version}")
            
            try:
                import telegram
                logger.info(f"Python-telegram-bot version: {telegram.__version__}")
            except ImportError:
                logger.error("Failed to import telegram package.")
                sys.exit(1)
            
            # Run the simplified registration bot
            success = create_and_run_registration_bot()
            if not success:
                logger.error("Failed to start the Registration bot.")
                sys.exit(1)
            
            # Keep the main thread alive
            logger.info("Bot is running. Press Ctrl+C to exit.")
            while True:
                time.sleep(10)
                logger.info("Bot still running...")
                
    except KeyboardInterrupt:
        logger.info("Telegram bot stopped by user.")
    except Exception as e:
        logger.error(f"Error running Telegram bot: {str(e)}")
        logger.error(traceback.format_exc())