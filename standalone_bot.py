#!/usr/bin/env python
"""
JBC News Telegram Bots
----------------------
This is an enhanced standalone Telegram bot runner that handles all 4 bots:
1. Registration Bot
2. Support Bot
3. News Bot
4. Staff Bot
"""

import os
import sys
import logging
import time
import traceback
import signal
from datetime import datetime
import threading

# Setup logging
log_filename = f"jbc_bots_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Global variables
running = True
updaters = []

# Signal handler for graceful shutdown
def signal_handler(signum, frame):
    global running
    logger.info(f"Received signal {signum}, shutting down bots...")
    running = False
    
    # Stop all updaters
    for updater in updaters:
        logger.info(f"Stopping bot {updater.bot.username}...")
        updater.stop()
    
    logger.info("All bots stopped successfully")
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Heartbeat thread function
def heartbeat_thread():
    count = 0
    while running:
        time.sleep(60)
        count += 1
        logger.info(f"Heartbeat: Bots running for {count} minutes")
        
        # Write heartbeat to file
        with open("bot_heartbeat.txt", "w") as f:
            f.write(f"Last heartbeat: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Running for: {count} minutes\n")
            f.write(f"Active bots: {len(updaters)}\n")
            for i, updater in enumerate(updaters):
                f.write(f"Bot {i+1}: {updater.bot.username}\n")

# Start the registration bot
def start_registration_bot():
    token = os.environ.get("REGISTRATION_BOT_TOKEN", "")
    if not token:
        logger.error("No REGISTRATION_BOT_TOKEN found in environment")
        return None
    
    try:
        # Import telegram package
        import telegram
        from telegram.ext import Updater, CommandHandler
        
        # Define command handlers
        def start(update, context):
            logger.info(f"[Registration Bot] Received /start command from user {update.effective_user.id}")
            update.message.reply_text(
                f"Hello {update.effective_user.first_name}! Welcome to JBC News Registration Bot."
            )
        
        def help_command(update, context):
            logger.info(f"[Registration Bot] Received /help command from user {update.effective_user.id}")
            update.message.reply_text("This is the JBC News Registration Bot. Use /register to create a new account.")
        
        def register_command(update, context):
            logger.info(f"[Registration Bot] Received /register command from user {update.effective_user.id}")
            update.message.reply_text("To register, please provide your email address.")
        
        # Create the bot
        logger.info("Creating Registration Bot updater...")
        updater = Updater(token=token)
        dispatcher = updater.dispatcher
        
        # Add handlers
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("help", help_command))
        dispatcher.add_handler(CommandHandler("register", register_command))
        
        # Start the bot
        logger.info("Starting Registration Bot polling...")
        updater.start_polling()
        
        logger.info(f"Registration Bot (@{updater.bot.username}) started successfully")
        return updater
        
    except Exception as e:
        logger.error(f"Error starting Registration Bot: {str(e)}")
        logger.error(traceback.format_exc())
        return None

# Start the support bot
def start_support_bot():
    token = os.environ.get("SUPPORT_BOT_TOKEN", "")
    if not token:
        logger.error("No SUPPORT_BOT_TOKEN found in environment")
        return None
    
    try:
        # Import telegram package
        import telegram
        from telegram.ext import Updater, CommandHandler
        
        # Define command handlers
        def start(update, context):
            logger.info(f"[Support Bot] Received /start command from user {update.effective_user.id}")
            update.message.reply_text(
                f"Hello {update.effective_user.first_name}! Welcome to JBC News Support Bot."
            )
        
        def help_command(update, context):
            logger.info(f"[Support Bot] Received /help command from user {update.effective_user.id}")
            update.message.reply_text("This is the JBC News Support Bot. Use /ticket to create a new support ticket.")
        
        def ticket_command(update, context):
            logger.info(f"[Support Bot] Received /ticket command from user {update.effective_user.id}")
            update.message.reply_text("To create a support ticket, please provide a brief description of your issue.")
        
        # Create the bot
        logger.info("Creating Support Bot updater...")
        updater = Updater(token=token)
        dispatcher = updater.dispatcher
        
        # Add handlers
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("help", help_command))
        dispatcher.add_handler(CommandHandler("ticket", ticket_command))
        
        # Start the bot
        logger.info("Starting Support Bot polling...")
        updater.start_polling()
        
        logger.info(f"Support Bot (@{updater.bot.username}) started successfully")
        return updater
        
    except Exception as e:
        logger.error(f"Error starting Support Bot: {str(e)}")
        logger.error(traceback.format_exc())
        return None

