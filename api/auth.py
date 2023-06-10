from fastapi import Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from datetime import datetime, timedelta
from starlette.config import Config
from models import TokenType
from config import settings
import jwt

env = Config("../.env")


class AuthHandler():
   security = HTTPBearer()
   
   def encode_token(self, user_id, token_type: TokenType):
      if token_type == TokenType.access:
         secret = env("ACCESS_TOKEN_SECRET")
         payload = {
            'exp': datetime.utcnow() + timedelta(days=0, minutes=settings.access_token_expiration_minute),
            'iat': datetime.utcnow(),
            'sub': user_id
         }
      elif token_type == TokenType.refresh:
         secret = env("REFRESH_TOKEN_SECRET")
         payload = {
            'exp': datetime.utcnow() + timedelta(days=settings.refresh_token_expiration_day, minutes=settings.refresh_token_expiration_minute),
            'iat': datetime.utcnow(),
            'sub': user_id
         }
      else:
         return "Invalid token name parameter in encode_token()"
         
      return jwt.encode(
         payload,
         secret,
         algorithm='HS256'
      )


   def decode_token(self, token, token_type: TokenType):
      if token_type == TokenType.access:
         secret = env("ACCESS_TOKEN_SECRET")
      elif token_type == TokenType.refresh:
         secret = env("REFRESH_TOKEN_SECRET")
      else:
         return "Invalid token name parameter in decode_token()"
      
      try:
         payload = jwt.decode(token, secret, algorithms=['HS256'])
         return {
            "payload" : payload['sub'],
            "message" : None
         }
      except jwt.ExpiredSignatureError:
         return {
            "payload" : None,
            "message" : "Token has expired"
         }
      except jwt.InvalidTokenError:
         return {
            "payload" : None,
            "message" : "Invalid token"
         }


   # for validating an access token
   def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
      return self.decode_token(auth.credentials, TokenType.access)
   
   # for validating a refresh token
   def auth_token_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
      return self.decode_token(auth.credentials, TokenType.refresh)
