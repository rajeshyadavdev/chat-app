import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "chat-app-secret-key")
    
    _db_url = os.environ.get("DATABASE_URL", "sqlite:///" + os.path.join(basedir, "chataap.db"))
    # Render fix - sab ko psycopg v3 pe le jao
    if _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif _db_url.startswith("postgresql://"):
        _db_url = _db_url.replace("postgresql://", "postgresql+psycopg://", 1)
    elif _db_url.startswith("postgresql+psycopg2://"):
        _db_url = _db_url.replace("postgresql+psycopg2://", "postgresql+psycopg://", 1)
    
    SQLALCHEMY_DATABASE_URI = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
