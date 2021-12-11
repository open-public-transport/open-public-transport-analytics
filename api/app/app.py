import random

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
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
        self.group = "",
        self.inhabitants = -1,
        self.area = -1,
        self.population_density = -1,


class RankedValue:
    def __init__(self):
        self.raw_value = -1
        self.overall_rank = -1  # Rank across all cities
        self.grouped_rank = -1  # Rank across cities of same group, e.g. metropolis, small town
        self.overall_percentile = -1  # Percentile across all cities
        self.grouped_percentile = -1  # Percentile across cities of same group, e.g. metropolis, small town


class StationInformation:
    def __init__(self):
        self.transport_type = ""  # all, bus, light_rail, subway, tram
        self.absolute_stations_count: RankedValue = RankedValue(),
        self.absolute_stations_accessibility_count: RankedValue = RankedValue(),
        self.relative_stations_accessibility_percentage: RankedValue = RankedValue(),
        self.relative_stations_per_sqkm: RankedValue = RankedValue(),
        self.relative_stations_per_inhabitant: RankedValue = RankedValue(),


class LineInformation:
    def __init__(self):
        self.transport_type = ""  # all, bus, light_rail, subway, tram
        self.absolute_line_count: RankedValue = RankedValue(),
        self.absolute_line_accessibility_count: RankedValue = RankedValue(),
        self.relative_line_accessibility_percentage: RankedValue = RankedValue(),
        self.relative_line_per_sqkm: RankedValue = RankedValue(),
        self.relative_line_per_inhabitant: RankedValue = RankedValue(),


class TravelDistanceInformation:
    def __init__(self):
        self.transport_type = ""  # all, bus, light_rail, subway, tram
        self.absolute_avg_isochrone_area: RankedValue = RankedValue(),
        self.absolute_avg_isochrone_area_rank: RankedValue = RankedValue(),


class PlaceMetrics:
    def __init__(self):
        self.mobility_index = random.randint(0, 100)
        self.station_information: list[StationInformation] = []
        self.line_information: list[LineInformation] = []
        self.travel_distance_information: list[TravelDistanceInformation] = []


class CityMetrics:
    def __init__(self):
        self.city_basic_information: CityBasicInformation = {}
        self.station_information: list[StationInformation] = []
        self.travel_distance_information: list[TravelDistanceInformation] = []


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
    # TODO Implement
    return PlaceMetrics()


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
