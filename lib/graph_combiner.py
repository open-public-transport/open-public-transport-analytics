import os
from os import path

import networkx as nx
import osmnx as ox
from tqdm import tqdm

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


#
# Main
#

class GraphCombiner:

    @TrackingDecorator.track_time
    def run(self, logger, results_path, graph_a, graph_b, connect_a_to_b=False, clean=False):
        """
        Combines two graphs into one

        Parameters
        ----------
        :param graph_a : MultiDiGraph First graph.
        :param graph_b : MultiDiGraph Second graph.
        :param connect_a_to_b : bool If true, each node of first graph will be connected to the closest node of the
        second graph via an edge
        :return composed graph
        """

        # Make results path
        os.makedirs(os.path.join(results_path), exist_ok=True)

        file_path = os.path.join(results_path, "all_composed.graphml")

        if clean or not os.path.exists(file_path):
            graph = nx.algorithms.operators.all.compose_all([graph_a, graph_b])

            if connect_a_to_b:
                a_nodes = ox.graph_to_gdfs(graph_a, edges=False)
                # b_nodes, b_edges = ox.graph_to_gdfs(graph_b)

                # Iterate over all nodes of first graph
                a_node_ids = a_nodes.axes[0]
                for a_node_id in tqdm(iterable=a_node_ids, desc="Compose graphs", total=len(a_node_ids), unit="node"):
                    # Get coordinates of node
                    a_nodes_point = graph_a.nodes[a_node_id]

                    # Get node in second graph that is closest to node in first graph
                    b_node_id, distance = ox.nearest_nodes(
                        G=graph_b,
                        X=a_nodes_point["x"],
                        Y=a_nodes_point["y"],
                        return_dist=True
                    )

                    # Add edges in both directions
                    graph.add_edge(
                        a_node_id,
                        b_node_id,
                        osmid=0,
                        name="Way from station",
                        highway="tertiary",
                        maxspeed="50",
                        oneway=False,
                        length=0,
                        time=0)
                    graph.add_edge(
                        b_node_id,
                        a_node_id,
                        osmid=0,
                        name="Way to station",
                        highway="tertiary",
                        maxspeed="50",
                        oneway=False,
                        length=0,
                        time=0)

            ox.save_graphml(graph, file_path)

            return graph
        else:
            logger.log_line("Load " + file_path)
            ox.load_graphml(file_path)
