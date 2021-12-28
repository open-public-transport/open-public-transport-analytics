from city_basic_information import CityBasicInformation
from station_information import StationInformation
from travel_distance_information import TravelDistanceInformation


class CityMetrics:
    def __init__(self):
        self.city_basic_information = CityBasicInformation()
        self.station_information = [StationInformation()]
        self.travel_distance_information = [TravelDistanceInformation()]
