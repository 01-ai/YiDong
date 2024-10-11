from pydantic_settings import BaseSettings


class Config(BaseSettings):
    api_key: str = ""
    api_key_header: str = "x-api-key"
    base_url: str = "https://api-yidong.lingyiwanwu.com/v1"

    class Config:
        env_prefix = "YIDONG_"


CONFIG = Config()
