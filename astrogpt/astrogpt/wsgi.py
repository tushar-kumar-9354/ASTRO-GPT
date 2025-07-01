"""
WSGI config for astrogpt project.
"""
import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'astrogpt.settings')
application = get_wsgi_application()