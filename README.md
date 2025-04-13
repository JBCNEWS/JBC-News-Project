# JBC News Broadcasting System

## Overview
JBC (JARAR BROADCASTING CORPORATION) is an AI-powered digital news broadcasting system that delivers personalized, multilingual, real-time news globally. The system features:

- Responsive website with admin, staff, and user portals
- Telegram bots for interactive news delivery and management
- Automated news fetching from reliable sources every 30 minutes
- Multilingual support through translation services
- Country-specific news customization for India, Pakistan, USA, Saudi Arabia, and Sri Lanka

## Features

### Web Interface
- Separate login portals for Admin, Staff, and Users
- Admin dashboard for managing staff, news, and user accounts
- Staff portal for content creation and management
- User-facing news portal with personalized content

### Telegram Bots
- Registration Bot: Handle user registrations
- Support Bot: Manage user support tickets
- News Bot: Deliver personalized news content
- Staff Bot: Enable staff to post and manage content via Telegram

### News Engine
- Automated fetching from CNN, Times of India, Dawn, Arab News
- Web scraping and API integration
- Category-based classification
- Breaking news notifications

## Technology Stack
- Backend: Flask (Python)
- Database: PostgreSQL
- Bot Framework: python-telegram-bot
- Scraping Utilities: Trafilatura
- Scheduling: APScheduler
- Authentication: Flask-Login

## Installation and Setup

### Prerequisites
- Python 3.11+
- PostgreSQL
- Telegram Bot API Tokens

### Environment Variables
- `DATABASE_URL`: PostgreSQL database connection string
- `SESSION_SECRET`: Secret key for session management
- `REGISTRATION_BOT_TOKEN`: Telegram token for Registration Bot
- `SUPPORT_BOT_TOKEN`: Telegram token for Support Bot
- `NEWS_BOT_TOKEN`: Telegram token for News Bot
- `STAFF_BOT_TOKEN`: Telegram token for Staff Bot

### Running the Application
1. Install dependencies: `pip install -r requirements.txt`
2. Initialize database: `flask db upgrade`
3. Run web server: `gunicorn --bind 0.0.0.0:5000 main:app`
4. Run Telegram bots: `python run_bots.py`

## Default Admin Credentials
- Email: ayyan@toxai.com.pk
- Password: 9045CcF2

## License
Proprietary software. All rights reserved.