import os
import sys
import django

# Set up Django environment
sys.path.append('d:\\pbl5\\FrontEnd\\BackEnd')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# Import necessary modules
from django.urls import get_resolver, URLPattern, URLResolver


# Check current URL patterns
resolver = get_resolver()

print("Checking API URL patterns...")
api_urls = [url for url in resolver.url_patterns if getattr(url, 'app_name', '') == 'api' or url.pattern.regex.pattern == 'api/']

if api_urls:
    for url in api_urls:
        if hasattr(url, 'urlconf_name') and url.urlconf_name:
            for pattern in url.urlconf_name:
                if hasattr(pattern, 'pattern') and pattern.pattern.regex.pattern == 'auth-check/':
                    print(f"Found auth-check endpoint: {pattern}")
                    print(f"Currently using view: {pattern.callback.__name__}")
                    print(f"Path to auth-check: api/{pattern.pattern}")

# Let's create a simple view test file to verify the auth-check endpoint
test_file = """
import requests

def test_auth_check():
    url = 'http://127.0.0.1:8000/api/auth-check/'
    
    try:
        token = input("Enter your JWT token: ")
        headers = {'Authorization': f'Bearer {token}'}
        
        print(f"\\nTesting URL: {url}")
        response = requests.get(url, headers=headers)
        
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Auth check successful!")
        else:
            print("❌ Auth check failed!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_auth_check()
"""

# Write the test file
with open('test_simple_auth.py', 'w', encoding='utf-8') as f:
    f.write(test_file)

print("\nDiagnostics complete.")
print("Created test_simple_auth.py to verify the auth-check endpoint")
print("Run it with: python test_simple_auth.py")
