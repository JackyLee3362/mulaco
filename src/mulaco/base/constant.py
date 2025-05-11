# 参考 PyInstaller
import os
from pathlib import Path

__version__ = "0.0.1"

PACKAGE_PATH = Path(__file__).parent

SRC_PATH = Path(__file__).parent.parent

CWD_PATH = Path(os.getcwd())
LOG_DIR_PATH = Path(os.getcwd()).joinpath("logs")
CONFIG_DIR_PATH = Path(os.getcwd()).joinpath("config")
DB_DIR_PATH = Path(os.getcwd()).joinpath("db")
JSON_CACHE_PATH = Path(os.getcwd()).joinpath("db", "app.json")
ENV = os.getenv("MULACO_ENV").lower()

if ENV:
    SETTING_FILE_PATH = Path(os.getcwd()).joinpath("config", f"settings.{ENV}.toml")
else:
    SETTING_FILE_PATH = Path(os.getcwd()).joinpath("config", "settings.toml")
