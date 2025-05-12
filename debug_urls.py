import sys
import os

# Thêm dự án vào PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

import django
django.setup()

from django.urls import get_resolver
from django.urls.resolvers import URLPattern, URLResolver

def list_urls(urlpatterns, prefix=''):
    for pattern in urlpatterns:
        if isinstance(pattern, URLPattern):
            print(f"{prefix}{pattern.pattern}")
        elif isinstance(pattern, URLResolver):
            print(f"{prefix}{pattern.pattern}")
            list_urls(pattern.url_patterns, prefix + str(pattern.pattern))
        else:
            print(f"Unknown pattern type: {pattern}")

print("\nAll URL patterns in the project:")
resolver = get_resolver()
list_urls(resolver.url_patterns)