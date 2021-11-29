import os

import networkx as nx
import osmnx as ox
from tqdm import tqdm

from tracking_decorator import TrackingDecorator


def get_station_node_ids(stations):
    station_ids = []

    for station in stations:
        if "id" in station:
            station_ids.append(station["id"])

    return station_ids


#
# Main
#

class GraphCombiner:

    @TrackingDecorator.track_time
    def run(self, logger, results_path, graph_transport, graph_walk, stations, clean=False, quiet=False):

        # Make results path
        os.makedirs(os.path.join(results_path), exist_ok=True)

        file_path = os.path.join(results_path, "all_composed.graphml")

        if clean or not os.path.exists(file_path):
            graph = nx.algorithms.operators.all.compose_all([graph_transport, graph_walk])

            station_node_ids = get_station_node_ids(stations)

            nodes_not_in_transport_graph = 0
            nodes_with_zero_distance_to_walk_graph = 0

            # Iterate over all nodes of first graph
            for station_node_id in tqdm(iterable=station_node_ids, desc="Compose graphs", total=len(station_node_ids),
                                        unit="node"):

                if station_node_id in graph_transport.nodes:

                    # Get coordinates of node
                    station_node_point = graph_transport.nodes[station_node_id]

                    # Get node in second graph that is closest to node in first graph
                    walk_node_id, distance = ox.nearest_nodes(
                        G=graph_walk,
                        X=station_node_point["x"],
                        Y=station_node_point["y"],
                        return_dist=True
                    )

                    if distance == 0.0:
                        logger.log_line(
                            f"✗️ distance between station node {str(station_node_id)} and walk node {str(walk_node_id)} is 0.0")
                        nodes_with_zero_distance_to_walk_graph += 1

                    # Add edges in both directions
                    graph.add_edge(
                        station_node_id,
                        walk_node_id,
                        osmid=0,
                        name="Way from station",
                        highway="tertiary",
                        maxspeed="50",
                        oneway=False,
                        length=0,
                        time=0)
                    graph.add_edge(
                        walk_node_id,
                        station_node_id,
                        osmid=0,
                        name="Way to station",
                        highway="tertiary",
                        maxspeed="50",
                        oneway=False,
                        length=0,
                        time=0)

                else:
                    logger.log_line(f"✗️ station node {str(station_node_id)} not part of transport graph")
                    nodes_not_in_transport_graph += 1

            ox.save_graphml(graph, file_path)

            nodes_not_in_transport_graph_percentage = round(nodes_not_in_transport_graph / len(station_node_ids),
                                                            2) * 100
            nodes_with_zero_distance_to_walk_graph_percentage = round(
                nodes_with_zero_distance_to_walk_graph / len(station_node_ids), 2) * 100

            logger.log_line(
                f"✗️ warning {str(nodes_not_in_transport_graph_percentage)}% of station nodes not in transport graph")
            logger.log_line(
                f"✗️ warning {str(nodes_with_zero_distance_to_walk_graph_percentage)}% of station nodes with 0m distance to walk graph")

            return graph
        else:
            if not quiet:
                logger.log_line("Load " + file_path)
            ox.load_graphml(file_path)
