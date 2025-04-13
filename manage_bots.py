#!/usr/bin/env python
"""
JBC Telegram Bot Manager
-------------------------
This script helps to start, stop, and manage the JBC Telegram bots.
"""

import os
import sys
import time
import signal
import subprocess
import argparse
import logging
from datetime import datetime

# Setup logging
log_file = f"bot_manager_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Bot process information
BOT_PROCESS = None
PID_FILE = "telegram_bots.pid"

def save_pid(pid):
    """Save process ID to file"""
    with open(PID_FILE, 'w') as f:
        f.write(str(pid))
    logger.info(f"Saved PID {pid} to {PID_FILE}")

def read_pid():
    """Read process ID from file"""
    if not os.path.exists(PID_FILE):
        return None
    
    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        return pid
    except:
        return None

def is_process_running(pid):
    """Check if a process with given PID is running"""
    try:
        os.kill(pid, 0)  # Signal 0 doesn't kill the process, just checks if it exists
        return True
    except OSError:
        return False

def start_bots():
    """Start the Telegram bots"""
    global BOT_PROCESS
    
    # Check if already running
    pid = read_pid()
    if pid and is_process_running(pid):
        logger.info(f"Bots already running with PID {pid}")
        return
    
    # Start the bot runner
    logger.info("Starting Telegram bots...")
    try:
        # Use nohup to keep process running after terminal closes
        cmd = ["python", "bot_runner.py"]
        BOT_PROCESS = subprocess.Popen(cmd, 
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT,
                                      universal_newlines=True)
        
        # Save PID for later management
        save_pid(BOT_PROCESS.pid)
        
        logger.info(f"Telegram bots started with PID {BOT_PROCESS.pid}")
        
        # Show initial output
        time.sleep(2)  # Give it a moment to start
        logger.info("Initial bot output:")
        
        # Print the first few lines of output
        output_lines = 0
        while output_lines < 10:
            output = BOT_PROCESS.stdout.readline()
            if not output:
                break
            logger.info(f"BOT: {output.strip()}")
            output_lines += 1
            
        logger.info(f"Bot process is running in the background. View logs for details.")
        return True
    
    except Exception as e:
        logger.error(f"Failed to start bots: {str(e)}")
        return False

def stop_bots():
    """Stop the Telegram bots"""
    pid = read_pid()
    if not pid:
        logger.info("No PID file found, bots may not be running")
        return
    
    if is_process_running(pid):
        logger.info(f"Stopping Telegram bots (PID {pid})...")
        try:
            os.kill(pid, signal.SIGTERM)
            
            # Wait briefly for graceful shutdown
            time.sleep(2)
            
            # Force if needed
            if is_process_running(pid):
                logger.info("Process still running, sending SIGKILL...")
                os.kill(pid, signal.SIGKILL)
                
            logger.info("Telegram bots stopped")
        except Exception as e:
            logger.error(f"Error stopping bots: {str(e)}")
    else:
        logger.info(f"Process with PID {pid} not found, cleaning up PID file")
    
    # Clean up PID file
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)

def status_bots():
    """Check status of Telegram bots"""
    pid = read_pid()
    if not pid:
        logger.info("No PID file found, bots are not running")
        return False
    
    if is_process_running(pid):
        logger.info(f"Telegram bots are running with PID {pid}")
        return True
    else:
        logger.info(f"PID file exists but process {pid} is not running")
        # Clean up stale PID file
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        return False

def restart_bots():
    """Restart the Telegram bots"""
    stop_bots()
    time.sleep(2)  # Wait a bit before starting again
    return start_bots()

def main():
    parser = argparse.ArgumentParser(description='JBC Telegram Bot Manager')
    parser.add_argument('action', choices=['start', 'stop', 'restart', 'status'],
                        help='Action to perform')
    
    args = parser.parse_args()
    
    if args.action == 'start':
        start_bots()
    elif args.action == 'stop':
        stop_bots()
    elif args.action == 'restart':
        restart_bots()
    elif args.action == 'status':
        status_bots()

if __name__ == "__main__":
    main()