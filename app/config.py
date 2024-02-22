from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "HexAPI"
    base_url: str
    youtube_verify_token: str
    twitter_api_key:str
    twitter_api_key_secret:str
    db_connection_string: str
    default_user: str
    
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()