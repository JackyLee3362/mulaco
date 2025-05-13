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


@cli.command("load")
def load():
    service.batch_load_excels()


@cli.command(name="pre")
def pre_fix():
    service.batch_pre_fix_excels()


@cli.command()
def translate(name="trans"):
    service.batch_translate_excels()


@cli.command(name="post")
def post_fix():
    service.batch_post_fix_excels()


@cli.command("export")
def export():
    service.batch_export_excels()
