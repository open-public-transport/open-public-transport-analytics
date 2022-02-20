import math
import os

from bike_information import BikeInformation
from cities import Cities
from line_information import LineInformation
from overpass_loader import OverpassLoader
from place_metrics import PlaceMetrics
from ranked_value import RankedValue
from station_information import StationInformation


def get_station_information(results_path, city_name, bounding_box, public_transport_type, lat, lon):
    walking_time_min = 15
    walking_speed_kph = 4.5
    radius_km = walking_time_min / 60 * walking_speed_kph

    # List of IDs of what we consider a station (may be a stop area containing multiple stations)
    station_ids = []

    overpass_loader = OverpassLoader(
        logger=None,
        results_path=os.path.join(results_path, "osm"),
        city_id=city_name,
        bounding_box=bounding_box,
        clean=False,
        quiet=True
    )

    if public_transport_type == "bus":
        bus_stops = overpass_loader.run(result_file_name="nodes_bus_stop.json", query='node["highway"="bus_stop"]')
        bus_platforms = overpass_loader.run(
            result_file_name="ways_bus_platform.json",
            query='way["public_transport"="platform"]["bus"="yes"]'
        )
        bus_stop_areas = overpass_loader.run(
            result_file_name="relations_bus_stop_area.json",
            query='relation["type"="public_transport"]["public_transport"="stop_area"]'
        )

        bus_stop_ids = get_nodes_in_radius(lat, lon, radius_km, bus_stops)
        bus_platform_ids = get_way_ids_by_node_ids(bus_platforms, bus_stop_ids)
        bus_stop_area_ids = get_relation_ids_by_way_ids(bus_stop_areas, bus_platform_ids)
        station_ids = bus_stop_area_ids
    elif public_transport_type == "light_rail":
        light_rail_stations = overpass_loader.run(
            result_file_name="nodes_light_rail_station.json",
            query='node["railway"~"station|halt"]["public_transport"="station"]["light_rail"="yes"]'
        )
        light_rail_stop_areas = overpass_loader.run(
            result_file_name="relations_light_rail_stop_area.json",
            query='relation["type"="public_transport"]["public_transport"="stop_area"]'
        )
        light_rail_stop_area_groups = overpass_loader.run(
            result_file_name="relations_light_rail_stop_area_group.json",
            query='relation["type"="public_transport"]["public_transport"="stop_area_group"]'
        )

        light_rail_station_ids = get_nodes_in_radius(lat, lon, radius_km, light_rail_stations)
        light_rail_stop_area_ids = get_relation_ids_by_node_ids(light_rail_stop_areas, light_rail_station_ids)
        light_rail_stop_area_group_ids = get_relation_ids_by_relation_ids(light_rail_stop_area_groups, light_rail_stop_area_ids)
        station_ids = light_rail_stop_area_group_ids
    elif public_transport_type == "tram":
        tram_stops = overpass_loader.run(
            result_file_name="nodes_tram_stop.json",
            query='node["railway"="tram_stop"]["public_transport"="stop_position"]["tram"="yes"]'
        )
        tram_stop_areas = overpass_loader.run(
            result_file_name="relations_tram_stop.json",
            query='relation["type"="public_transport"]["public_transport"="stop_area"]'
        )
        tram_stop_area_groups = overpass_loader.run(
            result_file_name="relations_tram_stop_area_group.json",
            query='relation["type"="public_transport"]["public_transport"="stop_area_group"]'
        )

        tram_stop_ids = get_nodes_in_radius(lat, lon, radius_km, tram_stops)
        tram_stop_area_ids = get_relation_ids_by_node_ids(tram_stop_areas, tram_stop_ids)
        tram_stop_area_group_ids = get_relation_ids_by_relation_ids(tram_stop_area_groups, tram_stop_area_ids)
        station_ids = tram_stop_area_group_ids
    elif public_transport_type == "subway":
        subway_stations = overpass_loader.run(
            result_file_name="nodes_subway_station.json",
            query='node["railway"~"station|halt"]["public_transport"="station"]["subway"="yes"]'
        )
        subway_stop_areas = overpass_loader.run(
            result_file_name="relations_subway_stop_area.json",
            query='relation["type"="public_transport"]["public_transport"="stop_area"]'
        )
        subway_stop_area_groups = overpass_loader.run(
            result_file_name="relations_subway_stop_area_group.json",
            query='relation["type"="public_transport"]["public_transport"="stop_area_group"]'
        )
    
        subway_station_ids = get_nodes_in_radius(lat, lon, radius_km, subway_stations)
        subway_stop_area_ids = get_relation_ids_by_node_ids(subway_stop_areas, subway_station_ids)
        subway_stop_area_group_ids = get_relation_ids_by_relation_ids(subway_stop_area_groups,
                                                                          subway_stop_area_ids)
        station_ids = subway_stop_area_group_ids

    absolute_station_count = RankedValue()
    absolute_station_count.raw_value = len(station_ids)

    station_information = StationInformation(public_transport_type=public_transport_type)
    station_information.absolute_station_count = absolute_station_count

    return station_information


