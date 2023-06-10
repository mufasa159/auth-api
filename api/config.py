from pydantic import BaseSettings


class Configuration(BaseSettings):
   domain: str                          = "https://localhost:8000"
   allowed_hosts: list                  = ["http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:5500"]
   active_mail_service: bool            = False
   access_token_expiration_minute: int  = 60
   refresh_token_expiration_day: int    = 7
   refresh_token_expiration_minute: int = 0
   refresh_token_session_only: bool     = True
   allow_username_change: bool          = False
   environment: str                     = "development"


settings = Configuration()
