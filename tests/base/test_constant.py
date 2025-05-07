from mulaco.base import constant


def test_constant():
    assert constant.DB_DIR_PATH.exists()
    assert constant.LOG_DIR_PATH.exists()
    assert constant.CONFIG_DIR_PATH.exists()
