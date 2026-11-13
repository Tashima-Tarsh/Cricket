"""Weather data: forecast is labelled and license-ack gate is enforced."""
from datetime import datetime,timezone,timedelta
from unittest.mock import patch
import os
from gl_engine.wbbl_weather import venue_forecast,_forecast


def fixture():
    start=datetime.now(timezone.utc).replace(minute=0,second=0,microsecond=0)+timedelta(hours=1)
    return {"match_id":"fixture1", "scheduled_start_utc":start.isoformat(),
            "latitude":-33.9,"longitude":151.2}


def test_weather_blocks_without_license_ack():
    with patch.dict(os.environ,{"CRICKET_OPEN_METEO_NONCOMMERCIAL_ACK":"0"}):
        assert venue_forecast(fixture())["status"]=="FREE_TIER_LICENSE_ACK_REQUIRED"


def test_forecast_uses_only_provided_hourly_observations():
    f=fixture()
    stamp=datetime.fromisoformat(f["scheduled_start_utc"]).strftime("%Y-%m-%dT%H:%M")
    hourly={
        "time":[stamp],"temperature_2m":[24.0],
        "relative_humidity_2m":[60.0],
        "precipitation_probability":[30.0],"wind_speed_10m":[12.0]
    }
    with patch.dict(os.environ,{"CRICKET_OPEN_METEO_NONCOMMERCIAL_ACK":"1"}):
        with patch("gl_engine.wbbl_weather._forecast",return_value={"hourly":hourly}):
            result=venue_forecast(f)
    assert result["status"]=="FORECAST_ONLY_NOT_ACTUAL_PITCH"
    assert result["temperature_c"]==24.0
    assert result["rain_probability_pct"]==30.0
