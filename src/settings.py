import typing
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ("TGBotSettings",)


class TGBotSettings(BaseSettings):
    debug: bool = Field(default=False)

    api_id: int = Field("22244987")
    api_hash: str = Field("5b2b7b9575535af6cbdb3335a5d95366")
    token: str = Field("7698584724:AAFWGnZlNt88TsZvxXrd0fcm7o8VfU5ntTM")

    model_config: typing.ClassVar[SettingsConfigDict] = SettingsConfigDict(
        extra="ignore",
        frozen=True,
        case_sensitive=False,
        env_file=Path(__file__).parent.parent / ".env",
        env_prefix="BOT_",
    )
