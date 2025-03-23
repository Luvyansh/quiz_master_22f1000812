import os

class Config:
    SECRET_KEY = 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///quiz_master.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False