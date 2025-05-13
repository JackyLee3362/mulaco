import pytest

from mulaco.translate.cli import GidCache


@pytest.fixture(scope="module")
def gid_cache(app):
    return GidCache(app.cache)


def test_get_glossary(gid_cache: GidCache):
    gid_cache.get_cached_gid("en", "zh")
