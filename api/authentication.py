# Custom JWT authentication backend for User model with user_id field
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed
from api.models.user import User
import logging

logger = logging.getLogger(__name__)

class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        """
        Attempt to find and return a user using the given validated token.
        """
        try:
            user_id = validated_token['user_id']
            logger.debug(f"Authenticating user with user_id: {user_id}")
        except KeyError:
            logger.error("No user_id found in token")
            raise AuthenticationFailed('No user_id found in token')

        try:
            # Try to get our custom User directly first
            user = User.objects.get(user_id=user_id)
            logger.debug(f"Found custom user: {user}")
            return user
        except User.DoesNotExist:
            logger.error(f"Custom user not found with ID: {user_id}")
            raise AuthenticationFailed('User not found')
