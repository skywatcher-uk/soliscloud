from soliscloud import soliscloud


def test_var_input():
    s = soliscloud.SolisCloud("abc", "xyz")
    assert s.key_id == "abc"
    assert s.key_secret == "xyz"


def test_failed_connection():
    s = soliscloud.SolisCloud("abc", "xyz")
    try:
        s.get_station_list()
    except soliscloud.SolisConnectException as err:
        assert err.args[0] == "There was an error - 403 - Forbidden"
    