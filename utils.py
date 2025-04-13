import os
import json
import requests
import logging
import uuid
import random
import string
from datetime import datetime
from flask import flash, current_app
from googletrans import Translator

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize translator
translator = Translator()

def generate_unique_id(length=8):
    """Generate a unique ID of specified length"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def translate_text(text, target_language='en'):
    """Translate text to target language using Google Translate API or GPT-4"""
    if not text:
        return ""
        
    try:
        # Using googletrans as a fallback free option
        translation = translator.translate(text, dest=target_language)
        return translation.text
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        return text

def get_local_time_for_country(country_code):
    """Get current local time for a country"""
    from datetime import datetime
    import pytz
    
    country_timezones = {
        'IN': 'Asia/Kolkata',
        'PK': 'Asia/Karachi',
        'US': 'America/New_York',
        'SA': 'Asia/Riyadh',
        'LK': 'Asia/Colombo'
    }
    
    timezone = country_timezones.get(country_code, 'UTC')
    tz = pytz.timezone(timezone)
    return datetime.now(tz)

def format_datetime(dt, format_str='%d %b %Y, %H:%M'):
    """Format datetime object to string"""
    if not dt:
        return ""
    return dt.strftime(format_str)

def get_country_flag_emoji(country_code):
    """Convert country code to flag emoji"""
    if not country_code or len(country_code) != 2:
        return "🌐"
    
    # Regional indicator symbols are Unicode characters that correspond to letters A-Z
    # and are used to create flag emojis
    return "".join([chr(ord(c) + 127397) for c in country_code.upper()])

def truncate_text(text, max_length=100):
    """Truncate text to max_length and add ellipsis if needed"""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def flash_form_errors(form):
    """Flash form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{getattr(form, field).label.text}: {error}", "error")

def is_valid_url(url):
    """Check if URL is valid"""
    import re
    url_pattern = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None

def get_random_news_image():
    """Get a random news image URL from predefined list"""
    news_images = [
        "https://images.unsplash.com/photo-1495020689067-958852a7765e",
        "https://images.unsplash.com/photo-1504711434969-e33886168f5c",
        "https://images.unsplash.com/photo-1560957123-e8e019c66980",
        "https://images.unsplash.com/photo-1581092787765-e3feb951d987",
        "https://images.unsplash.com/photo-1585282263861-f55e341878f8",
        "https://images.unsplash.com/photo-1593789198777-f29bc259780e"
    ]
    return random.choice(news_images)

def get_random_profile_image():
    """Get a random profile image URL from predefined list"""
    profile_images = [
        "https://images.unsplash.com/photo-1438761681033-6461ffad8d80",
        "https://images.unsplash.com/photo-1568602471122-7832951cc4c5",
        "https://images.unsplash.com/photo-1499557354967-2b2d8910bcca",
        "https://images.unsplash.com/photo-1503235930437-8c6293ba41f5"
    ]
    return random.choice(profile_images)
