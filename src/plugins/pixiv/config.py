from pydantic import BaseSettings


class Config(BaseSettings):
    proxy = ''
    pixiv_token = ''

    class Config:
        extra = "ignore"
