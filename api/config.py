from pydantic import BaseSettings


class Configuration(BaseSettings):
   domain: str                          = "https://localhost:8000"
   active_mail_service: bool            = False
   access_token_expiration_day: int     = 0
   access_token_expiration_minute: int  = 60
   refresh_token_expiration_day: int    = 7
   refresh_token_expiration_minute: int = 0
   allow_username_change: bool          = False
   environment: str                     = "development"


settings = Configuration()
