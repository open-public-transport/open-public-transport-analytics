import os
from functools import partial
from operator import is_not
from os import path

import networkx as nx
import osmnx as ox

from tracking_decorator import TrackingDecorator


def get_means_of_transport_graph(logger, results_path, city, transport, clean=False, quiet=False):
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
        elif transport == "bus":
            graph_transport = load_graphml_from_file(
                logger=logger,
                file_path=os.path.join(results_path, transport + ".graphml"),
                city=city,
                custom_filter='["highway"~"bus_stop"]',
                clean=clean,
                quiet=quiet
            )
        elif transport == "light_rail":
            graph_transport = load_graphml_from_file(
                logger=logger,
                file_path=os.path.join(results_path, transport + ".graphml"),
                city=city,
                custom_filter='["railway"~"station|halt"]["station"~"light_rail"]',
                clean=clean,
                quiet=quiet
            )
        elif transport == "subway":
            graph_transport = load_graphml_from_file(
                logger=logger,
                file_path=os.path.join(results_path, transport + ".graphml"),
                city=city,
                custom_filter='["railway"~"station|halt"]["station"~"subway"]',
                clean=clean,
                quiet=quiet
            )
        elif transport == "tram":
            graph_transport = load_graphml_from_file(
                logger=logger,
                file_path=os.path.join(results_path, transport + ".graphml"),
                city=city,
                custom_filter='["railway"~"tram_stop"]',
                clean=clean,
                quiet=quiet
            )

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
                                             clean=clean, quiet=quiet),
                get_means_of_transport_graph(logger=logger, results_path=results_path, city=city, transport="subway",
                                             clean=clean, quiet=quiet),
                get_means_of_transport_graph(logger=logger, results_path=results_path, city=city, transport="tram",
                                             clean=clean, quiet=quiet),
                get_means_of_transport_graph(logger=logger, results_path=results_path, city=city,
                                             transport="light_rail", clean=clean, quiet=quiet)
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


import warnings

warnings.filterwarnings("ignore")


#
# Main
#

class StationLoader:

    @TrackingDecorator.track_time
    def run(self, logger, results_path, city, transport, clean=False, quiet=False):
        # Make results path
        os.makedirs(os.path.join(results_path), exist_ok=True)

        # Load graph
        graph = get_means_of_transport_graph(
            logger=logger,
            results_path=results_path,
            city=city,
            transport=transport,
            clean=clean,
            quiet=quiet
        )

        if not quiet:
            logger.log_line("✓️ Load stations for " + str(transport) + " transport in " + city)

        return graph
