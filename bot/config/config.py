from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    API_ID: int
    API_HASH: str


    REF_LINK: str = "https://t.me/notpixel/app?startapp=f6624523270"
    X3POINTS: bool = True
    AUTO_UPGRADE_PAINT_REWARD: bool = True
    AUTO_UPGRADE_RECHARGE_SPEED:bool = True
    AUTO_UPGRADE_RECHARGE_ENERGY:bool = True
    AUTO_TASK: bool = True

    NIGHT_MODE: bool = True
    SLEEP_TIME: list[int] = [0, 7] # your time zone

    DELAY_EACH_ACCOUNT: list[int] = [10,15]
    SLEEP_TIME_BETWEEN_EACH_ROUND: list[int] = [1000, 1500]
    USE_PROXY_FROM_FILE: bool = False


settings = Settings()

