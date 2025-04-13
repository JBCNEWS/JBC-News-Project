#!/usr/bin/env python
"""
JBC News Telegram Bot Runner
---------------------------
This script is responsible for starting and monitoring the standalone Telegram bot.
It will restart the bot if it crashes.
"""

import os
import sys
import time
import logging
import signal
import subprocess
import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"bot_runner_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global variables
bot_process = None
running = True

def signal_handler(signum, frame):
    """Handle termination signals"""
    global running, bot_process
    logger.info(f"Received signal {signum}, shutting down...")
    running = False
    
    if bot_process:
        logger.info("Terminating bot process...")
        try:
            os.killpg(os.getpgid(bot_process.pid), signal.SIGTERM)
            bot_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            logger.warning("Bot process did not terminate gracefully, forcing...")
            os.killpg(os.getpgid(bot_process.pid), signal.SIGKILL)
        except Exception as e:
            logger.error(f"Error terminating bot process: {e}")
    
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def start_bot():
    """Start the bot process"""
    global bot_process
    
    logger.info("Starting Telegram bot...")
    
    try:
        # Start the bot in a new process group
        bot_process = subprocess.Popen(
            ["python", "standalone_bot.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            preexec_fn=os.setsid
        )
        
        logger.info(f"Bot process started with PID {bot_process.pid}")
        
        # Write PID to file
        with open("telegram_bot.pid", "w") as f:
            f.write(str(bot_process.pid))
        
        return True
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        return False

def check_bot_process():
    """Check if the bot process is still running"""
    global bot_process
    
    if bot_process is None:
        return False
    
    # Check if process is still running
    if bot_process.poll() is not None:
        exit_code = bot_process.poll()
        logger.warning(f"Bot process has terminated with exit code {exit_code}")
        
        # Get the output
        output, _ = bot_process.communicate()
        logger.info(f"Bot output: {output}")
        
        bot_process = None
        return False
    
    return True

def main():
    """Main function"""
    logger.info("=" * 50)
    logger.info("Starting JBC News Telegram Bot Runner")
    logger.info("=" * 50)
    
    # Start the bot initially
    if not start_bot():
        logger.error("Failed to start bot initially")
        return 1
    
    # Monitor and restart if needed
    failures = 0
    while running:
        try:
            # Check if bot is running
            if not check_bot_process():
                failures += 1
                logger.warning(f"Bot process not running. Failures: {failures}")
                
                if failures >= 5:
                    logger.error("Too many failures, giving up")
                    return 1
                
                logger.info("Restarting bot...")
                time.sleep(5)  # Wait a bit before restarting
                if not start_bot():
                    logger.error("Failed to restart bot")
                    time.sleep(30)  # Wait longer before trying again
            else:
                # Reset failure counter if bot has been running for a while
                if failures > 0:
                    failures = max(0, failures - 1)
            
            # Check for any new output
            if bot_process:
                # Read output without blocking
                while True:
                    line = bot_process.stdout.readline()
                    if line:
                        print(f"BOT> {line.strip()}")
                    else:
                        break
            
            # Sleep for a while
            time.sleep(5)
            
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
            break
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            time.sleep(10)
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logger.info("Runner stopped by user")
        signal_handler(signal.SIGINT, None)
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}")
        sys.exit(1)