def get_line_information(results_path, city_name, bounding_box, public_transport_type, lat, lon):
    walking_time_min = 15
    walking_speed_kph = 4.5
    radius_km = walking_time_min / 60 * walking_speed_kph

    # List of IDs of what we consider a line
    line_ids = []

    overpass_loader = OverpassLoader(
        logger=None,
        results_path=os.path.join(results_path, "osm"),
        city_id=city_name,
        bounding_box=bounding_box,
        clean=False,
        quiet=True
    )

    if public_transport_type == "bus":
        # FIXME
        #
        # # Limited bounding box around target
        # limited_bounding_box = [float(lon) - 0.025, float(lat) - 0.025, float(lon) + 0.025, float(lat) + 0.025]
        #
        # bus_stops = overpass_loader.run(result_file_name="nodes_bus_stop.json", query='node["highway"="bus_stop"]')
        # bus_platforms = overpass_loader.run(result_file_name="ways_bus_platform.json",
        #                                     query='way["public_transport"="platform"]["bus"="yes"]')
        # bus_routes = overpass_loader.run(result_file_name="relations_bus_route.json",
        #                                  query='relation["type"="route"]["route"="bus"]',
        #                                  bounding_box=limited_bounding_box,
        #                                  clean=True)
        #
        # bus_stop_ids = get_nodes_in_radius(lat, lon, radius_km, bus_stops)
        # bus_platform_ids = get_way_ids_by_node_ids(bus_platforms, bus_stop_ids)
        # bus_route_ids = get_relation_ids_by_node_ids(bus_routes, bus_platform_ids)
        # line_ids = bus_route_ids
        line_ids = []
    elif public_transport_type == "light_rail":
        light_rail_stations = overpass_loader.run(
            result_file_name="nodes_light_rail_station.json",
            query='node["railway"~"station|halt"]["public_transport"="station"]["light_rail"="yes"]'
        )
        light_rail_stop_areas = overpass_loader.run(
            result_file_name="relations_light_rail_stop_area.json",
            query='relation["type"="public_transport"]["public_transport"="stop_area"]'
        )
        light_rail_platforms = overpass_loader.run(
            result_file_name="ways_light_rail_platform.json",
            query='way["railway"="platform"]["public_transport"="platform"]["light_rail"="yes"]'
        )
        light_rail_routes = overpass_loader.run(
            result_file_name="relations_light_rail_route.json",
            query='relation["line"="light_rail"]["route"="train"]'
        )

        light_rail_station_ids = get_nodes_in_radius(lat, lon, radius_km, light_rail_stations)
        light_rail_stop_area_ids = get_relation_ids_by_node_ids(light_rail_stop_areas, light_rail_station_ids)
        light_rail_platform_ids = get_platform_ids_by_relation_ids(light_rail_stop_areas, light_rail_stop_area_ids)
        light_rail_route_refs = get_relation_refs_by_relation_ids(light_rail_routes, light_rail_platform_ids)
        line_ids = light_rail_route_refs
    elif public_transport_type == "tram":
        tram_stops = overpass_loader.run(
            result_file_name="nodes_tram_stop.json",
            query='node["railway"="tram_stop"]["public_transport"="stop_position"]["tram"="yes"]'
        )
        tram_routes = overpass_loader.run(
            result_file_name="relations_tram_route.json", query='relation["route"="tram"]'
        )

        tram_stop_ids = get_nodes_in_radius(lat, lon, radius_km, tram_stops)
        tram_route_ids = get_relation_refs_by_node_ids(tram_routes, tram_stop_ids)
        line_ids = tram_route_ids
    elif public_transport_type == "subway":
        subway_stations = overpass_loader.run(
            result_file_name="nodes_subway_station.json",
            query='node["railway"~"station|halt"]["public_transport"="station"]["subway"="yes"]'
        )
        subway_stop_areas = overpass_loader.run(
            result_file_name="relations_subway_stop_area.json",
            query='relation["type"="public_transport"]["public_transport"="stop_area"]'
        )
        subway_platforms = overpass_loader.run(
            result_file_name="ways_subway_platform.json",
            query='way["railway"="platform"]["public_transport"="platform"]["subway"="yes"]'
        )
        subway_routes = overpass_loader.run(
            result_file_name="relations_subway_route.json",
            query='relation["route"="subway"]'
        )

        subway_station_ids = get_nodes_in_radius(lat, lon, radius_km, subway_stations)
        subway_stop_area_ids = get_relation_ids_by_node_ids(subway_stop_areas, subway_station_ids)
        subway_platform_ids = get_platform_ids_by_relation_ids(subway_stop_areas, subway_stop_area_ids)
        subway_route_refs = get_relation_refs_by_way_ids(subway_routes, subway_platform_ids)
        line_ids = subway_route_refs

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


