import json
import os

from cities import Cities
from city_basic_information import CityBasicInformation
from city_metrics import CityMetrics
from line_information import LineInformation
from logger_facade import LoggerFacade
from overpass_route_loader import OverpassRouteLoader
from overpass_station_loader import OverpassStationLoader
from ranked_value import RankedValue
from station_information import StationInformation


def get_station_information(logger, results_path, city_id, area, inhabitants, bounding_box, public_transport_types):
    overall_station_ids = []

    for public_transport_type in public_transport_types:
        stations = OverpassStationLoader().run(
            logger=logger,
            results_path=os.path.join(results_path, "osm"),
            city_id=city_id,
            bounding_box=bounding_box,
            public_transport_type=public_transport_type,
            clean=False,
            quiet=False
        )

        if stations is not None:
            station_ids = get_station_ids(stations)

            overall_station_ids += station_ids

    absolute_station_count = RankedValue()
    absolute_station_count.raw_value = len(overall_station_ids)

    relative_stations_per_sqkm = RankedValue()
    relative_stations_per_sqkm.raw_value = len(overall_station_ids) / area

    relative_stations_per_inhabitant = RankedValue()
    relative_stations_per_inhabitant.raw_value = len(overall_station_ids) / inhabitants

    station_information = StationInformation(public_transport_type="all")
    station_information.absolute_station_count = absolute_station_count
    station_information.relative_stations_per_sqkm = relative_stations_per_sqkm
    station_information.relative_stations_per_inhabitant = relative_stations_per_inhabitant

    return station_information


def get_station_ids(stations):
    nodes = []
    elements = stations["elements"]
    for element in elements:
        id = element["id"]
        nodes.append(id)

    return nodes


def get_line_information(logger, results_path, city_id, area, inhabitants, bounding_box, public_transport_types):
    overall_line_ids = []

    for public_transport_type in public_transport_types:
        lines = OverpassRouteLoader().run(
            logger=logger,
            results_path=os.path.join(results_path, "osm"),
            city_id=city_id,
            bounding_box=bounding_box,
            public_transport_type=public_transport_type,
            clean=False,
            quiet=False
        )

        if lines is not None:
            line_ids = get_line_ids(lines)

            overall_line_ids += line_ids

    absolute_lines_count = RankedValue()
    absolute_lines_count.raw_value = len(overall_line_ids)

    relative_lines_per_sqkm = RankedValue()
    relative_lines_per_sqkm.raw_value = len(overall_line_ids) / area

    relative_lines_per_inhabitant = RankedValue()
    relative_lines_per_inhabitant.raw_value = len(overall_line_ids) / inhabitants

    line_information = LineInformation(public_transport_type="all")
    line_information.absolute_line_count = absolute_lines_count
    line_information.relative_line_per_sqkm = relative_lines_per_sqkm
    line_information.relative_line_per_inhabitant = relative_lines_per_inhabitant

    return line_information


def get_line_ids(lines):
    ways = []
    elements = lines["elements"]
    for element in elements:
        id = element["id"]
        ways.append(id)

    return ways


def load_json(file_path):
    with open(file_path, "r") as f:
        text = f.read()

    return json.loads(text.replace("'", ""))


class CityMetricsBuilder:

    def __init__(self, results_path):
        self.logger = LoggerFacade(results_path, console=True, file=False)
        self.results_path = results_path

    def run(self, clean=False):

        # Make results path
        os.makedirs(os.path.join(self.results_path), exist_ok=True)

        # Define file path
        file_path = os.path.join(self.results_path, "cities.json")

        # Check if result needs to be generated
        if clean or not os.path.exists(file_path):

            cities = Cities().cities

            city_metrics_list = []

            # Iterate over cities
            for city in cities:
                city_id = city["id"]
                city_name = city["name"]
                federal_state_name = city["federal_state"]
                query = city["query"]
                area = city["area"]
                inhabitants = city["inhabitants"]
                bounding_box = city["bounding_box"]
                transport_association = city["transport_association"]
                public_transport_types = city["public_transport_types"]

                results_path = os.path.join(self.results_path, city_id)

                city_basic_information = CityBasicInformation()
                city_basic_information.id = city_id
                city_basic_information.city_name = city_name
                city_basic_information.federal_state_name = federal_state_name
                city_basic_information.group = ""
                city_basic_information.inhabitants = inhabitants
                city_basic_information.area = area
                city_basic_information.population_density = inhabitants / area

                station_information_all = get_station_information(
                    logger=self.logger,
                    results_path=results_path,
                    city_id=city_id,
                    area=area,
                    inhabitants=inhabitants,
                    bounding_box=bounding_box,
                    public_transport_types=public_transport_types
                )

                line_information_all = get_line_information(
                    logger=self.logger,
                    results_path=results_path,
                    city_id=city_id,
                    area=area,
                    inhabitants=inhabitants,
                    bounding_box=bounding_box,
                    public_transport_types=public_transport_types
                )

                city_metrics = CityMetrics()
                city_metrics.city_basic_information = city_basic_information
                city_metrics.station_information = [station_information_all]
                city_metrics.line_information = [line_information_all]

                city_metrics_list.append(city_metrics)

            # Save result
            with open(file_path, "w") as f:
                json_content = json.dumps(city_metrics_list, default=lambda x: x.__dict__)
                f.write("%s" % json_content)

            return city_metrics_list
        else:
            # Load graph
            return load_json(file_path=file_path)
