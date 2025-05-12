import requests
import sys
import json

# Test auth-check endpoint
def test_auth_check(token=None):
    if not token:
        print("Please provide a token as the first argument")
        return
    
    BASE_URL = 'http://127.0.0.1:8000'
    
    # Try different paths to find the auth-check endpoint
    urls_to_try = [
        f"{BASE_URL}/api/auth-check/",
        f"{BASE_URL}/auth-check/"
    ]
    
    for url in urls_to_try:
        print(f"\nTesting URL: {url}")
        
        try:
            headers = {
                'Authorization': f'Bearer {token}'
            }
            
            response = requests.get(url, headers=headers)
            
            print(f"Status Code: {response.status_code}")
            print("Response Headers:")
            for key, value in response.headers.items():
                print(f"  {key}: {value}")
            
            print("\nResponse Body:")
            try:
                print(json.dumps(response.json(), indent=2))
            except:
                print(response.text)
                
            if response.status_code == 200:
                print("\n✅ Auth check successful!")
                return True
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n❌ Auth check failed for all URLs")
    return False

# Test login endpoint to get a token
def test_login(email, password):
    BASE_URL = 'http://127.0.0.1:8000'
    login_url = f"{BASE_URL}/api/login/"
    
    print(f"Testing login at: {login_url}")
    
    try:
        data = {
            "email": email,
            "password": password
        }
        
        response = requests.post(login_url, json=data)
        
        print(f"Status Code: {response.status_code}")
        
        try:
            result = response.json()
            print(json.dumps(result, indent=2))
            
            if "access" in result:
                print("\n✅ Login successful! Access token received.")
                return result["access"]
        except:
            print(response.text)
    
    except Exception as e:
        print(f"Error: {e}")
    
    return None

if __name__ == "__main__":
    # If token provided as argument, use it directly
    if len(sys.argv) > 1:
        token = sys.argv[1]
        test_auth_check(token)
    # If email and password provided, login first
    elif len(sys.argv) > 2:
        email = sys.argv[1]
        password = sys.argv[2]
        token = test_login(email, password)
        if token:
            test_auth_check(token)
    else:
        print("Usage:")
        print("  python test_auth_check.py <token>")
        print("  OR")
        print("  python test_auth_check.py <email> <password>")
