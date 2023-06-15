from pydantic import BaseModel
from pydantic.datetime_parse import datetime
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
   

class ProfileWithNoAuth(BaseModel):
   name_first: str
   name_last: str
   image: str | None = None
   username: str
   bio: str | None = None
   

class ProfileWithAuth(BaseModel):
   name_first: str
   name_last: str
   image: str | None = None
   username: str
   bio: str | None = None
   email: str
   last_login_at: datetime
   last_login_ip: str
   created_at: datetime
   updated_at: datetime | None = None
   confirmed_email: bool


class TokenType(Enum):
   access = "access"
   refresh = "refresh"
