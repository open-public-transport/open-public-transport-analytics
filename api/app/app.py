import random

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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


class PointOnInterest(BaseModel):
    lat = 0
    lon = 0


class Metrics:
    mobility_index = 0

    def __init__(self, mobility_index):
        self.mobility_index = mobility_index


class CityBasicInformation:
    city_name = ""
    federal_state_name = ""
    group = "",
    inhabitants = -1,
    area = -1,
    population_density = -1,


class RankedValue:
    raw_value = -1
    overall_rank = -1  # Rank across all cities
    grouped_rank = -1  # Rank across cities of same group, e.g. metropolis, small town
    overall_percentile = -1  # Percentile across all cities
    grouped_percentile = -1  # Percentile across cities of same group, e.g. metropolis, small town


class StationInformation:
    transport_type = ""  # all, bus, light_rail, subway, tram
    absolute_stations_count: RankedValue = RankedValue(),
    absolute_stations_accessibility_count: RankedValue = RankedValue(),
    relative_stations_accessibility_percentage: RankedValue = RankedValue(),
    relative_stations_per_sqkm: RankedValue = RankedValue(),
    relative_stations_per_inhabitant: RankedValue = RankedValue(),


class LineInformation:
    transport_type = ""  # all, bus, light_rail, subway, tram
    absolute_line_count: RankedValue = RankedValue(),
    absolute_line_accessibility_count: RankedValue = RankedValue(),
    relative_line_accessibility_percentage: RankedValue = RankedValue(),
    relative_line_per_sqkm: RankedValue = RankedValue(),
    relative_line_per_inhabitant: RankedValue = RankedValue(),


class TravelDistanceInformation:
    transport_type = ""  # all, bus, light_rail, subway, tram
    absolute_avg_isochrone_area: RankedValue = RankedValue(),
    absolute_avg_isochrone_area_rank: RankedValue = RankedValue(),


class Place:
    mobility_index = random.randint(0, 100)
    station_information: list[StationInformation] = []
    line_information: list[LineInformation] = []
    travel_distance_information: list[TravelDistanceInformation] = []
    pass


class City:
    city_basic_information: CityBasicInformation = {}
    station_information: list[StationInformation] = []
    travel_distance_information: list[TravelDistanceInformation] = []


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
    return Place()


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
        City()
    ]
