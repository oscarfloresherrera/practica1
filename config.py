import os

class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:1379@localhost/practica1"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.urandom(24)
