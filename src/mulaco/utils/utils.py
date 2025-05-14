import os
from pathlib import Path

from rich.prompt import Prompt

from mulaco.base.console import console
from mulaco.base.constant import DB_DIR_PATH, ENV

# 开发工具链


def confirm_delete(file_path: Path) -> bool:
    """确认删除文件的函数。"""
    return Prompt.ask(f"确认删除 [bold red]{file_path}[/]? [blue](y/n)", default=True)


def delete_file(file_path: Path, auto_confirm: bool) -> None:
    """删除文件，带有确认逻辑。"""
    if auto_confirm:
        if file_path.exists():
            os.remove(file_path)
            console.print(f"已删除: [bold red]{file_path}[/]")
    else:
        if confirm_delete(file_path):
            os.remove(file_path)
            console.print(f"已删除: [bold red]{file_path}[/]")


def clear_db_cache(auto_confirm: bool = True) -> None:
    """清除数据库缓存和文件。"""
    match ENV:
        case "test" | "dev" | "mock":
            console.print(f"当前环境: [bold blue]{ENV}[/]")
        case "prod":
            console.print("生产环境请手动删除")
            return
        case _:
            console.print("未知环境")
            return

    cache_path = Path(DB_DIR_PATH.joinpath(f"cache.{ENV}.json"))
    db_path = Path(DB_DIR_PATH.joinpath(f"app.{ENV}.db"))

    # 删除缓存文件
    delete_file(cache_path, auto_confirm)

    # 删除数据库文件
    delete_file(db_path, auto_confirm)
