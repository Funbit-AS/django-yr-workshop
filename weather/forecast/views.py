from dataclasses import dataclass
from time import sleep
from dateutil import parser

import datetime
import logging

import requests

from django.core.cache import cache
from django.views.generic.edit import CreateView
from django.utils import timezone
from django.shortcuts import get_object_or_404, render

from .models import Location

logger = logging.getLogger("django")


@dataclass
class ForecastResponse:
    """
    A little helper class that wraps forecast data along with the datetime at which it is
    due to expire.
    """

    data: dict
    expires_at: datetime.datetime


def fetch_forecast(location: Location) -> ForecastResponse:
    """
    Fetches the forecast and returns it as a ForecastResponse.
    """
    # Deliberately make this slow to highlight why we might want to cache API calls like this.
    logger.info("🌦   Fetching data from Yr for %s", location.name)

    sleep(3)
    r = requests.get(
        url="https://api.met.no/weatherapi/locationforecast/2.0/compact",
        headers={
            "User-Agent": "DjangoWorkshop github.com/Funbit-AS/django-yr-workshop"
        },
        params={"lat": location.latitude, "lon": location.longitude},
        timeout=5,
    )

    return ForecastResponse(
        data=r.json(),
        expires_at=parser.parse(r.headers["Expires"]),
    )


def index(request):
    """
    The site homepage, where we list out Locations.
    """
    locations = Location.objects.order_by("name")
    return render(request, "forecast/index.html", context={"locations": locations})


def location(request, pk: int):
    """
    Fetches and presents weather forecast for Location whose primary key is given by the
    `pk` argument.
    """
    location = get_object_or_404(Location, pk=pk)

    # Look in the cache for a forecast for this location
    cache_key = f"FORECAST_{location.pk}"  # Needs to be unique per location
    data = cache.get(key=cache_key)

    if not data:
        # We didn't have a suitable value in the cache.
        # We have either never fetched this forecast or the data we have has expired
        # We will have to get fresh data from Yr
        logger.info("🐢  No suitable value found in cache ")
        yr_response = fetch_forecast(location=location)
        data = yr_response.data
        # Work out how long it is until this data expires
        # - Just incase, use max to ensure this is never negative
        ttl = (yr_response.expires_at - timezone.now()).seconds
        logger.info("... this forecast will expire in %s seconds", ttl)
        cache.set(key=cache_key, value=data, timeout=ttl)
    else:
        logger.info("🏎  Using a cached value")

    # Now we need to wrangle the data into our forecast format
    # - Again, no error handling for now, we blindly trust the Yr API docs.

    # We can use Python's support for unpacking to assign lat, lon and altitude in one line!
    latitude, longitude, altitude = data["geometry"]["coordinates"]

    # Timeseries
    # - Here we can use a little inline function to keep our code tidy
    def parse_timeseries(datapoint):
        """
        Given a dict from the raw timeseries data, grab the interesting bits and
        return as a new dict that is 'template ready'
        """
        measurements = datapoint["data"]["instant"]["details"]

        try:
            # Watch out! Not all datapoints have symbols
            symbol = datapoint["data"]["next_1_hours"]["summary"]["symbol_code"]
        except KeyError:
            symbol = ""

        return {
            "time": parser.parse(datapoint["time"]),
            "air_temperature": measurements["air_temperature"],
            "wind_speed": measurements["wind_speed"],
            "cloud_area_fraction": measurements["cloud_area_fraction"],
            "symbol": symbol,
        }

    # Apply our helper function to each datapoint in the Yr timeseries list
    timeseries = [parse_timeseries(point) for point in data["properties"]["timeseries"]]

    # Pass the real values we have gathered to the template
    forecast = {
        "latitude": latitude,
        "longitude": longitude,
        "altitude": altitude,
        "symbol": timeseries[0]["symbol"],  # Use symbol from first timeseries datapoint
        "timeseries": timeseries,
    }

    return render(
        request,
        "forecast/location.html",
        context={"location": location, "forecast": forecast},
    )


class CreateLocationView(CreateView):
    template_name = "forecast/new_location.html"

    model = Location
    fields = ["name", "latitude", "longitude"]
