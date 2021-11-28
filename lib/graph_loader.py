import os
from functools import partial
from operator import is_not
from os import path

import networkx as nx
import osmnx as ox

from tracking_decorator import TrackingDecorator


def get_means_of_transport_graph(logger, results_path, city, transport, enhance_with_speed=False, clean=False,
                                 quiet=False):
    graph_transport = None

    try:
        if transport == "all":
            graph_transport = load_complete_graphml_from_file(
                logger=logger,
                file_path=os.path.join(results_path, transport + ".graphml"),
                city=city,
                results_path=results_path,
                clean=clean,
                quiet=quiet
            )
        elif transport == "walk":
            graph_transport = load_graphml_from_file(
                logger=logger,
                file_path=os.path.join(results_path, transport + ".graphml"),
                city=city,
                network_type=transport,
                clean=clean,
                quiet=quiet
            )
        elif transport == "bike":
            graph_transport = load_graphml_from_file(
                logger=logger,
                file_path=os.path.join(results_path, transport + ".graphml"),
                city=city,
                network_type=transport,
                clean=clean,
                quiet=quiet
            )
        elif transport == "bus":
            graph_transport = load_graphml_from_file(
                logger=logger,
                file_path=os.path.join(results_path, transport + ".graphml"),
                city=city,
                custom_filter='["highway"~"secondary|tertiary|residential|bus_stop"]',
                clean=clean,
                quiet=quiet
            )
        elif transport == "light_rail":
            graph_transport = load_graphml_from_file(
                logger=logger,
                file_path=os.path.join(results_path, transport + ".graphml"),
                city=city,
                custom_filter='["railway"~"light_rail|station"]["railway"!="light_rail_entrance"]'
                              '["railway"!="service_station"]["station"!="subway"]',
                clean=clean,
                quiet=quiet
            )
        elif transport == "subway":
            graph_transport = load_graphml_from_file(
                logger=logger,
                file_path=os.path.join(results_path, transport + ".graphml"),
                city=city,
                custom_filter='["railway"~"subway|station"]["railway"!="subway_entrance"]["railway"!="service_station"]'
                              '["station"!="light_rail"]["service"!="yard"]',
                clean=clean,
                quiet=quiet
            )
        elif transport == "tram":
            graph_transport = load_graphml_from_file(
                logger=logger,
                file_path=os.path.join(results_path, transport + ".graphml"),
                city=city,
                custom_filter='["railway"~"tram|tram_stop"]["railway"!="tram_crossing"]["train"!="yes"]'
                              '["station"!="subway"]["station"!="light_rail"]',
                clean=clean,
                quiet=quiet
            )

        if enhance_with_speed:
            return enhance_graph_with_speed(g=graph_transport, transport=transport)
        else:
            return graph_transport
    except:
        return None


def get_query(city):
    if city == "berlin":
        return "Berlin, Germany"
    elif city == "hamburg":
        return "Hamburg, Germany"
    else:
        return None


def load_graphml_from_file(logger, file_path, city, network_type=None, custom_filter=None, clean=False, quiet=False):
    query = get_query(city)

    if clean or not path.exists(file_path):
        if not quiet:
            logger.log_line("Download " + file_path)
        graph = load_graphml(query=query,
                             network_type=network_type,
                             custom_filter=custom_filter)
        ox.save_graphml(graph, file_path)
        return graph
    else:
        if not quiet:
            logger.log_line("Load " + file_path)
        return ox.load_graphml(file_path)


def load_complete_graphml_from_file(logger, file_path, city, results_path, clean=False, quiet=False):
    if clean or not path.exists(file_path):
        graph = nx.algorithms.operators.all.compose_all(
            list(filter(partial(is_not, None), [
                get_means_of_transport_graph(logger=logger, results_path=results_path, city=city, transport="bus",
                                             enhance_with_speed=True, clean=clean, quiet=quiet),
                get_means_of_transport_graph(logger=logger, results_path=results_path, city=city, transport="subway",
                                             enhance_with_speed=True, clean=clean, quiet=quiet),
                get_means_of_transport_graph(logger=logger, results_path=results_path, city=city, transport="tram",
                                             enhance_with_speed=True, clean=clean, quiet=quiet),
                get_means_of_transport_graph(logger=logger, results_path=results_path, city=city,
                                             transport="light_rail", enhance_with_speed=True, clean=clean, quiet=quiet)
            ])))

        ox.save_graphml(graph, file_path)
        return graph
    else:
        if not quiet:
            logger.log_line("Load " + file_path)
        return ox.load_graphml(file_path)


def load_graphml(query, network_type=None, custom_filter=None):
    return ox.graph_from_place(query=query,
                               simplify=True,
                               retain_all=False,
                               buffer_dist=2500,
                               network_type=network_type,
                               custom_filter=custom_filter)


def enhance_graph_with_speed(g, time_attribute="time", transport=None):
    for _, _, _, data in g.edges(data=True, keys=True):

        speed = None

        if transport == "walk":
            speed = 6.0
        elif transport == "bus":
            speed = 19.5
        elif transport == "bike":
            speed = 16.0
        elif transport == "subway":
            speed = 31.0
        elif transport == "tram":
            speed = 19.0
        elif transport == "light_rail":
            speed = 38.0

        if speed is not None:
            data[time_attribute] = data["length"] / (float(speed) * 1000 / 60)

    return g

import warnings
warnings.filterwarnings("ignore")

#
# Main
#

class GraphLoader:

    @TrackingDecorator.track_time
    def run(self, logger, results_path, city, transport, enhance_with_speed=False, clean=False, quiet=False):
        # Make results path
        os.makedirs(os.path.join(results_path), exist_ok=True)

        # Load graph
        graph = get_means_of_transport_graph(
            logger=logger,
            results_path=results_path,
            city=city,
            transport=transport,
            enhance_with_speed=enhance_with_speed,
            clean=clean,
            quiet=quiet
        )

        if not quiet:
            logger.log_line("✓️ Load graph for " + str(transport) + " transport in " + city)

        return graph
