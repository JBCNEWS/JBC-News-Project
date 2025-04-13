from app import app
from routes import *
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Import Telegram bots but don't initialize them here
# This prevents conflicts with gunicorn workers
# Use run_bots.py to start the bots separately

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
