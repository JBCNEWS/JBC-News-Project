import os
import sys
import logging
import time
from datetime import datetime
import traceback

# Setup logging
log_file = f"telegram_bots_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def log_heading(message):
    """Log a heading with separator lines for better visibility"""
    separator = "=" * 50
    logger.info(separator)
    logger.info(message)
    logger.info(separator)

def main():
    try:
        log_heading("Starting JBC Telegram Bot Runner")
        
        # Log system information
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Current directory: {os.getcwd()}")
        
        # Import and check telegram package
        try:
            import telegram
            logger.info(f"Python-telegram-bot version: {telegram.__version__}")
        except ImportError:
            logger.error("Failed to import telegram package. Please install python-telegram-bot==13.7")
            return 1
        except Exception as e:
            logger.error(f"Error importing telegram: {str(e)}")
            logger.error(traceback.format_exc())
            return 1
        
        # Import Flask app and create application context
        try:
            from app import app
            logger.info("Successfully imported Flask app")
        except ImportError:
            logger.error("Failed to import Flask app")
            logger.error(traceback.format_exc())
            return 1
        
        # Check environment variables for bot tokens
        log_heading("Checking Bot Tokens")
        registration_token = os.environ.get("REGISTRATION_BOT_TOKEN", "")
        support_token = os.environ.get("SUPPORT_BOT_TOKEN", "")
        news_token = os.environ.get("NEWS_BOT_TOKEN", "")  
        staff_token = os.environ.get("STAFF_BOT_TOKEN", "")
        
        logger.info(f"Registration Bot Token present: {bool(registration_token)}")
        logger.info(f"Support Bot Token present: {bool(support_token)}")
        logger.info(f"News Bot Token present: {bool(news_token)}")
        logger.info(f"Staff Bot Token present: {bool(staff_token)}")
        
        # Run bots within Flask application context
        with app.app_context():
            log_heading("Starting Bots (within Flask app context)")
            
            # Save critical information
            with open("bot_status.txt", "w") as f:
                f.write(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"PID: {os.getpid()}\n")
                f.write(f"Python version: {sys.version}\n")
                f.write(f"Working directory: {os.getcwd()}\n")
            
            try:
                # Create a simple bot with basic commands
                from telegram.ext import Updater, CommandHandler
                
                def start(update, context):
                    update.message.reply_text("Welcome to JBC News Bot!")
                    
                def help_command(update, context):
                    update.message.reply_text("This is the JBC News Bot help message.")
                    
                updaters = []
                
                # Start the registration bot
                if registration_token:
                    logger.info("Initializing Registration Bot...")
                    
                    try:
                        updater_reg = Updater(token=registration_token)
                        dispatcher = updater_reg.dispatcher
                        
                        # Add command handlers
                        dispatcher.add_handler(CommandHandler("start", start))
                        dispatcher.add_handler(CommandHandler("help", help_command))
                        
                        # Start the bot
                        updater_reg.start_polling()
                        updaters.append(updater_reg)
                        logger.info("Registration Bot started successfully.")
                    except Exception as e:
                        logger.error(f"Error starting Registration Bot: {str(e)}")
                        logger.error(traceback.format_exc())
                else:
                    logger.warning("Registration Bot not started (no token provided).")
                
                # Log bot status
                with open("bot_status.txt", "a") as f:
                    f.write(f"Registration Bot: {'Started' if registration_token else 'Not started'}\n")
                
                # Keep the main thread alive
                log_heading("Bots Running")
                count = 0
                while True:
                    time.sleep(60)
                    count += 1
                    logger.info(f"Bots still running... (running for {count} minutes)")
                    
                    # Log to a status file every minute for debugging
                    with open("bot_heartbeat.txt", "a") as f:
                        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Bots running for {count} minutes\n")
                    
            except KeyboardInterrupt:
                logger.info("Bots stopped by user.")
            except Exception as e:
                logger.error(f"Error in bot main loop: {str(e)}")
                logger.error(traceback.format_exc())
                
                # Write error to a file for debugging
                with open("bot_error.txt", "a") as f:
                    f.write(f"ERROR at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {str(e)}\n")
                    f.write(traceback.format_exc())
                    f.write("\n\n")
                
                return 1
        
        return 0
        
    except Exception as e:
        # Global exception handler
        logger.critical(f"Unhandled exception in main function: {str(e)}")
        logger.critical(traceback.format_exc())
        
        # Write fatal error to a file for debugging
        with open("bot_fatal_error.txt", "a") as f:
            f.write(f"FATAL ERROR at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {str(e)}\n")
            f.write(traceback.format_exc())
            f.write("\n\n")
        
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        logger.critical(f"Unhandled exception in main: {str(e)}")
        logger.critical(traceback.format_exc())
        sys.exit(1)