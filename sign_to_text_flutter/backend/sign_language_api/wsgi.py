"""
WSGI config for sign_language_api project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sign_language_api.settings')

application = get_wsgi_application()
