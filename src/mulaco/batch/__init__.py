# 创建应用
from mulaco.batch.service import BatchService
from mulaco.core.app import App


def init_batch_service() -> BatchService:
    app = App()
    # 初始化应用骨架：读取配置 + 设置缓存 + 配置日志
    app.init_base()
    # 初始化应用：初始化数据库 + 读取应用配置
    app.init_app()
    # 初始化服务
    service = BatchService(app)
    return service
