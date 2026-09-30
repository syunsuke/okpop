from okpop import database


def test_database_module():
    assert database.TBL_CENSUS == "census"
