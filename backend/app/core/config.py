from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "LeitoSync"
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/leitossync"
    
    class Config:
        env_file = ".env"

settings = Settings()
