import os

from geojson import FeatureCollection
from tracking_decorator import TrackingDecorator


def write_graph_to_geojson(file_path, graph):
    edge_features = get_edge_features(graph)
    node_features = get_node_features(graph)
    collection = FeatureCollection(edge_features + node_features)

    with open(file_path, "w") as f:
        f.write("%s" % collection)


def get_edge_features(graph):
    features = []

    if len(graph.edges) > 0:
        for node_ids in graph.edges:
            node_start = graph.nodes[node_ids[0]]
            node_end = graph.nodes[node_ids[1]]
            feature = {}
            feature["geometry"] = {"type": "LineString", "coordinates": [[node_start["x"], node_start["y"]],
                                                                         [node_end["x"], node_end["y"]]]}
            feature["type"] = "Feature"
            features.append(feature)

    return features


def get_node_features(graph):
    features = []

    if len(graph.nodes) > 0:
        for node_id in graph.nodes:
            node = graph.nodes[node_id]
            feature = {}
            feature["geometry"] = {"type": "Point", "coordinates": [node["x"], node["y"]]}
            feature["type"] = "Feature"
            features.append(feature)

    return features


#
# Main
#

class GraphToGeojsonConverter:

    @TrackingDecorator.track_time
    def run(self, logger, results_path, graph, means_of_transportation, clean=False, quiet=False):

        # Make results path
        os.makedirs(os.path.join(results_path), exist_ok=True)

        # Define file path
        file_path = os.path.join(results_path, f"transport-{means_of_transportation}.geojson")

        # Check if result needs to be generated
        if clean or not os.path.exists(file_path):

            write_graph_to_geojson(file_path, graph)

            if not quiet:
                logger.log_line(f"✓ Convert {means_of_transportation} to GeoJSON")
