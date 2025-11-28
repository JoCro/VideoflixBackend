from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication class that retrieves the token from an HTTP-only cookie.
    If there is no token or it's invalid/expired, the request is treated as anonymous instead of raising an error. 
    """

    def authenticate(self, request):
        header = self.get_header(request)
        if header is not None:
            raw_token = self.get_raw_token(header)
        else:
            raw_token = request.COOKIES.get('access_token')

        if not raw_token:
            return None
        try:
            validated_token = self.get_validated_token(raw_token)
        except (InvalidToken, TokenError) as e:
            return None

        try:
            user = self.get_user(validated_token)
        except Exception as e:
            return None
        return (user, validated_token)
