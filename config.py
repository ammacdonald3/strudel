import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEVELOPMENT = True
    DEBUG = True
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'this-really-needs-to-be-changed'
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URL = ['DATABASE_URL']

    # Below config for image uploads
    MAX_CONTENT_LENGTH = 2048 * 2048
    UPLOAD_EXTENSIONS = ['.jpg', '.png', '.webp', '.jpeg']
    UPLOAD_PATH = 'uploads'
    BUCKET = os.environ.get('S3_BUCKET')

    # Below config for email server
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['strudelapp@gmail.com']

    # Below config for Google Sign-in
    GOOGLE_LOGIN_URI = os.environ.get('GOOGLE_LOGIN_URI')
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


