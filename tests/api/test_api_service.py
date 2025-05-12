from mulaco.api.service import ApiService
from mulaco.base.scaffold import Scaffold
from mulaco.db.service import DbService


def test_api_service():
    db = DbService("sqlite:///db/test.db")
    app = Scaffold()

    service = ApiService(db, app)

    service.setup_batch_excel("config/batch1.toml")

    service.api_load_excels()
    service.api_pre_fix_excels()
    service.api_translate_excels()
    service.api_post_fix_excels()
    service.api_export_excels()
