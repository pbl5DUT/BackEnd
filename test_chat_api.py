import requests
import json
import sys

# URL cơ sở
BASE_URL = "http://127.0.0.1:8000"
API_URL = f"{BASE_URL}/api"

def test_authentication(token=None):
    """Kiểm tra xác thực bằng token"""
    if not token:
        token = input("Nhập token JWT của bạn: ")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print("\n===== KIỂM TRA XÁC THỰC =====")
    
    # Kiểm tra endpoint users
    users_url = f"{API_URL}/users/"
    print(f"\nĐang kiểm tra endpoint users: {users_url}")
    
    try:
        response = requests.get(users_url, headers=headers)
        print(f"Mã trạng thái: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Xác thực thành công qua endpoint users!")
            data = response.json()
            print(f"Số lượng người dùng: {len(data)}")
        else:
            print("❌ Xác thực thất bại qua endpoint users!")
            print(f"Nội dung lỗi: {response.text}")
    except Exception as e:
        print(f"Lỗi: {e}")
    
    # Kiểm tra endpoint chatrooms
    chatrooms_url = f"{API_URL}/chatrooms/"
    print(f"\nĐang kiểm tra endpoint chatrooms: {chatrooms_url}")
    
    try:
        response = requests.get(chatrooms_url, headers=headers)
        print(f"Mã trạng thái: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Xác thực thành công qua endpoint chatrooms!")
            data = response.json()
            print(f"Số lượng phòng chat: {len(data)}")
        else:
            print("❌ Xác thực thất bại qua endpoint chatrooms!")
            print(f"Nội dung lỗi: {response.text}")
    except Exception as e:
        print(f"Lỗi: {e}")
    
    print("\n===== KẾT THÚC KIỂM TRA =====")
    return

if __name__ == "__main__":
    token = sys.argv[1] if len(sys.argv) > 1 else None
    test_authentication(token)
