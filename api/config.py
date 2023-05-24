from pydantic import BaseSettings

class Configuration(BaseSettings):
   domain: str = "https://localhost:8000"
   active_mail_service: bool = False
   access_token_expiration_minute: int = 60
   environment: str = "development"


settings = Configuration()