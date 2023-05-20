from pydantic import BaseModel
from fastapi import Query
from enum import Enum

class Role(Enum):
   admin = "admin"
   maintainer = "maintainer"
   user = "user"


class Account(BaseModel):
   uid: str
   name_first: str
   name_last: str
   image: str | None = None
   role: Role
   username: str
   email: str
   hash: str
   bio: str | None = None
   created_at: str
   last_login_at: str | None = None
   last_login_ip: str | None = None
   current_login_at: str | None = None
   current_login_ip : str | None = None
   login_count: int
   confirmed_email: bool


class TokenData(BaseModel):
   id: int
   uid: str
   access_token: str
   refresh_token: str
   created_at: str
   pair_count: int
   refresh_token_use_count: int
   refresh_token_last_used_at: str | None = None
 

class NewUser(BaseModel):
   name_first: str
   name_last: str
   username: str
   email: str
   password: str


class UserLogin(BaseModel):
   username: str
   password: str
   

class Profile(BaseModel):
   name_first: str
   name_last: str
   image: str | None = None
   username: str
   bio: str | None = None


class TokenType(Enum):
   access = "access"
   refresh = "refresh"

   
class Token(BaseModel):
   value: str = Query(max_length=128, min_length=128)