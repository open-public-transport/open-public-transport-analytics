import math
import os

from bike_information import BikeInformation
from cities import Cities
from line_information import LineInformation
from overpass_station_loader import OverpassStationLoader
from overpass_route_loader import OverpassRouteLoader
from place_metrics import PlaceMetrics
from ranked_value import RankedValue
from station_information import StationInformation


def get_station_information(results_path, city_name, bounding_box, public_transport_type, lat, lon):
    stations = OverpassStationLoader().run(
        logger=None,
        results_path=os.path.join(results_path, "osm"),
        city_id=city_name,
        bounding_box=bounding_box,
        public_transport_type=public_transport_type,
        clean=False,
        quiet=True
    )

    walking_time_min = 15
    walking_speed_kph = 4.5
    radius_km = walking_time_min / 60 * walking_speed_kph

    station_ids = get_stations_in_radius(lat, lon, radius_km, stations)

    absolute_station_count = RankedValue()
    absolute_station_count.raw_value = len(station_ids)

    station_information = StationInformation(public_transport_type=public_transport_type)
    station_information.absolute_station_count = absolute_station_count

    return station_information

def get_line_information(results_path, city_name, bounding_box, public_transport_type, lat, lon):
    stations = OverpassStationLoader().run(
        logger=None,
        results_path=os.path.join(results_path, "osm"),
        city_id=city_name,
        bounding_box=bounding_box,
        public_transport_type=public_transport_type,
        clean=False,
        quiet=True
    )
    routes = OverpassRouteLoader().run(
        logger=None,
        results_path=os.path.join(results_path, "osm"),
        city_id=city_name,
        bounding_box=bounding_box,
        public_transport_type=public_transport_type,
        clean=False,
        quiet=True
    )

    walking_time_min = 15
    walking_speed_kph = 4.5
    radius_km = walking_time_min / 60 * walking_speed_kph

    station_ids = get_stations_in_radius(lat, lon, radius_km, stations)
    line_ids = get_lines_by_stations(routes, station_ids)

    absolute_line_count = RankedValue()
    absolute_line_count.raw_value = len(line_ids)

    line_information = LineInformation(public_transport_type=public_transport_type)
    line_information.absolute_line_count = absolute_line_count

    return line_information


# See https://en.wikipedia.org/wiki/Haversine_formula
def get_distance(point_a, point_b):
    earth_radius = 6373.0

    lat_a = math.radians(float(point_a[0]))
    lon_a = math.radians(float(point_a[1]))
    lat_b = math.radians(float(point_b[0]))
    lon_b = math.radians(float(point_b[1]))

    distance_lon = lon_b - lon_a
    distance_lat = lat_b - lat_a

    # Apply Haversine formula
    a = math.sin(distance_lat / 2) ** 2 + math.cos(lat_a) * math.cos(lat_b) * math.sin(distance_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return earth_radius * c


def get_stations_in_radius(lat, lon, radius, stations):
    nodes = []
    elements = stations["elements"]
    for element in elements:
        id = element["id"]
        station_lat = element["lat"]
        station_lon = element["lon"]

        start_point = (lat, lon)
        station_point = (station_lat, station_lon)
        distance = get_distance(start_point, station_point)

        if distance < radius:
            nodes.append(id)

    return nodes


def get_lines_by_stations(routes, station_ids):
    lines = []

    if routes is not None:
        elements = routes["elements"]
        for element in elements:
            id = element["id"]
            members = element["members"]

            for member in members:
                role = member["role"]
                ref = member["ref"]
                if role == "stop" and ref in station_ids and id not in lines:
                    lines.append(id)

    return lines

class PlaceMetricsBuilder:

    def __init__(self, results_path):
        self.results_path = results_path

    def run(self, city_id, lat, lon):
        city = Cities().get_city_by_id(city_id.lower())

        city_name = city["name"]
        bounding_box = city["bounding_box"]
        public_transport_types = city["public_transport_types"]

        station_information = []
        line_information = []

        for public_transport_type in public_transport_types:
            transport_station_information = get_station_information(self.results_path, city_name, bounding_box, public_transport_type=public_transport_type, lat=lat, lon=lon)
            transport_line_information = get_line_information(self.results_path, city_name, bounding_box, public_transport_type=public_transport_type, lat=lat, lon=lon)

            if transport_station_information is not None:
                station_information.append(transport_station_information)
            if transport_line_information is not None:
                line_information.append(transport_line_information)

        return PlaceMetrics(
            station_information=station_information,
            line_information=line_information,
            bike_information=BikeInformation()
        )
