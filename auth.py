import jwt
import os
import enum
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv(".env")

class TokenType(enum.Enum):
   access = "access"
   refresh = "refresh"


class AuthHandler():
   security = HTTPBearer()
   
   def encode_token(self, user_id, token_type: TokenType):
      if token_type == TokenType.access:
         secret = os.environ.get("ACCESS_TOKEN_SECRET")
         payload = {
            'exp': datetime.utcnow() + timedelta(days=0, minutes=15),
            'iat': datetime.utcnow(),
            'sub': user_id
         }
      elif token_type == TokenType.refresh:
         secret = os.environ.get("REFRESH_TOKEN_SECRET")
         payload = {
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
         secret = os.environ.get("ACCESS_TOKEN_SECRET")
      elif token_type == TokenType.refresh:
         secret = os.environ.get("REFRESH_TOKEN_SECRET")
      else:
         return "Invalid token name parameter in encode_token()"
      
      try:
         payload = jwt.decode(token, secret, algorithms=['HS256'])
         return payload['sub']
      except jwt.ExpiredSignatureError:
         raise HTTPException(status_code=401, detail='Token has expired')
      except jwt.InvalidTokenError as e:
         raise HTTPException(status_code=401, detail='Invalid token')


   # for validating using access token
   def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
      return self.decode_token(auth.credentials, TokenType.access)
   
   # for validating a refresh token
   def auth_token_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
      return self.decode_token(auth.credentials, TokenType.refresh)
