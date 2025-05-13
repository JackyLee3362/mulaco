import os
import sys

from dotenv import load_dotenv

# 环境变量
sys.path.insert(0, os.path.dirname(__file__) + "/src")
#
load_dotenv()

if __name__ == "__main__":
    from mulaco.cli import cli

    cli()
