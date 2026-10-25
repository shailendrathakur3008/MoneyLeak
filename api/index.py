import os
import sys
import re
import urllib.parse

# Ensure root directory is on the path so 'app' and 'config' can be imported by Vercel
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app import create_app

# Vercel serverless function entrypoint (looks for 'app')
flask_app = create_app(os.environ.get('FLASK_ENV', 'production'))


class VercelPathMiddleware:
    """
    WSGI Middleware to ensure URL routing works reliably in Vercel's serverless environment.
    Vercel rewrites routes to '/api/index', which sets WSGI PATH_INFO to '/api/index' by default.
    This middleware restores the original requested path from query string or headers.
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        # Normalize HTTPS scheme and clear SCRIPT_NAME so cookies and url_for use '/' root
        if environ.get('HTTP_X_FORWARDED_PROTO') == 'https':
            environ['wsgi.url_scheme'] = 'https'
        environ['SCRIPT_NAME'] = ''

        query_string = environ.get('QUERY_STRING', '')

        # 1. Primary: Extract path from __vercel_path parameter if rewritten via vercel.json
        if '__vercel_path=' in query_string:
            params = urllib.parse.parse_qs(query_string, keep_blank_values=True)
            if '__vercel_path' in params:
                raw_path = params['__vercel_path'][0] or '/'
                # Normalize slashes: ensure starts with single slash
                environ['PATH_INFO'] = re.sub(r'^/+', '/', '/' + raw_path.lstrip('/'))
                # Clean __vercel_path out of QUERY_STRING
                clean_items = [(k, v) for k, vals in params.items() if k != '__vercel_path' for v in vals]
                environ['QUERY_STRING'] = urllib.parse.urlencode(clean_items)
                return self.wsgi_app(environ, start_response)

        # 2. Secondary: Check Vercel proxy headers for original path
        for header in ('HTTP_X_FORWARDED_URI', 'HTTP_X_MATCHED_PATH', 'HTTP_X_REWRITE_URL'):
            header_val = environ.get(header)
            if header_val and not header_val.startswith('/api/index'):
                clean_path = header_val.split('?')[0]
                if clean_path:
                    environ['PATH_INFO'] = re.sub(r'^/+', '/', '/' + clean_path.lstrip('/'))
                    return self.wsgi_app(environ, start_response)

        # 3. Tertiary: Fallback if path is literally /api/index
        path_info = environ.get('PATH_INFO', '')
        if path_info in ('/api/index', '/api/index/'):
            environ['PATH_INFO'] = '/'
        elif path_info.startswith('/api/index/'):
            environ['PATH_INFO'] = path_info[len('/api/index'):]

        return self.wsgi_app(environ, start_response)


from werkzeug.middleware.proxy_fix import ProxyFix

# Wrap Flask with ProxyFix and VercelPathMiddleware
flask_app.wsgi_app = ProxyFix(flask_app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)
flask_app.wsgi_app = VercelPathMiddleware(flask_app.wsgi_app)


# Explicit fallback route on Flask app for /api/index
@flask_app.route('/api/index', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
@flask_app.route('/api/index/', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def vercel_entrypoint_fallback():
    from app.routes.dashboard import index
    return index()


# Vercel looks for 'app'
app = flask_app
