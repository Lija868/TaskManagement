from rest_framework import authentication
from rest_framework import exceptions
from api_v0.JwtValidator import jwtValidator

class TokensAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        token_id = request.headers.get("Authorization", "")
        try:
            payload = jwtValidator(token_id)
            return payload, None
        except:
            raise exceptions.AuthenticationFailed('Token expired.')















