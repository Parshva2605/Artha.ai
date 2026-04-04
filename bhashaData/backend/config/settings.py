from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    reddit_client_id: str = Field(default="", alias="REDDIT_CLIENT_ID")
    reddit_client_secret: str = Field(default="", alias="REDDIT_CLIENT_SECRET")
    reddit_user_agent: str = Field(default="BhashaData/1.0", alias="REDDIT_USER_AGENT")
    redis_url: str = Field(default="redis://localhost:6379", alias="REDIS_URL")
    database_url: str = Field(default="sqlite:///./bhashaData.db", alias="DATABASE_URL")
    datasets_storage_path: str = Field(default="./datasets", alias="DATASETS_STORAGE_PATH")
    next_public_api_url: str = Field(default="http://localhost:8000", alias="NEXT_PUBLIC_API_URL")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
