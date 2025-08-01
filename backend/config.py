import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'humtumhare-Hawale_hai'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///parking_app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False