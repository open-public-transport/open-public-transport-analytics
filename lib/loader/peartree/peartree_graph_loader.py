import os

import osmnx as ox
import peartree as pt
from tracking_decorator import TrackingDecorator


def download_transport_graph(logger, data_path, results_path, transport_association, start_time, end_time,
                             existing_graph):
    file_path = os.path.join(results_path, f"transport-{start_time}-{end_time}-osmnx.graphml")

    try:
        gtfs_path = os.path.join(data_path, "transport-associations", transport_association, "GTFS.zip")
        feed = pt.get_representative_feed(gtfs_path)
        graph_transport = pt.load_feed_as_graph(feed, start_time, end_time, existing_graph, use_multiprocessing=True)

        # Save graph
        ox.save_graphml(graph_transport, file_path)
        # nx.write_graphml(graph_transport, os.path.join(results_path, f"transport-{start_time}-{end_time}-nx.graphml"))
        # nx.write_gpickle(graph_transport, os.path.join(results_path, f"transport-{start_time}-{end_time}-nx.gpickle"))
        # nx.write_gml(graph_transport, os.path.join(results_path, f"transport-{start_time}-{end_time}-nx.gml"))
        # nx.write_gexf(graph_transport, os.path.join(results_path, f"transport-{start_time}-{end_time}-nx.gexf"))
        # nx.write_pajek(graph_transport, os.path.join(results_path, f"transport-{start_time}-{end_time}-nx.net"))
        # nx.write_yaml(graph_transport, os.path.join(results_path, f"transport-{start_time}-{end_time}-nx.yaml"))

        return graph_transport
    except Exception as e:
        logger.log_line(f"✗️ Exception: {str(e)}")
        return None


def load_transport_graph(file_path):
    return ox.load_graphml(file_path)


#
# Main
#

class PeartreeGraphLoader:

    @TrackingDecorator.track_time
    def run(self, logger, data_path, results_path, transport_association, start_time, end_time, existing_graph=None, clean=False,
            quiet=False):
        # Make results path
        os.makedirs(os.path.join(results_path), exist_ok=True)

        # Define file path
        file_path = os.path.join(results_path, f"transport-{start_time}-{end_time}-osmnx.graphml")

        # Check if result needs to be generated
        if clean or not os.path.exists(file_path):

            # Download graph
            graph = download_transport_graph(
                logger=logger,
                data_path=data_path,
                results_path=results_path,
                transport_association=transport_association,
                start_time=start_time,
                end_time=end_time,
                existing_graph=existing_graph
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
