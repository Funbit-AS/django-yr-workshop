from dateutil import parser

import requests

from django.shortcuts import get_object_or_404, render

from .models import Location


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

    # Fetch the location's forceast, ignoring any errors (to keep example code simple..!)
    r = requests.get(
        url="https://api.met.no/weatherapi/locationforecast/2.0/compact",
        headers={
            "User-Agent": "DjangoWorkshop github.com/Funbit-AS/django-yr-workshop"
        },
        params={"lat": location.latitude, "lon": location.longitude},
        timeout=5,
    )

    # Requests can convert the Yr-response's JSON body into a nice Python dict for us
    data = r.json()

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
