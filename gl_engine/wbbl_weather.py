"""Optional no-key venue forecast, with explicit licensing and missing-data labels.

Open-Meteo is free for noncommercial use only. Forecast is not an observed
pitch report, dew measurement or automatic fantasy-performance adjustment.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from functools import lru_cache
import os
import time
import requests


@lru_cache(maxsize=128)
def _forecast(latitude: float, longitude: float, utc_day: str, cache_bucket: int) -> dict:
    target = datetime.fromisoformat(utc_day)
    start = (target - timedelta(days=1)).date().isoformat()
    end = (target + timedelta(days=1)).date().isoformat()
    response = requests.get("https://api.open-meteo.com/v1/forecast", params={
        "latitude":latitude, "longitude":longitude,
        "hourly":"temperature_2m,relative_humidity_2m,precipitation_probability,wind_speed_10m",
        "timezone":"UTC", "start_date":start,"end_date":end}, timeout=8)
    response.raise_for_status()
    return response.json()


def venue_forecast(fixture: dict) -> dict:
    if fixture.get("latitude") is None or fixture.get("longitude") is None:
        return {"status":"COORDINATES_NOT_REGISTERED","source":None}
    if os.getenv("CRICKET_OPEN_METEO_NONCOMMERCIAL_ACK") != "1":
        return {"status":"FREE_TIER_LICENSE_ACK_REQUIRED","source":None,
                "note":"Set CRICKET_OPEN_METEO_NONCOMMERCIAL_ACK=1 only when usage is allowed by free noncommercial terms."}
    start=datetime.fromisoformat(fixture["scheduled_start_utc"]).astimezone(timezone.utc)
    try:
        data=_forecast(float(fixture["latitude"]),float(fixture["longitude"]),
                       start.isoformat(),int(time.time()//900))
        hourly=data.get("hourly") or {}
        times=hourly.get("time") or []
        candidates=[]
        for i,t in enumerate(times):
            candidate=datetime.fromisoformat(t).replace(tzinfo=timezone.utc)
            delta=abs((candidate-start).total_seconds())
            if delta <= 3600:
                candidates.append((delta,i))
        if not candidates:
            return {"status":"FORECAST_UNAVAILABLE","source":"open-meteo"}
        index=min(candidates)[1]
        fields={
            "temperature_c": "temperature_2m",
            "humidity_pct": "relative_humidity_2m",
            "rain_probability_pct": "precipitation_probability",
            "wind_kmh": "wind_speed_10m"
        }
        values={}
        for dest,key in fields.items():
            series=hourly.get(key) or []
            values[dest]=series[index] if index < len(series) else None
        return {"status":"FORECAST_ONLY_NOT_ACTUAL_PITCH",
                "forecast_for_utc":times[index]+"Z",**values,
                "source":"https://open-meteo.com/",
                "license_note":"Free-tier noncommercial use and provider attribution required",
                "observed_at_utc":datetime.now(timezone.utc).isoformat()}
    except (ValueError,KeyError,TypeError,requests.RequestException):
        return {"status":"FORECAST_UNAVAILABLE","source":"open-meteo"}
