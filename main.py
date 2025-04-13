from app import app, db
from routes import *
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables if they don't exist
with app.app_context():
    db.create_all()
    logger.info("Database initialized")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
