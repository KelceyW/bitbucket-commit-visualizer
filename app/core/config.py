from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    bitbucket_username: str
    bitbucket_display_name: str
    bitbucket_app_password: str
    bitbucket_workspace: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