# Start the news bot
def start_news_bot():
    token = os.environ.get("NEWS_BOT_TOKEN", "")
    if not token:
        logger.error("No NEWS_BOT_TOKEN found in environment")
        return None
    
    try:
        # Import telegram package
        import telegram
        from telegram.ext import Updater, CommandHandler
        
        # Define command handlers
        def start(update, context):
            logger.info(f"[News Bot] Received /start command from user {update.effective_user.id}")
            update.message.reply_text(
                f"Hello {update.effective_user.first_name}! Welcome to JBC News Bot."
            )
        
        def help_command(update, context):
            logger.info(f"[News Bot] Received /help command from user {update.effective_user.id}")
            update.message.reply_text("This is the JBC News Bot. Use /news to get the latest news.")
        
        def news_command(update, context):
            logger.info(f"[News Bot] Received /news command from user {update.effective_user.id}")
            update.message.reply_text("Here are the latest headlines from JBC News:")
            update.message.reply_text("1. Global markets rebound after recent slump")
            update.message.reply_text("2. New climate agreement reached at international summit")
            update.message.reply_text("3. Tech company announces breakthrough in AI research")
        
        # Create the bot
        logger.info("Creating News Bot updater...")
        updater = Updater(token=token)
        dispatcher = updater.dispatcher
        
        # Add handlers
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("help", help_command))
        dispatcher.add_handler(CommandHandler("news", news_command))
        
        # Start the bot
        logger.info("Starting News Bot polling...")
        updater.start_polling()
        
        logger.info(f"News Bot (@{updater.bot.username}) started successfully")
        return updater
        
    except Exception as e:
        logger.error(f"Error starting News Bot: {str(e)}")
        logger.error(traceback.format_exc())
        return None

# Start the staff bot
def start_staff_bot():
    token = os.environ.get("STAFF_BOT_TOKEN", "")
    if not token:
        logger.error("No STAFF_BOT_TOKEN found in environment")
        return None
    
    try:
        # Import telegram package
        import telegram
        from telegram.ext import Updater, CommandHandler
        
        # Define command handlers
        def start(update, context):
            logger.info(f"[Staff Bot] Received /start command from user {update.effective_user.id}")
            update.message.reply_text(
                f"Hello {update.effective_user.first_name}! Welcome to JBC News Staff Bot."
            )
        
        def help_command(update, context):
            logger.info(f"[Staff Bot] Received /help command from user {update.effective_user.id}")
            update.message.reply_text("This is the JBC News Staff Bot. Use /addnews to add a new article.")
        
        def addnews_command(update, context):
            logger.info(f"[Staff Bot] Received /addnews command from user {update.effective_user.id}")
            update.message.reply_text("To add news, please provide the title of the article.")
        
        # Create the bot
        logger.info("Creating Staff Bot updater...")
        updater = Updater(token=token)
        dispatcher = updater.dispatcher
        
        # Add handlers
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("help", help_command))
        dispatcher.add_handler(CommandHandler("addnews", addnews_command))
        
        # Start the bot
        logger.info("Starting Staff Bot polling...")
        updater.start_polling()
        
        logger.info(f"Staff Bot (@{updater.bot.username}) started successfully")
        return updater
        
    except Exception as e:
        logger.error(f"Error starting Staff Bot: {str(e)}")
        logger.error(traceback.format_exc())
        return None

def main():
    logger.info("=" * 50)
    logger.info("Starting JBC News Telegram Bots")
    logger.info("=" * 50)
    
    # Log system information
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Current directory: {os.getcwd()}")
    
    try:
        # Check telegram package
        import telegram
        logger.info(f"Using python-telegram-bot version: {telegram.__version__}")
        
        # Save initial information
        with open("bot_status.txt", "w") as f:
            f.write(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"PID: {os.getpid()}\n")
            f.write(f"Python version: {sys.version}\n")
            f.write(f"Working directory: {os.getcwd()}\n")
            f.write(f"Log file: {log_filename}\n")
        
        # Start heartbeat thread
        logger.info("Starting heartbeat thread...")
        heartbeat = threading.Thread(target=heartbeat_thread)
        heartbeat.daemon = True
        heartbeat.start()
        
        # Start all bots
        global updaters
        
        # Registration Bot
        reg_bot = start_registration_bot()
        if reg_bot:
            updaters.append(reg_bot)
        
        # Support Bot
        sup_bot = start_support_bot()
        if sup_bot:
            updaters.append(sup_bot)
        
        # News Bot
        news_bot = start_news_bot()
        if news_bot:
            updaters.append(news_bot)
        
        # Staff Bot
        staff_bot = start_staff_bot()
        if staff_bot:
            updaters.append(staff_bot)
        
        # Log active bots
        logger.info(f"Successfully started {len(updaters)} out of 4 bots")
        
        # Keep the main thread alive
        if updaters:
            logger.info("=" * 50)
            logger.info("All bots are running")
            logger.info("=" * 50)
            
            # Use .idle() on just one updater, which will handle signals for us
            if updaters:
                updaters[0].idle()
            else:
                # If no updaters, just keep the script running
                while running:
                    time.sleep(1)
                    
            return 0
        else:
            logger.error("No bots were started successfully")
            return 1
            
    except Exception as e:
        logger.critical(f"Unhandled exception in main function: {str(e)}")
        logger.critical(traceback.format_exc())
        
        # Write fatal error to a file
        with open("bot_fatal_error.txt", "w") as f:
            f.write(f"FATAL ERROR at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {str(e)}\n")
            f.write(traceback.format_exc())
        
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logger.info("Bots stopped by user")
    except Exception as e:
        logger.critical(f"Unhandled exception: {str(e)}")
        logger.critical(traceback.format_exc())
        sys.exit(1)