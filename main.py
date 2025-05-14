import sys
from pathlib import Path

from dotenv import load_dotenv

# 环境变量
sys.path.insert(0, str(Path(__file__).resolve().parent.joinpath("src")))
# 加载 .env 变量
load_dotenv()

if __name__ == "__main__":
    from mulaco.cli import cli

    cli()
