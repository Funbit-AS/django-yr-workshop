from datetime import datetime

from django.utils import timezone
from django.shortcuts import render


def forecast_bergen(request):
    """
    Collects weather forecast for Bergen and feeds it to the bergen template.
    """

    # ----------------------------
    # YOUR MISSION
    # ----------------------------
    
    # 1. Use the requests library to fetch data for Bergen from Yr
    # 2. Edit the forecast dictionary below to use real data from the JSON response

    # TIPS:
    # - Yr API Docs: https://developer.yr.no/doc/GettingStarted/
    # - Base url for API call: https://api.met.no/weatherapi/locationforecast/2.0/compact
    # - Yr require that you set a User-Agent header, use "<Your Name> <Your Email>"
    # - The coordinates from Bergen to use in your API request are:
    # - - lat: 60.3929
    # - - lon: 5.3241
    # - Never use more coordinates with more than 4 decimal places or Yr may reject your call.
    # - Do not alter the structure of the forecast dictionary, just fill it with real data.
    # - The real data from Yr will have many more timeseries points than 3. 


    forecast = {
        "latitude": "0.0000",
        "longitude": "0.0000",
        "altitude": "0",
        "symbol": "cloudy",  # Use symbol from first timeseries datapoint
        "timeseries": [
            {
                "time": timezone.make_aware(datetime(2022,11,1,12,0)),
                "air_temperature": 8.2,
                "wind_speed": 0.8,
                "cloud_area_fraction": 100.0,
                "symbol": "cloudy"
            },
            {
                "time": timezone.make_aware(datetime(2022,11,1,13,0)),
                "air_temperature": 7.9,
                "wind_speed": 2.2,
                "cloud_area_fraction": 94.5,
                "symbol": "rain"
            },
            {
                "time": timezone.make_aware(datetime(2022,11,1,14,0)),
                "air_temperature": 7.7,
                "wind_speed": 3.2,
                "cloud_area_fraction": 88.9,
                "symbol": "rainandthunder"
            }
            # ... more
        ]
    }
    return render(request, "forecast/bergen.html", context={"forecast": forecast})