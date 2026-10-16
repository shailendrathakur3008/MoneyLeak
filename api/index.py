import os
import sys

# Ensure root directory is on the path so 'app' and 'config' can be imported by Vercel
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app import create_app

# Vercel serverless function entrypoint (looks for 'app')
app = create_app(os.environ.get('FLASK_ENV', 'production'))
