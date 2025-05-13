try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    import tomli as tomllib

__all__ = ("TomlConfig",)


class _AttrDict(dict):
    """类似字典的类，比如
    >>> A = _AttrDict()
    >>> A['name'] = 'Bob'
    >>> assert A.name == 'Bob' # 即可以通过 A.name 访问字典变量
    >>> A.age = 20
    >>> assert A.age == 20
    """

    def __getitem__(self, key: str):
        value = super().__getitem__(key)
        if isinstance(value, dict):
            self[key] = value = _AttrDict(value)
        return value

    def __getattr__(self, key: str) -> object:
        return self[key]

    def __setattr__(self, key: str, value: object):
        self[key] = value
        return


class TomlConfig(_AttrDict):

    def __init__(self, path=None, params=None):
        """初始化, path 是文件路径, params 是默认值"""
        super().__init__()
        if path:
            self.load_file(path, params)
        return

    def load_file(self, path, params: dict = None):
        """从文件中加载"""
        with open(path, "rb") as f:
            data = tomllib.load(f)
        if params:
            self.setdefault(params).update(data)
        else:
            self = recursive_update(self, data)


def recursive_update(src: dict, data: dict):
    for key, val in data.items():
        _v = src.get(key)
        if isinstance(val, dict) and isinstance(_v, dict):
            src[key] = recursive_update(_v, val)
        else:
            src[key] = val
    return src


if __name__ == "__main__":
    import doctest

    doctest.testmod()
