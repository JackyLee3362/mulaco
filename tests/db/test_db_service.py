from mulaco.db.service import DbService
from mulaco.models.bo_model import ExcelSheetBO


def test_1_测试数据数量(mem_db_data: DbService):
    r1 = mem_db_data.get_all_exsh()
    assert len(r1) > 0

    r2 = mem_db_data.get_all_cell_info()
    assert len(r2) > 0

    r3 = mem_db_data.get_all_trans_info()
    assert len(r3) > 0


def test_2_测试未翻译的Cell(mem_db_data: DbService):
    exsh = ExcelSheetBO(id=1, excel="ex1", sheet="sh1")
    res = mem_db_data.get_not_translated_cells(exsh, src="en", dst="zh", col=2)
    print("未翻译的 Cell ")
    for res_cell in res:
        print(res_cell)
    # TODO assert


# TODO 还有测试 3 个
