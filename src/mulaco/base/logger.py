import logging
from datetime import datetime
from pathlib import Path

from rich.logging import RichHandler

default_fmt = "[%(asctime)s] %(name)s - %(levelname)-8s %(funcName)s  : %(message)s"
default_date_fmt = "%Y-%m-%d %H:%M:%S"
default_log_filename_fmt = "%Y-%m-%d.log"


def set_logger(
    logger_name: str,
    console_level: int = logging.DEBUG,
    file_level: int = logging.INFO,
    log_dir: str = None,
    log_filename_fmt: str = None,
    date_fmt: str = None,
    fmt: str = None,
    *args,
    **kwargs,
) -> None:
    """日志配置

    Args:
        logger_name (str): 日志名
        console_level (int, optional): 控制台输出级别. 默认是 logging.DEBUG.
        file_level (int, optional): 文件输出级别. 默认是 logging.INFO.
        log_dir (str, optional): 日志文件夹. 默认是 None.
        log_filename_fmt (str, optional): 日志文件名. 默认是 None.
        date_fmt (str, optional): 日志中日期格式. 默认是 None.
        fmt (str, optional): 日志格式. 默认是 None.
    使用示例
    >>> set_logger("my_module")
    >>> import logging
    >>> log = logging.getLogger("my_module")
    >>> #log.info("hello")
    """
    log = logging.getLogger(logger_name)
    if len(log.handlers) > 0:
        return
    log.setLevel(console_level)

    # 控制台处理器
    console_handler = RichHandler(level=console_level, rich_tracebacks=True)
    log.addHandler(console_handler)

    # 格式化
    if log_dir is None:
        return
    _fmt = fmt or default_fmt
    _date_fmt = date_fmt or default_date_fmt
    formatter = logging.Formatter(fmt=_fmt, datefmt=_date_fmt)
    log_name_fmt = datetime.now().strftime(log_filename_fmt)
    log_dir_obj = Path(log_dir)
    log_dir_obj.mkdir(parents=True, exist_ok=True)
    log_file_path = log_dir_obj.joinpath(log_name_fmt)

    # 文件处理器
    file_handler = logging.FileHandler(filename=log_file_path, encoding="utf-8")
    file_handler.setLevel(file_level)

    # 给处理器设置格式
    file_handler.setFormatter(formatter)

    # 添加处理器
    log.addHandler(file_handler)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
