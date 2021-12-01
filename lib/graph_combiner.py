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


def load_transport_graph(file_path):
    return ox.load_graphml(file_path)


#
# Main
#

class GraphCombiner:

    @TrackingDecorator.track_time
    def run(self, logger, results_path, graph_transport, graph_walk, stations, clean=False, quiet=False):

        # Make results path
        os.makedirs(os.path.join(results_path), exist_ok=True)

        # Define file path
        file_path = os.path.join(results_path, "all_composed.graphml")

        # Check if result needs to be generated
        if clean or not os.path.exists(file_path):
            graph = nx.algorithms.operators.all.compose_all([graph_transport, graph_walk])

            graph_transport_nodes, graph_transport_edges = ox.graph_to_gdfs(graph_transport)
            graph_transport_node_ids = list(graph_transport_nodes.axes[0])

            # Iterate over all nodes of first graph
            for transport_node_id in tqdm(iterable=graph_transport_node_ids,
                                        desc="Compose graphs",
                                        total=len(graph_transport_node_ids),
                                        unit="node"):

                # Get coordinates of node
                transport_node_point = graph_transport.nodes[transport_node_id]

                # Get node in walk graph that is closest to station node
                walk_node_id, distance = ox.nearest_nodes(
                    G=graph_walk,
                    X=transport_node_point["x"],
                    Y=transport_node_point["y"],
                    return_dist=True
                )

                # Add edges in both directions
                graph.add_edge(
                    transport_node_id,
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
                    transport_node_id,
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
            # Load graph
            graph = load_transport_graph(file_path)

            if not quiet:
                logger.log_line(f"✓ Load {file_path}")

            return graph
