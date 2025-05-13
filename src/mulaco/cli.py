import typer

from mulaco.batch.service import BatchService
from mulaco.core.app import App

# 创建应用
app = App()

# 初始化数据库
app.init_base()

# 初始化应用
app.init_app()

# 初始化服务
service = BatchService(app)

# 初始化命令行
cli = typer.Typer()


@cli.command(name="load", help="批量导入 Excel")
def load():
    service.batch_load_excels()


@cli.command(name="pre", help="批量修复原始数据")
def pre_fix():
    service.batch_pre_fix_excels()


@cli.command(name="trans", help="批量翻译")
def translate():
    service.batch_translate_excels()


@cli.command(name="post", help="批量修复翻译")
def post_fix():
    service.batch_post_fix_excels()


@cli.command(name="export", help="批量导出 Excels")
def export():
    service.batch_export_excels()
