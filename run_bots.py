import os
import logging
import time
from app import app
from telegram_bots import init_telegram_bots

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting JBC Telegram bots...")
    
    try:
        # Use Flask application context
        with app.app_context():
            logger.info("Checking Telegram bot tokens...")
            from telegram_bots import REGISTRATION_BOT_TOKEN, SUPPORT_BOT_TOKEN, NEWS_BOT_TOKEN, STAFF_BOT_TOKEN
            
            logger.info(f"Registration Bot Token present: {bool(REGISTRATION_BOT_TOKEN)}")
            logger.info(f"Support Bot Token present: {bool(SUPPORT_BOT_TOKEN)}")
            logger.info(f"News Bot Token present: {bool(NEWS_BOT_TOKEN)}")
            logger.info(f"Staff Bot Token present: {bool(STAFF_BOT_TOKEN)}")
            
            # Initialize and start Telegram bots
            logger.info("Initializing Telegram bots...")
            init_telegram_bots()
            
            # Keep the main thread alive
            logger.info("Bots are running. Press Ctrl+C to exit.")
            while True:
                logger.info("Bots still running...")
                time.sleep(60)
                
    except KeyboardInterrupt:
        logger.info("Telegram bots stopped by user.")
    except Exception as e:
        logger.error(f"Error running Telegram bots: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())