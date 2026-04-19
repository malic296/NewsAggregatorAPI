from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    db_server: str = Field(alias="DB_SERVER")
    db_user: str = Field(alias="DB_USER")
    db_password: str = Field(alias="DB_PASSWORD")
    db_address: str = Field(alias="DB_ADDRESS")
    db_port: int = Field(alias="DB_PORT")
    db_name: str = Field(alias="DB_NAME")

    valkey_host: str = Field(alias="VALKEY_HOST")
    valkey_port: int = Field(alias="VALKEY_PORT")
    valkey_db: int = Field(alias="VALKEY_DB")

    resend_key: str = Field(alias="RESEND_API_KEY")
    jwt_secret: str = Field(alias="JWT_SECRET")
    pepper: str = Field(alias="PEPPER")

    environment: str = Field(alias="ENVIRONMENT", default="dev")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
