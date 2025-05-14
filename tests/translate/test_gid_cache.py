import pytest

from mulaco.translate.helper import LocalGidCache


@pytest.fixture(scope="module")
def gid_cache(app):
    return LocalGidCache(app.cache)


def test_get_glossary(gid_cache: LocalGidCache):
    gid_cache.get_cached_gid("en", "zh")
