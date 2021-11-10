import glob
import os
from os import path

import networkx as nx
import osmnx as ox

from tracking_decorator import TrackingDecorator


def get_means_of_transport_graph(logger, results_path, city, transport, enhance_with_speed=False):
    if transport == "all":
        return nx.algorithms.operators.all.compose_all([
            get_means_of_transport_graph(logger=logger, results_path=results_path, city=city, transport="bus",
                                         enhance_with_speed=True),
            get_means_of_transport_graph(logger=logger, results_path=results_path, city=city, transport="subway",
                                         enhance_with_speed=True),
            get_means_of_transport_graph(logger=logger, results_path=results_path, city=city, transport="tram",
                                         enhance_with_speed=True),
            get_means_of_transport_graph(logger=logger, results_path=results_path, city=city, transport="light_rail",
                                         enhance_with_speed=True)
        ])
    else:
        g_transport = None

        try:
            if transport == "walk":
                g_transport = load_graphml_from_file(logger=logger,
                                                     file_path=os.path.join(results_path, transport + ".graphml"),
                                                     city=city,
                                                     network_type=transport, )
            elif transport == "bike":
                g_transport = load_graphml_from_file(logger=logger,
                                                     file_path=os.path.join(results_path, transport + ".graphml"),
                                                     city=city,
                                                     network_type=transport, )
            elif transport == "bus":
                g_transport = load_graphml_from_file(logger=logger,
                                                     file_path=os.path.join(results_path, transport + ".graphml"),
                                                     city=city,
                                                     custom_filter='["highway"~"secondary|tertiary|residential|bus_stop"]')
            elif transport == "light_rail":
                g_transport = load_graphml_from_file(logger=logger,
                                                     file_path=os.path.join(results_path, transport + ".graphml"),
                                                     city=city,
                                                     custom_filter='["railway"~"light_rail|station"]["railway"!="light_rail_entrance"]["railway"!="service_station"]["station"!="subway"]')
            elif transport == "subway":
                g_transport = load_graphml_from_file(logger=logger,
                                                     file_path=os.path.join(results_path, transport + ".graphml"),
                                                     city=city,
                                                     custom_filter='["railway"~"subway|station"]["railway"!="subway_entrance"]["railway"!="service_station"]["station"!="light_rail"]["service"!="yard"]')
            elif transport == "tram":
                g_transport = load_graphml_from_file(logger=logger,
                                                     file_path=os.path.join(results_path, transport + ".graphml"),
                                                     city=city,
                                                     custom_filter='["railway"~"tram|tram_stop"]["railway"!="tram_crossing"]["train"!="yes"]["station"!="subway"]["station"!="light_rail"]')

            if enhance_with_speed:
                return enhance_graph_with_speed(g=g_transport, transport=transport)
            else:
                return g_transport
        except:
            return None


def get_query(city):
    if city == "berlin":
        return "Berlin, Germany"
    else:
        return None


def load_graphml_from_file(logger, file_path, city, network_type=None, custom_filter=None):
    query = get_query(city)

    if not path.exists(file_path):
        logger.log_line("Download " + file_path)
        graph = load_graphml(query=query,
                             network_type=network_type,
                             custom_filter=custom_filter)
        ox.save_graphml(graph, file_path)
        return graph
    else:
        logger.log_line("Load " + file_path)
        return ox.io.load_graphml(file_path)


def load_graphml(query, network_type=None, custom_filter=None):
    return ox.graph.graph_from_place(query=query,
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


#
# Main
#

class GraphLoader:

    @TrackingDecorator.track_time
    def run(self, logger, results_path, city, transport, enhance_with_speed=False, quiet=False, clean=False):

        # Make results path
        os.makedirs(os.path.join(results_path), exist_ok=True)

        # Clean results path
        if clean:
            files = glob.glob(os.path.join(results_path, "*.graphml"))
            for f in files:
                os.remove(f)

        graph = get_means_of_transport_graph(
            logger=logger,
            results_path=results_path,
            city=city,
            transport=transport,
            enhance_with_speed=enhance_with_speed,
        )

        if not quiet:
            logger.log_line("✓️ Load graph for " + str(transport) + " transport in " + city)

        return graph
