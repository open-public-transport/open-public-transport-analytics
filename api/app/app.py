import random

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
        self.raw_value = -1
        self.overall_rank = -1  # Rank across all cities
        self.grouped_rank = -1  # Rank across cities of same group, e.g. metropolis, small town
        self.overall_percentile = -1  # Percentile across all cities
        self.grouped_percentile = -1  # Percentile across cities of same group, e.g. metropolis, small town


class StationInformation:
    def __init__(self, transport_type = ""):
        self.transport_type = transport_type  # all, bus, light_rail, subway, tram
        self.absolute_stations_count = RankedValue()
        self.absolute_stations_accessibility_count = RankedValue()
        self.relative_stations_accessibility_percentage = RankedValue()
        self.relative_stations_per_sqkm = RankedValue()
        self.relative_stations_per_inhabitant = RankedValue()


class LineInformation:
    def __init__(self, transport_type = ""):
        self.transport_type = transport_type # all, bus, light_rail, subway, tram
        self.absolute_line_count = RankedValue()
        self.absolute_line_accessibility_count = RankedValue()
        self.relative_line_accessibility_percentage = RankedValue()
        self.relative_line_per_sqkm = RankedValue()
        self.relative_line_per_inhabitant = RankedValue()


class TravelDistanceInformation:
    def __init__(self):
        self.transport_type = ""  # all, bus, light_rail, subway, tram
        self.absolute_avg_isochrone_area = RankedValue()
        self.absolute_avg_isochrone_area_rank = RankedValue()


class PlaceMetrics:
    def __init__(self, station_information = [], line_information  = []):
        self.mobility_index = random.randint(0, 100)
        self.station_information = station_information
        self.line_information = line_information
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
        station_information= [
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
        ]
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
