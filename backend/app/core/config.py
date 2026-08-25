import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    
    # Postgres
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "solar_wind_db"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@postgres:5432/solar_wind_db"
    
    # MongoDB
    MONGO_USER: str = "mongo"
    MONGO_PASSWORD: str = "mongo"
    MONGO_HOST: str = "mongo"
    MONGO_PORT: int = 27017
    MONGO_DB_NAME: str = "solar_wind_mongo"
    MONGO_URL: str = "mongodb://mongo:mongo@mongo:27017"
    
    # JWT
    JWT_SECRET: str = "supersecretjwtsecretkey"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
