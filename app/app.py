import os
import random
import sys

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

file_path = os.path.realpath(__file__)
script_path = os.path.dirname(file_path)

# Make library available in path
library_paths = [
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
from cities import Cities

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


class CityBasicInformation:
    def __init__(self):
        self.city_name = ""
        self.federal_state_name = ""
        self.group = ""
        self.inhabitants = -1
        self.area = -1
        self.population_density = -1


class RankedValue:
    def __init__(self):
        self.raw_value = random.randint(1, 24)
        self.overall_rank = -1  # Rank across all cities
        self.grouped_rank = -1  # Rank across cities of same group, e.g. metropolis, small town
        self.overall_percentile = -1  # Percentile across all cities
        self.grouped_percentile = -1  # Percentile across cities of same group, e.g. metropolis, small town


class StationInformation:
    def __init__(self, transport_type=""):
        self.transport_type = transport_type  # all, bus, light_rail, subway, tram
        self.absolute_stations_count = RankedValue()
        self.absolute_stations_accessibility_count = RankedValue()
        self.relative_stations_accessibility_percentage = RankedValue()
        self.relative_stations_per_sqkm = RankedValue()
        self.relative_stations_per_inhabitant = RankedValue()


class LineInformation:
    def __init__(self, transport_type=""):
        self.transport_type = transport_type  # all, bus, light_rail, subway, tram
        self.absolute_line_count = RankedValue()
        self.absolute_line_accessibility_count = RankedValue()
        self.relative_line_accessibility_percentage = RankedValue()
        self.relative_line_per_sqkm = RankedValue()
        self.relative_line_per_inhabitant = RankedValue()


class BikeInformation:
    def __init__(self):
        self.bike_infrastructure_percentage = random.randint(1, 100)


class TravelDistanceInformation:
    def __init__(self):
        self.transport_type = ""  # all, bus, light_rail, subway, tram
        self.absolute_avg_isochrone_area = RankedValue()
        self.absolute_avg_isochrone_area_rank = RankedValue()


class PlaceMetrics:
    def __init__(self, station_information=None, line_information=None, bike_information=None):
        if station_information is None:
            station_information = []
        if line_information is None:
            line_information = []
        self.mobility_index = random.randint(0, 100)
        self.station_information = station_information
        self.line_information = line_information
        self.bike_information = bike_information
        self.travel_distance_information = [TravelDistanceInformation()]


class CityMetrics:
    def __init__(self):
        self.city_basic_information = CityBasicInformation()
        self.station_information = [StationInformation()]
        self.travel_distance_information = [TravelDistanceInformation()]


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
