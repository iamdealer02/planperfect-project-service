# middleware.py

from django.utils.deprecation import MiddlewareMixin
from rest_framework.exceptions import AuthenticationFailed
from projectService.utils.JWT import JWTAuthentication, CustomUser

class JWTAuthenticationMiddleware(MiddlewareMixin):

    def process_request(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', None)
        if not auth_header:
            return None
        
        token = auth_header.split(' ')[1] if auth_header and ' ' in auth_header else None
        if not token:
            return None

        try:
            jwt_auth = JWTAuthentication()
            payload = jwt_auth.decode_token(token)
            if not payload:
                raise AuthenticationFailed('Unauthorized')
            
            user_id = payload.get('user_id')
            if not user_id:
                raise AuthenticationFailed('Unauthorized')

       

            # Create a user-like object
            user = CustomUser(user_id=user_id)

            # Optionally set additional user attributes here
            # user.username = user_details.get('username', '')
            # user.is_active = user_details.get('is_active', True)
            # user.is_staff = user_details.get('is_staff', False)
            # user.is_superuser = user_details.get('is_superuser', False)

            request.user = user
            
        except Exception as e:
            raise AuthenticationFailed(f'Unauthorized: {str(e)}')

