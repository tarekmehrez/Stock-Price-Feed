from app.actions import feed
from app.validators.instruments import Feed
from app.validators.instruments import CandleStick
from app.validators.instruments import CandleStickAggregates


def test_list_instruments_empty(client):
    url = "/instruments"
    response = client.get(url)
    assert response.status_code == 200
    response_json = response.json()
    assert "count" in response_json
    assert "results" in response_json

    assert response_json["results"] == []
    assert response_json["count"] == 0


def test_list_instruments(client, seed_instruments):
    url = "/instruments"
    response = client.get(url)
    assert response.status_code == 200
    response_json = response.json()
    assert "count" in response_json
    assert "results" in response_json

    assert response_json["results"]
    assert response_json["count"] == 4

    instrument = response_json["results"][0]
    assert "isin" in instrument
    assert "description" in instrument


def test_search_instruments(client, seed_instruments):
    search_term = "XK16"
    url = f"/instruments?search={search_term}"
    response = client.get(url)
    assert response.status_code == 200
    response_json = response.json()
    assert "count" in response_json
    assert "results" in response_json

    assert response_json["results"]
    assert response_json["count"] == 1

    instrument = response_json["results"][0]
    assert "isin" in instrument and instrument["isin"] == "XK165564K480"


def test_list_instruments_wrong_page(client, seed_instruments):
    url = "/instruments?page=3"
    response = client.get(url)
    assert response.status_code == 200
    response_json = response.json()
    assert "count" in response_json
    assert "results" in response_json

    assert response_json["results"] == []
    assert response_json["count"] == 0


def test_get_instrument_404(client, seed_instruments):
    url = "/instruments/somerandomisin"
    response = client.get(url)
    assert response.status_code == 404


def test_get_instrument_no_feed(client, seed_instruments):
    url = "/instruments/YA3Q15371402"
    response = client.get(url)
    assert response.status_code == 200
    response_json = response.json()

    assert response_json["isin"] == "YA3Q15371402"


def test_get_instrument_with_feed(client, seed_instruments, mock_function):
    url = "/instruments/YA3Q15371402"

    mock_function("app.actions.feed.instrument_last_price", return_value=500.0)
    mock_function(
        "app.actions.feed.get_instrument_data",
        return_value=Feed(
            candle_sticks=[
                CandleStick(
                    timestamp="2021-04-15T17:07:00",
                    data=CandleStickAggregates(
                        high=917.0588,
                        low=889.4902,
                        open=892.6863,
                        close=900.1765,
                        open_ts="2021-04-15T17:07:19.019000+00:00",
                        close_ts="2021-04-15T17:07:58.381000+00:00",
                    ),
                )
            ]
        ),
    )

    response = client.get(url)
    assert response.status_code == 200
    response_json = response.json()

    assert response_json["isin"] == "YA3Q15371402"
    assert response_json["last_price"] == 500.0
    assert response_json["feed"] == {
        "candle_sticks": [
            {
                "timestamp": "2021-04-15T17:07:00",
                "data": {
                    "high": 917.0588,
                    "low": 889.4902,
                    "open": 892.6863,
                    "close": 900.1765,
                    "open_ts": "2021-04-15T17:07:19.019000+00:00",
                    "close_ts": "2021-04-15T17:07:58.381000+00:00",
                },
            }
        ]
    }
