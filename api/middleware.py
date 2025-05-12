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
        
        # Get the user from the database
        User = get_user_model()
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            # Try custom user model if exists
            from api.models.user import User as CustomUser
            try:
                return CustomUser.objects.get(user_id=user_id)
            except CustomUser.DoesNotExist:
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
            scope['user'] = await get_user(token)
        else:
            scope['user'] = AnonymousUser()
            
        return await super().__call__(scope, receive, send)

def TokenAuthMiddlewareStack(inner):
    return TokenAuthMiddleware(inner)
