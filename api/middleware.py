from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model

@database_sync_to_async
def get_user(token_key):
    try:
        # This will verify the token and raise an exception if invalid
        access_token = AccessToken(token_key)
        
        # Get the user ID from the token payload
        user_id = access_token.get('user_id')
        
        if not user_id:
            return AnonymousUser()
        
        # Thử custom user model trước vì chúng ta biết user_id có dạng chuỗi
        from api.models.user import User as CustomUser
        try:
            user = CustomUser.objects.get(user_id=user_id)
            print(f"✅ WebSocket authenticated as user: {user_id}")
            return user
        except CustomUser.DoesNotExist:
            # Thử tìm trong model mặc định (thường không cần thiết)
            try:
                User = get_user_model()
                # Chỉ thử tìm bằng id nếu user_id là số
                if isinstance(user_id, (int, float)) or (isinstance(user_id, str) and user_id.isdigit()):
                    return User.objects.get(id=user_id)
                return AnonymousUser()
            except Exception:
                return AnonymousUser()
                
    except Exception as e:
        print(f"Token authentication error: {str(e)}")
        return AnonymousUser()

class TokenAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # Extract token from query string
        query_string = scope.get('query_string', b'').decode('utf-8')
        query_params = dict(param.split('=') for param in query_string.split('&') if '=' in param)
        token = query_params.get('token')
        
        if token:
            # Get the user from the token
            user = await get_user(token)
            # Add the user to the scope
            scope['user'] = user
        else:
            # No token, set anonymous user
            scope['user'] = AnonymousUser()
            
        return await super().__call__(scope, receive, send)

# Đảm bảo TokenAuthMiddlewareStack được định nghĩa đúng cách
def TokenAuthMiddlewareStack(inner):
    return TokenAuthMiddleware(inner)