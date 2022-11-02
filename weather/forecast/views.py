from dataclasses import dataclass
from time import sleep
from dateutil import parser

import datetime
import logging

import requests

from django.core.cache import cache
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

    # -------------------------------------- YOUR MISSION --------------------------------------

    # It's wasteful for us to fetch the forecast from Yr for every page request when we know
    # that a forecast from 5 minutes ago (or longer) is still fine to use

    # If we're not careful Yr will start throttling our requests which will break our app.

    # In this exercise the API call to Yr has been moved out of this view function and put in
    # its own function 'fetch_forecast'.

    # This new function returns both the yr data we have already been using as well as when the
    # data expires.

    # We want to minimise how often we call this function by using caching to save Yr responses
    # for a period of time. If we have a value in the cache, we can use that rather than fetch
    # new values. Only if we have no value in the cache (or the value we have has expired) do we
    # want to call the function.

    # A 3 second sleep penalty has been added to fetch_forecast to simulate a slow API request.

    # Tips:
    # - Relevant docs: https://docs.djangoproject.com/en/4.1/topics/cache/#the-low-level-cache-api
    # - Use the default cache. This gets wiped every time your local server restarts.
    # - Make sure you cache each location's forecast with a unique key
    # - Start by expiring forecasts after, say, 10 seconds.
    # - Then see if you can use the expires_at value to expire forecasts when Yr wants us to
    # - Replace the two lines that follow this comment with your improved caching functionality.
    # - Everything can stay the same.

    # ----------------------------------------------------------------------------------------

    # Fetch data from yr
    yr_response = fetch_forecast(location=location)
    data = yr_response.data

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
