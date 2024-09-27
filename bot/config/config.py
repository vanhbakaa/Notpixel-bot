from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    API_ID: int
    API_HASH: str


    REF_LINK: str = "https://t.me/notpixel/app?startapp=f6624523270"
    AUTO_UPGRADE: bool = True
    AUTO_TASK: bool = True

    USE_PROXY_FROM_FILE: bool = False


settings = Settings()

