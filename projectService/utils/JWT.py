# utils/JWT.py

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
import jwt
import requests
from dotenv import load_dotenv
import os

load_dotenv()

# utils/JWT.py

class CustomUser:
    def __init__(self, user_id, username=None, is_active=True, is_authenticated=True, is_staff=False, is_superuser=False):
        self.user_id = user_id
        self.username = username
        self.is_active = is_active
        self.is_authenticated = is_authenticated
        self.is_staff = is_staff
        self.is_superuser = is_superuser

    def __getattr__(self, item):
        if item == 'is_authenticated':
            return self.is_authenticated
        elif item == 'is_active':
            return self.is_active
        elif item == 'username':
            return self.username
        elif item == 'user_id':
            return self.user_id
        raise AttributeError(f"'CustomUser' object has no attribute '{item}'")

    def get_id(self):
        return self.user_id

    # Add a placeholder `get` method to prevent the 'get' error
    def get(self, key, default=None):
        return getattr(self, key, default)


class JWTAuthentication(BaseAuthentication):
    
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', None)
        if not auth_header:
            return None
        
        token = auth_header.split(' ')[1] if auth_header and ' ' in auth_header else None
        if not token:
            return None

        try:
            payload = self.decode_token(token)
            if not payload:
                raise AuthenticationFailed('Unauthorized')
            
            user_id = payload.get('user_id')
            if not user_id:
                raise AuthenticationFailed('Unauthorized')

            user_details = self.get_user_details(user_id)
            if not user_details:
                raise AuthenticationFailed('Unauthorized')

            # Create a user-like object
            user = CustomUser(user_id=user_id, **user_details)
            return (user, token)
            
        except Exception as e:
            raise AuthenticationFailed(f'Unauthorized: {str(e)}')
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')
        except jwt.InvalidSignatureError:
            raise AuthenticationFailed('Invalid signature')
        except jwt.InvalidIssuerError:
            raise AuthenticationFailed('Invalid issuer')
        except jwt.InvalidAudienceError:
            raise AuthenticationFailed('Invalid audience')

    def decode_token(self, token):
        try:
            return jwt.decode(token, os.getenv('JWT_SECRET_KEY'), algorithms='HS256')
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')