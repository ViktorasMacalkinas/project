import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RECAPTCHA_SITE_KEY = '6LersQkqAAAAAF5PIjZMob-36wudlrSzyMoci4rt'
    RECAPTCHA_PRIVATE_KEY = '6LersQkqAAAAAI8okasFmNjgzCQSrTSveYxFtNb_'


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(Config):
    DEBUG = False