def get_nodes_in_radius(lat, lon, radius, stations):
    nodes = []
    elements = stations["elements"]
    for element in elements:
        element_id = element["id"]
        station_lat = element["lat"]
        station_lon = element["lon"]

        start_point = (lat, lon)
        station_point = (station_lat, station_lon)
        distance = get_distance(start_point, station_point)

        if distance < radius:
            nodes.append(element_id)

    return nodes


def get_way_ids_by_node_ids(ways, node_ids):
    results = []

    if ways is not None:
        elements = ways["elements"]
        for element in elements:
            element_id = element["id"]
            members = element["nodes"]

            for member in members:
                if member in node_ids and element_id not in results:
                    results.append(element_id)

    return results


def get_relation_ids_by_relation_ids(relations, relation_ids, element_name="id"):
    results = []

    if relations is not None:
        elements = relations["elements"]
        for element in elements:
            element_id = element[element_name]
            members = element["members"]

            for member in members:
                member_type = member["type"]
                ref = member["ref"]
                if member_type == "relation" and ref in relation_ids and element_id not in results:
                    results.append(element_id)

    return results

def get_platform_ids_by_relation_ids(relations, relation_ids, element_name="id"):
    results = []

    if relations is not None:
        elements = relations["elements"]
        for element in elements:
            element_id = element[element_name]
            members = element["members"]

            if element_id in relation_ids:
                for member in members:
                    ref = member["ref"]
                    member_role = member["role"]
                    if member_role == "platform" and ref not in results:
                        results.append(ref)

    return results

def get_relation_ids_by_way_ids(relations, way_ids, element_name="id"):
    results = []

    if relations is not None:
        elements = relations["elements"]
        for element in elements:
            element_id = element[element_name]
            members = element["members"]

            for member in members:
                member_type = member["type"]
                ref = member["ref"]
                if member_type == "way" and ref in way_ids and element_id not in results:
                    results.append(element_id)

    return results

def get_relation_ids_by_node_ids(relations, node_ids, element_name="id"):
    results = []

    if relations is not None:
        elements = relations["elements"]
        for element in elements:
            element_id = element[element_name]
            members = element["members"]

            for member in members:
                member_type = member["type"]
                ref = member["ref"]
                if member_type == "node" and ref in node_ids and element_id not in results:
                    results.append(element_id)

    return results


def get_relation_refs_by_node_ids(relations, node_ids):
    results = []

    if relations is not None:
        elements = relations["elements"]
        for element in elements:
            element_ref = element["tags"]["ref"]
            members = element["members"]

            for member in members:
                member_type = member["type"]
                ref = member["ref"]
                if member_type == "node" and ref in node_ids and element_ref not in results:
                    results.append(element_ref)

    return results

def get_relation_refs_by_relation_ids(relations, relation_ids):
    results = []

    if relations is not None:
        elements = relations["elements"]
        for element in elements:
            element_ref = element["tags"]["ref"]
            members = element["members"]

            for member in members:
                member_type = member["type"]
                ref = member["ref"]
                if member_type == "relation" and ref in relation_ids and element_ref not in results:
                    results.append(element_ref)

    return results

def get_relation_refs_by_way_ids(relations, way_ids):
    results = []

    if relations is not None:
        elements = relations["elements"]
        for element in elements:
            element_ref = element["tags"]["ref"]
            members = element["members"]

            for member in members:
                member_type = member["type"]
                ref = member["ref"]
                if member_type == "way" and ref in way_ids and element_ref not in results:
                    results.append(element_ref)

    return results


def get_lines_by_stations(routes, station_ids):
    lines = []

    if routes is not None:
        elements = routes["elements"]
        for element in elements:
            element_id = element["id"]
            members = element["members"]

            for member in members:
                role = member["role"]
                ref = member["ref"]
                if role == "stop" and ref in station_ids and element_id not in lines:
                    lines.append(element_id)

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
            transport_station_information = get_station_information(
                self.results_path, city_name, bounding_box, public_transport_type=public_transport_type, lat=lat,
                lon=lon
            )
            transport_line_information = get_line_information(
                self.results_path, city_name, bounding_box, public_transport_type=public_transport_type, lat=lat,
                lon=lon
            )

            if transport_station_information is not None:
                station_information.append(transport_station_information)
            if transport_line_information is not None:
                line_information.append(transport_line_information)

        return PlaceMetrics(
            station_information=station_information,
            line_information=line_information,
            bike_information=BikeInformation()
        )
