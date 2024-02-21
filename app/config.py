from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "HexAPI"
    # bot_token: str
    # discord_channel_id: int
    # youtube_developer_key: str
    youtube_channel_id: str
    
    model_config = SettingsConfigDict(env_file=".env")

