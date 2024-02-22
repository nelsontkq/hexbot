from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "HexAPI"
    # bot_token: str
    # discord_channel_id: int
    # youtube_developer_key: str
    base_url: str
    youtube_channel_id: str
    youtube_verify_token: str
    twitter_bearer_token: str
    twitter_api_key:str
    twitter_api_key_secret:str
    twitter_client_id:str
    twitter_client_secret:str
    twitter_access_token:str
    twitter_access_token_secret: str
    db_connection_string: str
    default_user: str
    
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()