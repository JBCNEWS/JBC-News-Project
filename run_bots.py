import os
import logging
import time
from app import app
from telegram_bots import init_telegram_bots

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting JBC Telegram bots...")
    
    try:
        # Use Flask application context
        with app.app_context():
            # Initialize and start Telegram bots
            init_telegram_bots()
            
            # Keep the main thread alive
            logger.info("Bots are running. Press Ctrl+C to exit.")
            while True:
                time.sleep(60)
                
    except KeyboardInterrupt:
        logger.info("Telegram bots stopped by user.")
    except Exception as e:
        logger.error(f"Error running Telegram bots: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())