from pydantic import BaseSettings

class Configuration(BaseSettings):
   domain: str = "https://localhost:8000"
   active_mail_service: bool = False
   environment: str = "development"


settings = Configuration()