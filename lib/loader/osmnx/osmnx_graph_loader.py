import os
from functools import partial
from operator import is_not

import networkx as nx
import osmnx as ox
from tracking_decorator import TrackingDecorator


def download_transport_graph(logger, results_path, city, transport, simplify=False, enhance_with_speed=False):
    graph_transport = None

    if simplify:
        file_path = os.path.join(results_path, transport + "-simplified.graphml")
    else:
        file_path = os.path.join(results_path, transport + "-unsimplified.graphml")

    try:
        if transport == "all":
            graph_transport = download_complete_graph(
                logger=logger,
                city=city,
                simplify=simplify,
                results_path=results_path
            )
        elif transport == "walk":
            graph_transport = download_graph(
                city=city,
                network_type=transport,
                simplify=simplify,
            )
        elif transport == "bike":
            graph_transport = download_graph(
                city=city,
                network_type=transport,
                simplify=simplify,
            )
        elif transport == "bus":
            graph_transport = download_graph(
                city=city,
                custom_filter='["highway"~"secondary|tertiary|residential|bus_stop"]',
                simplify=simplify,
            )
        elif transport == "light_rail":
            graph_transport = download_graph(
                city=city,
                custom_filter='["railway"~"light_rail|station"]["railway"!="light_rail_entrance"]'
                              '["railway"!="service_station"]["station"!="subway"]',
                simplify=simplify,
            )
        elif transport == "subway":
            graph_transport = download_graph(
                city=city,
                custom_filter='["railway"~"subway|station"]["railway"!="subway_entrance"]["railway"!="service_station"]'
                              '["station"!="light_rail"]["service"!="yard"]',
                simplify=simplify,
            )
        elif transport == "tram":
            graph_transport = download_graph(
                city=city,
                custom_filter='["railway"~"tram|tram_stop"]["railway"!="tram_crossing"]["train"!="yes"]'
                              '["station"!="subway"]["station"!="light_rail"]',
                simplify=simplify,
            )

        # Enhance graph with speed
        if enhance_with_speed:
            graph_transport = enhance_graph_with_speed(graph=graph_transport, transport=transport)

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


def download_graph(city, network_type=None, custom_filter=None, simplify=False):
    return ox.graph_from_place(
        query=get_query(city),
        simplify=simplify,
        retain_all=False,
        buffer_dist=2500,
        network_type=network_type,
        custom_filter=custom_filter
    )


def download_complete_graph(logger, city, simplify, results_path):
    return nx.algorithms.operators.all.compose_all(
        list(filter(partial(is_not, None), [
            download_transport_graph(logger=logger, results_path=results_path, city=city, transport="bus",
                                     simplify=simplify, enhance_with_speed=True),
            download_transport_graph(logger=logger, results_path=results_path, city=city, transport="subway",
                                     simplify=simplify, enhance_with_speed=True),
            download_transport_graph(logger=logger, results_path=results_path, city=city, transport="tram",
                                     simplify=simplify, enhance_with_speed=True),
            download_transport_graph(logger=logger, results_path=results_path, city=city, transport="light_rail",
                                     simplify=simplify, enhance_with_speed=True)
        ])))


def enhance_graph_with_speed(graph, time_attribute="time", transport=None):
    for _, _, _, data in graph.edges(data=True, keys=True):

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
            data[time_attribute] = int(data["length"] / (float(speed) * 1000 / 60))

    return graph


def load_transport_graph(file_path):
    return ox.load_graphml(file_path)


import warnings

warnings.filterwarnings("ignore")


#
# Main
#

class OsmnxGraphLoader:

    @TrackingDecorator.track_time
    def run(self, logger, results_path, city, transport, simplify=False, enhance_with_speed=False, clean=False,
            quiet=False):
        # Make results path
        os.makedirs(os.path.join(results_path), exist_ok=True)

        # Define file path
        if simplify:
            file_path = os.path.join(results_path, transport + "-simplified.graphml")
        else:
            file_path = os.path.join(results_path, transport + "-unsimplified.graphml")

        # Check if result needs to be generated
        if clean or not os.path.exists(file_path):

            # Download graph
            graph = download_transport_graph(
                logger=logger,
                results_path=results_path,
                city=city,
                transport=transport,
                simplify=simplify,
                enhance_with_speed=enhance_with_speed,
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
