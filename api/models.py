from pydantic import BaseModel
from enum import Enum


class Role(Enum):
   admin = "admin"
   maintainer = "maintainer"
   user = "user"
 

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
