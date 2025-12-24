import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    #The name of your project
    PROJECT_NAME: str = "Duvet"

    DATABASE_URL: str

    #security settings
    # Run "openssl rand -hex 32" in terminal to generate a good key
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "temporary-secret-key-change-me") #this line is only suitable for development not prod
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()