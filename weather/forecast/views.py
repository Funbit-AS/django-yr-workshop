from datetime import datetime
from dateutil import parser

import requests

from django.utils import timezone
from django.shortcuts import render


def forecast_bergen(request):
    """
    Collects weather forecast for Bergen and feeds it to the bergen template.
    """
    # Fetch forceast for Bergen, ignoring any errors (to keep example code simple..!)
    r = requests.get(
        url="https://api.met.no/weatherapi/locationforecast/2.0/compact",
        headers={"User-Agent": "DjangoWorkshop github.com/Funbit-AS/django-yr-workshop"},
        params={"lat": 60.3929,"lon": 5.3241}
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
            "symbol": symbol
        }

    # Apply our helper function to each datapoint in the Yr timeseries list
    timeseries = [
        parse_timeseries(point) for point in data["properties"]["timeseries"]
    ]

    # Pass the real values we have gathered to the template
    forecast = {
        "latitude":latitude,
        "longitude": longitude,
        "altitude": altitude,
        "symbol": timeseries[0]["symbol"],  # Use symbol from first timeseries datapoint
        "timeseries": timeseries
    }

    return render(request, "forecast/bergen.html", context={"forecast": forecast})