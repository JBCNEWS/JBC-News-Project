
from setuptools import setup, find_packages

setup(
    name="jbc-news",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "email-validator>=2.2.0",
        "flask-login>=0.6.3",
        "flask>=3.1.0",
        "flask-sqlalchemy>=3.1.1",
        "gunicorn>=23.0.0",
        "psycopg2-binary>=2.9.10",
        "routes>=2.5.1",
        "trafilatura>=2.0.0",
        "flask-wtf>=1.2.2",
        "telegram>=0.0.1",
        "wtforms>=3.2.1",
        "flask-migrate>=4.1.0",
        "googletrans>=4.0.2",
        "requests>=2.32.3",
        "sqlalchemy>=2.0.40",
        "flask-apscheduler>=1.13.1",
        "google-api-python-client>=2.166.0",
        "werkzeug>=3.1.3",
        "python-telegram-bot==13.7",
        "pytz>=2025.2"
    ]
)
