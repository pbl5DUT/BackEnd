
import requests

def test_auth_check():
    url = 'http://127.0.0.1:8000/api/auth-check/'
    
    try:
        token = input("Enter your JWT token: ")
        headers = {'Authorization': f'Bearer {token}'}
        
        print(f"\nTesting URL: {url}")
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
