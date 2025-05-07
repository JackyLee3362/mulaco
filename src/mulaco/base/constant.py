# 参考 PyInstaller
import os
from pathlib import Path

__version__ = "0.0.1"

PACKAGE_PATH = Path(__file__).parent

SRC_PATH = Path(__file__).parent.parent

CWD_PATH = Path(os.getcwd())
LOG_DIR_PATH = Path(os.getcwd()).joinpath("logs")
CONFIG_DIR_PATH = Path(os.getcwd()).joinpath("config")
SETTING_FILE_PATH = Path(os.getcwd()).joinpath("config", "settings.toml")
DB_DIR_PATH = Path(os.getcwd()).joinpath("db")
KVDB_PATH = Path(os.getcwd()).joinpath("db", "app.json")
