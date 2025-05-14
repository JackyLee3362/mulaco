import typer

from mulaco.batch import init_batch_service
from mulaco.utils.utils import clear_db_cache

# 初始化命令行
cli = typer.Typer()


@cli.command(name="run", help="所有步骤：导入 + 预处理 + 翻译 + 修复 + 导出")
def run():
    init_batch_service().batch_run()


@cli.command(name="load", help="批量导入 Excel")
def load():
    init_batch_service().batch_load_excels()


@cli.command(name="pre", help="批量预处理原始数据")
def pre_process():
    init_batch_service().batch_pre_process_excels()


@cli.command(name="trans", help="批量翻译")
def translate():
    init_batch_service().batch_translate_excels()


@cli.command(name="post", help="批量修复翻译")
def post_fix():
    init_batch_service().batch_post_fix_excels()


@cli.command(name="export", help="批量导出 Excels")
def export():
    init_batch_service().batch_export_excels()


@cli.command(name="dev:clear", help="开发工具：删除数据库 + 缓存")
def dev_clear(confirm: bool = False):
    clear_db_cache(confirm)
