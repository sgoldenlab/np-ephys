import os
import pathlib
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict, TomlConfigSettingsSource
from pydantic import BaseModel
from typing import Tuple, Type
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv("config/.env"))
run_config_file = os.getenv('RUN_CONFIG_FILE')

class PathsConfig(BaseModel):
    drive: pathlib.Path
    meta_dir: pathlib.Path
    data_dir: pathlib.Path
    dataset_dir: pathlib.Path
    raw_dir: pathlib.Path
    processed_dir: pathlib.Path
    alignment_dir: pathlib.Path
    output_dir: pathlib.Path

# # class LoggingConfig(BaseSettings):
# #     log_level: str = "INFO"
# #     log_file: pathlib.Path = pathlib.Path("logs/app.log")

class ExperimentConfig(BaseSettings):
    dir: str
    recordings: dict[str, dict]
    # WIP

class Settings(BaseSettings):
    paths: PathsConfig
    # # logging: LoggingConfig
    experiment: ExperimentConfig

    model_config = SettingsConfigDict(
        toml_file = ["config/default_config.toml", run_config_file if run_config_file else "config/run_config.toml"],
        env_prefix='PIPELINE_',
        env_nested_delimiter='__',
        env_file='config/.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore',
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (TomlConfigSettingsSource(settings_cls), dotenv_settings)


settings = Settings()
