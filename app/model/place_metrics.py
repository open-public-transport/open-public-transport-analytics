import random

from travel_distance_information import TravelDistanceInformation


class PlaceMetrics:
    def __init__(self, station_information=None, line_information=None, bike_information=None):
        if station_information is None:
            station_information = []
        if line_information is None:
            line_information = []
        self.mobility_index = None
        self.station_information = station_information
        self.line_information = line_information
        self.bike_information = bike_information
        self.travel_distance_information = [TravelDistanceInformation()]
