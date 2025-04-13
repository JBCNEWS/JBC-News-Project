import os
import logging
import sys

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_telegram.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def test_telegram_import():
    """Test importing telegram package"""
    try:
        import telegram
        logger.info(f"Successfully imported telegram package, version: {telegram.__version__}")
        return True
    except ImportError as e:
        logger.error(f"Failed to import telegram package: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error while importing telegram: {str(e)}")
        return False

def test_bot_creation():
    """Test creating a Telegram bot instance"""
    try:
        import telegram
        
        # Try with a placeholder token (won't connect, just testing creation)
        token = os.environ.get("REGISTRATION_BOT_TOKEN", "")
        if not token:
            logger.warning("No REGISTRATION_BOT_TOKEN found, using placeholder")
            token = "placeholder_token"
            
        bot = telegram.Bot(token=token)
        logger.info(f"Successfully created bot instance: {bot}")
        return True
    except Exception as e:
        logger.error(f"Failed to create bot instance: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    logger.info("Running Telegram bot tests...")
    
    # Test imports
    if not test_telegram_import():
        logger.error("Failed to import telegram package. Exiting.")
        sys.exit(1)
    
    # Test bot creation
    if not test_bot_creation():
        logger.error("Failed to create bot instance. Exiting.")
        sys.exit(1)
    
    logger.info("Telegram bot tests completed successfully.")