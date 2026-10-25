import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

is_vercel = os.environ.get('VERCEL') == '1' or 'VERCEL' in os.environ
default_sqlite = 'sqlite:////tmp/moneyleak.db' if is_vercel else 'sqlite:///moneyleak.db'

_raw_db_url = os.environ.get('DATABASE_URL') or default_sqlite
if _raw_db_url and _raw_db_url.startswith('postgres://'):
    _raw_db_url = _raw_db_url.replace('postgres://', 'postgresql://', 1)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'moneyleak-production-sec-key-7f9a12c8b4e05139')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = _raw_db_url
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    } if _raw_db_url and _raw_db_url.startswith('postgresql') else {}
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_PATH = '/'
    APPLICATION_ROOT = '/'
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() in ('true', '1')
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max for imports

    # Supabase Configuration
    SUPABASE_URL = os.environ.get('SUPABASE_URL') or 'https://roxyqqtfgzrbwqthvrnt.supabase.co'
    SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY') or 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJveHlxcXRmZ3pyYndxdGh2cm50Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTIxNDcxNzQsImV4cCI6MjEwNzcyMzE3NH0.osUI_k9rWSEK2EwzDIbnxMEhrYEmBLe1zLhC1baUAXI'
    SUPABASE_SERVICE_ROLE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJveHlxcXRmZ3pyYndxdGh2cm50Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc5MjE0NzE3NCwiZXhwIjoyMTA3NzIzMTc0fQ.u04NN6RrpDtK52FeePRvEYLcNorLomNhzric1ERvhhY'

    # Scheduler & Web Push VAPID Configuration
    SCHEDULER_SECRET_KEY = os.environ.get('SCHEDULER_SECRET_KEY', 'moneyleak-scheduler-secret-key-9a8b7c6d5e')
    VAPID_PUBLIC_KEY = os.environ.get('VAPID_PUBLIC_KEY', 'BB9Fv5DX6dMJ-lt-7UvR3TKYgDUVpD2uUVN5pg-VuSNrWdx0-fqk2I4DFjATVayrYTvAuQ30cgDOhpWXqxvE2Fs')
    VAPID_PRIVATE_KEY = os.environ.get('VAPID_PRIVATE_KEY', '-----BEGIN PRIVATE KEY-----\nMIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQg+AOR5K9p+potfIHv\nnHuR7DDP8/zpJmY50gr5LOigBIShRANCAAQfRb+Q1+nTCfpbfu1L0d0ymIA1FaQ9\nrlFTeaYPlbkja1ncdPn6pNiOAxYwE1Wsq2E7wLkN9HIAzoaVl6sbxNhb\n-----END PRIVATE KEY-----')
    VAPID_CLAIM_EMAIL = os.environ.get('VAPID_CLAIM_EMAIL', 'admin@moneyleak.app')

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_PATH = '/'

config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
