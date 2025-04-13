import os
import logging
from telegram_bots import init_telegram_bots

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting JBC Telegram bots...")
    
    try:
        # Initialize and start Telegram bots
        init_telegram_bots()
        
        # Keep the main thread alive
        logger.info("Bots are running. Press Ctrl+C to exit.")
        import time
        while True:
            time.sleep(60)
            
    except KeyboardInterrupt:
        logger.info("Telegram bots stopped by user.")
    except Exception as e:
        logger.error(f"Error running Telegram bots: {str(e)}")