from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "HexAPI"
    base_url: str
    db_connection_string: str
    default_user: str
    twitter_api_key_secret:str
    twitter_api_key:str
    youtube_verify_token: str
    hub_topic: str
    
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()