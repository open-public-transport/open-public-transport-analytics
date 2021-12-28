import os
import sys

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

file_path = os.path.realpath(__file__)
script_path = os.path.dirname(file_path)

# Make library available in path
library_paths = [
    os.path.join(script_path, "model"),
    os.path.join(script_path, "..", "lib"),
    os.path.join(script_path, "..", "lib", "config"),
    os.path.join(script_path, "..", "lib", "cloud"),
    os.path.join(script_path, "..", "lib", "loader", "osmnx"),
    os.path.join(script_path, "..", "lib", "loader", "overpass"),
    os.path.join(script_path, "..", "lib", "loader", "peartree"),
    os.path.join(script_path, "..", "lib", "converter"),
    os.path.join(script_path, "..", "lib", "log"),
]

for p in library_paths:
    if not (p in sys.path):
        sys.path.insert(0, p)

# Import library classes
from bike_information import BikeInformation
from city_metrics import CityMetrics
from place_metrics import PlaceMetrics
from station_information import StationInformation
from line_information import LineInformation

# Set paths
data_path = os.path.join(script_path, "..", "data", "data")
base_results_path = os.path.join(script_path, "..", "results", "results")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "https://open-public-transport-qa.web.app",
        "https://openpublictransport.de",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#
# Dashboard
#

@app.get("/isochrones")
def get_isochrones(city):
    # TODO Implement
    return {}


@app.get("/transport")
def get_isochrones(city, transport):
    # TODO Implement
    return {}


#
# Comparison
#

@app.get("/place")
def get_metrics(lat, lon):
    return PlaceMetrics(
        station_information=[
            StationInformation(transport_type="bus"),
            StationInformation(transport_type="light_rail"),
            StationInformation(transport_type="subway"),
            StationInformation(transport_type="tram")
        ],
        line_information=[
            LineInformation(transport_type="bus"),
            LineInformation(transport_type="light_rail"),
            LineInformation(transport_type="subway"),
            LineInformation(transport_type="tram")
        ],
        bike_information=BikeInformation()
    )


@app.get("/isochrone")
def get_isochrones(lat, lon, transport):
    # TODO Implement
    return {}


#
# Overview
#

@app.get("/cities")
def get_cities():
    # TODO Implement
    return [
        CityMetrics()
    ]


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
