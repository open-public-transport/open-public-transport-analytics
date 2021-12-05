import os

import osmnx as ox

from tracking_decorator import TrackingDecorator


def transform_graph(graph):
    for _, _, _, data in graph.edges(data=True, keys=True):
        speed = 4.5
        length = data["length"]

        data["length"] = length / 1_000 / speed * 60 * 60

    for i, node in graph.nodes(data=True):
        graph.node[i]["boarding_cost"] = 0

    return graph


def load_transport_graph(file_path):
    return ox.load_graphml(file_path)


#
# Main
#

class GraphTransformer:

    @TrackingDecorator.track_time
    def run(self, logger, results_path, graph, clean=False,
            quiet=False):
        # Make results path
        os.makedirs(os.path.join(results_path), exist_ok=True)

        # Define file path
        file_path = os.path.join(results_path, "walk-transformed.graphml")

        # Check if result needs to be generated
        if clean or not os.path.exists(file_path):
            transformed_graph = transform_graph(graph)

            # Save graph
            ox.save_graphml(transformed_graph, file_path)

            return transformed_graph
        else:
            # Load graph
            graph = load_transport_graph(file_path)

            if not quiet:
                logger.log_line(f"✓ Load {file_path} with {len(graph.nodes)} nodes and {len(graph.edges)} edges")

            return graph
