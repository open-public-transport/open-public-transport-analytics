import os

from cities import Cities
from city_basic_information import CityBasicInformation
from city_metrics import CityMetrics
from logger_facade import LoggerFacade
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

    absolute_stations_count = RankedValue()
    absolute_stations_count.raw_value = len(overall_station_ids)

    relative_stations_per_sqkm = RankedValue()
    relative_stations_per_sqkm.raw_value = len(overall_station_ids) / area

    relative_stations_per_inhabitant = RankedValue()
    relative_stations_per_inhabitant.raw_value = len(overall_station_ids) / inhabitants

    station_information = StationInformation(public_transport_type="all")
    station_information.absolute_stations_count = absolute_stations_count
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


class CityMetricsBuilder:

    def __init__(self, base_results_path):
        self.logger = LoggerFacade(base_results_path, console=True, file=False)
        self.base_results_path = base_results_path

    def run(self):
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

            results_path = os.path.join(self.base_results_path, city_id)

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

            city_metrics = CityMetrics()
            city_metrics.city_basic_information = city_basic_information
            city_metrics.station_information = [station_information_all]

            city_metrics_list.append(city_metrics)

        return city_metrics_list
