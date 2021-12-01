import os
from functools import partial
from operator import is_not

import networkx as nx
import osmnx as ox
from tracking_decorator import TrackingDecorator


def download_transport_graph(logger, results_path, city, transport):
    graph_transport = None
    file_path = os.path.join(results_path, transport + ".graphml")

    try:
        if transport == "all":
            graph_transport = download_graph(
                city=city,
            )
        elif transport == "bus":
            graph_transport = download_graph(
                city=city,
                custom_filter='["highway"~"bus_stop"]',
            )
        elif transport == "light_rail":
            graph_transport = download_graph(
                city=city,
                custom_filter='["railway"~"station|halt"]["station"~"light_rail"]',
            )
        elif transport == "subway":
            graph_transport = download_graph(
                city=city,
                custom_filter='["railway"~"station|halt"]["station"~"subway"]',
            )
        elif transport == "tram":
            graph_transport = download_graph(
                city=city,
                custom_filter='["railway"~"tram_stop"]',
            )

        # Save graph
        ox.save_graphml(graph_transport, file_path)

        return graph_transport
    except Exception as e:
        logger.log_line(f"✗️ Exception: {str(e)}")
        return None


def get_query(city):
    if city == "berlin":
        return "Berlin, Germany"
    elif city == "hamburg":
        return "Hamburg, Germany"
    else:
        return None


def download_graph(city, network_type=None, custom_filter=None):
    return ox.graph_from_place(
        query=get_query(city),
        simplify=False,
        retain_all=True,
        buffer_dist=2500,
        network_type=network_type,
        custom_filter=custom_filter
    )


def download_complete_graph(logger, city, results_path):
    return nx.algorithms.operators.all.compose_all(
        list(filter(partial(is_not, None), [
            download_transport_graph(logger=logger, results_path=results_path, city=city, transport="bus"),
            download_transport_graph(logger=logger, results_path=results_path, city=city, transport="subway"),
            download_transport_graph(logger=logger, results_path=results_path, city=city, transport="tram"),
            download_transport_graph(logger=logger, results_path=results_path, city=city, transport="light_rail")
        ])))


def load_transport_graph(file_path):
    return ox.load_graphml(file_path)


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

        # Define file path
        file_path = os.path.join(results_path, transport + ".graphml")

        # Check if result needs to be generated
        if clean or not os.path.exists(file_path):

            # Download graph
            graph = download_transport_graph(
                logger=logger,
                results_path=results_path,
                city=city,
                transport=transport
            )

            if not quiet:
                logger.log_line(f"✓ Download {file_path} with {len(graph.nodes)} nodes and {len(graph.edges)} edges")

            return graph
        else:
            # Load graph
            graph = load_transport_graph(file_path)

            if not quiet:
                logger.log_line(f"✓ Load {file_path} with {len(graph.nodes)} nodes and {len(graph.edges)} edges")

            return graph
