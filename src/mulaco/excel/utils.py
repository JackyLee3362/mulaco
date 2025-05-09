def excel_col_alpha_increment(column_name: str, num: int):
    """
    将 Excel 列名递增指定数量
    :param column_name: str, Excel 列名（如 'A', 'B', 'AA'）
    :param num: int, 递增数量
    :return: str, 递增后的列名
    """
    return excel_col_num2alpha(excel_col_alpha2num(column_name) + num)


def excel_col_alpha2num(column_name: str):
    """
    将 Excel 列名转换为列索引（从 1 开始）
    :param column_name: str, Excel 列名（如 'A', 'B', 'AA'）
    :return: int, 列索引
    """
    column_index = 0
    for char in column_name:
        column_index = column_index * 26 + (ord(char.upper()) - ord("A") + 1)
    return column_index


def excel_col_num2alpha(column_index: int):
    """
    将列索引转换为列名（如 1 转换为 'A'）
    :param column_index: int, 列索引（从 1 开始）
    :return: str, 列名
    """
    res = []
    while column_index > 0:
        column_index, remainder = divmod(column_index - 1, 26)
        res.append(chr(remainder + 65))
    return "".join(res[::-1])
