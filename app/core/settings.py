from dataclasses import dataclass
from .errors import EnvVarNotFoundError
from dotenv import load_dotenv
from pathlib import Path
import os

@dataclass(frozen=True)
class DatabaseSettings:
    SERVER: str
    USER: str
    PASSWORD: str
    ADDRESS: str
    PORT: str
    DATABASE: str

@dataclass(frozen=True)
class CacheSettings:
    HOST: str
    PORT: int
    DATABASE: int

@dataclass(frozen=True)
class KeysSettings:
    RESEND: str

@dataclass(frozen=True)
class SecretsSettings:
    JWT: str
    PEPPER: str

@dataclass(frozen=True)
class Settings:
    db: DatabaseSettings
    cache: CacheSettings
    keys: KeysSettings
    secrets: SecretsSettings

def load_settings() -> Settings:
    try:
        load_dotenv(Path(__file__).parent.parent.parent / ".env")
        db: DatabaseSettings = DatabaseSettings(
            SERVER = os.environ["DB_SERVER"],
            USER = os.environ["DB_USER"],
            PASSWORD = os.environ["DB_PASSWORD"],
            ADDRESS = os.environ["DB_ADDRESS"],
            PORT = os.environ["DB_PORT"],
            DATABASE = os.environ["DB_DATABASE"]
        )

        cache: CacheSettings = CacheSettings(
            HOST = os.environ["VALKEY_HOST"],
            PORT = int(os.environ["VALKEY_PORT"]),
            DATABASE = int(os.environ["VALKEY_DB"]),
        )

        keys: KeysSettings = KeysSettings(
            RESEND = os.environ["RESEND_API_KEY"],
        )

        secrets: SecretsSettings = SecretsSettings(
            JWT = os.environ["JWT_SECRET"],
            PEPPER = os.environ["PEPPER"],
        )

        return Settings(
            db=db,
            cache=cache,
            keys=keys,
            secrets=secrets
        )

    except KeyError as e:
        raise EnvVarNotFoundError(variable=str(e))

settings = load_settings()
