# JBC - JARAR BROADCASTING CORPORATION

JBC is an AI-powered digital news broadcasting system that delivers country-specific news through multiple channels including a responsive website and Telegram bots.

## Features

- Multi-tier user system (Admin, Staff, User)
- Real-time news updates every 30 minutes
- Geo-targeted news for India, Pakistan, USA, Saudi Arabia, and Sri Lanka
- Four integrated Telegram bots:
  - Registration Bot: User registration
  - Support Bot: Customer support tickets
  - News Bot: Personalized news delivery
  - Staff Bot: News management for staff
- Multilingual news translation
- Breaking news alerts
- Search functionality

## Technologies Used

- Backend: Flask (Python)
- Database: PostgreSQL
- ORM: SQLAlchemy
- Task scheduling: APScheduler
- Telegram integration: python-telegram-bot v13.7

## Running the Application

### Web Application

To start the web application:

```
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

Or use the "Start application" workflow in Replit.

### Telegram Bots

To start the Telegram bots separately:

```
python bot_runner.py
```

The Telegram bots require the following environment variables:
- REGISTRATION_BOT_TOKEN
- SUPPORT_BOT_TOKEN
- NEWS_BOT_TOKEN
- STAFF_BOT_TOKEN

## Workflows

- `Start application`: Runs the web application
- `Telegram Bots`: Runs the Telegram bot service (not yet configured in Replit)

## Project Structure

- `app.py`: Flask application setup and configuration
- `routes.py`: Web routes and views
- `models.py`: Database models
- `forms.py`: WTForms for data validation
- `telegram_bots.py`: Telegram bot implementation
- `bot_runner.py`: Simplified runner for Telegram bots
- `news_fetcher.py`: News API integration

## User Roles

### Admin
- Manage staff accounts
- Broadcast messages
- Full access to all features

### Staff
- Create and edit news
- Respond to support tickets
- Translate news articles

### User
- View personalized news
- Set preferences
- Create support tickets