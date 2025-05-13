import pytest

from mulaco.batch.service import BatchService


@pytest.fixture(scope="module")
def service(app):
    return BatchService(app)


def test_1_batch_service(service: BatchService):
    service.batch_load_excels()


def test_2_batch_service(service: BatchService):
    service.batch_pre_fix_excels()


def test_3_batch_service(service: BatchService):
    service.batch_translate_excels()


def test_4_batch_service(service: BatchService):
    service.batch_post_fix_excels()


def test_5_batch_service(service: BatchService):
    service.batch_export_excels()
