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
ENV = os.getenv("MULACO_ENV") or None
SETTINGS_DEFAULT_PATH = Path(os.getcwd()).joinpath("config", "settings.toml")
SETTING_ENV_FILE_PATH = None
if ENV:
    SETTING_ENV_FILE_PATH = Path(os.getcwd()).joinpath("config", ENV, "settings.toml")


def init_path_dir():
    LOG_DIR_PATH.mkdir(exist_ok=True)
    CONFIG_DIR_PATH.mkdir(exist_ok=True)
    DB_DIR_PATH.mkdir(exist_ok=True)
