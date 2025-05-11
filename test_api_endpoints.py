import requests
import json
import sys

def test_endpoint(token, endpoint, method='get', data=None):
    base_url = 'http://127.0.0.1:8000'
    url = f"{base_url}/api/{endpoint}"
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print(f"\n--- Testing {method.upper()} {url} ---")
    
    try:
        if method.lower() == 'get':
            response = requests.get(url, headers=headers)
        elif method.lower() == 'post':
            response = requests.post(url, headers=headers, json=data)
        else:
            print(f"Method {method} not supported")
            return
            
        print(f"Status Code: {response.status_code}")
        print("Response Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        
        print("\nResponse Body:")
        if response.status_code == 200:
            try:
                print(json.dumps(response.json(), indent=2))
            except:
                print(response.text)
                
            if response.status_code == 200:
                print("\n✅ Endpoint test successful!")
                return True
            else:
                print("\n❌ Endpoint test failed!")
                return False
        else:
            print(response.text)
            print("\n❌ Endpoint test failed!")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_jwt_login(email, password):
    base_url = 'http://127.0.0.1:8000'
    login_url = f"{base_url}/api/login/"
    
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
            else:
                print("\n❌ Login failed! No access token received.")
                return None
        except:
            print(response.text)
            print("\n❌ Login failed! Invalid response format.")
            return None
    
    except Exception as e:
        print(f"Error: {e}")
        print("\n❌ Login failed! Exception occurred.")
        return None

def run_api_tests():
    # Lấy thông tin đăng nhập từ người dùng
    email = input("Enter your email: ")
    password = input("Enter your password: ")
    
    # Lấy token JWT
    token = test_jwt_login(email, password)
    if not token:
        print("Cannot proceed without a valid token.")
        return
    
    # Danh sách các endpoint cần test
    endpoints = [
        ("users/", "get"),
        ("projects/", "get"),
        ("chatrooms/", "get"),
        # Thêm các endpoint khác nếu cần
    ]
    
    # Test từng endpoint
    results = {}
    for endpoint, method in endpoints:
        results[endpoint] = test_endpoint(token, endpoint, method)
    
    # Tổng hợp kết quả
    print("\n----- TEST SUMMARY -----")
    success_count = 0
    for endpoint, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{endpoint}: {status}")
        if success:
            success_count += 1
    
    print(f"\nTotal: {success_count}/{len(results)} endpoints working correctly")

if __name__ == "__main__":
    run_api_tests()
