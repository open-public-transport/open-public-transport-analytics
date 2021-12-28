import getopt
import os
import sys

file_path = os.path.realpath(__file__)
script_path = os.path.dirname(file_path)

# Make library available in path
library_paths = [
    os.path.join(script_path, "lib"),
    os.path.join(script_path, "lib", "cloud"),
    os.path.join(script_path, "lib", "config"),
    os.path.join(script_path, "lib", "loader", "osmnx"),
    os.path.join(script_path, "lib", "loader", "overpass"),
    os.path.join(script_path, "lib", "loader", "peartree"),
    os.path.join(script_path, "lib", "converter"),
    os.path.join(script_path, "lib", "log"),
]

for p in library_paths:
    if not (p in sys.path):
        sys.path.insert(0, p)

# Import library classes
from tracking_decorator import TrackingDecorator
from point_generator import PointGenerator
from peartree_graph_loader import PeartreeGraphLoader
from overpass_station_loader import OverpassStationLoader
from overpass_line_loader import OverpassLineLoader
from overpass_route_loader import OverpassRouteLoader
from osm_to_geojson_converter import OsmToGeojsonConverter
from osmnx_graph_loader import OsmnxGraphLoader
from graph_transformer import GraphTransformer
from logger_facade import LoggerFacade
from isochrone_builder import IsochroneBuilder
from google_cloud_platform_bucket_uploader import GoogleCloudPlatformBucketUploader
from cities import Cities

#
# Main
#

@TrackingDecorator.track_time
def main(argv):
    # Set default values
    clean = False
    quiet = False
    points_per_sqkm = 100
    start_end_times = [(7 * 60 * 60, 7.25 * 60 * 60)]
    travel_times = [15]

    # Read command line arguments
    try:
        opts, args = getopt.getopt(argv, "hcqp:", ["help", "clean", "quiet", "points_per_sqkm="])
    except getopt.GetoptError:
        print("main.py --help --clean --quiet --points_per_sqkm <points>")
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print("main.py")
            print("--help                           show this help")
            print("--clean                          clean intermediate results before start")
            print("--quiet                          do not log outputs")
            print("--points_per_sqkm                number of sample points to use")
            sys.exit()
        elif opt in ("-c", "--clean"):
            clean = True
        elif opt in ("-q", "--quiet"):
            quiet = True
        elif opt in ("-p", "--points_per_sqkm"):
            points_per_sqkm = int(arg)

    # Set paths
    data_path = os.path.join(script_path, "data", "data")
    base_results_path = os.path.join(script_path, "results", "results")

    # Iterate over cities
    for city in Cities().cities:

        city_name = city["name"]
        query = city["query"]
        area = city["area"]
        inhabitants = city["inhabitants"]
        bounding_box = city["bounding_box"]
        transport_association = city["transport_association"]

        results_path = os.path.join(base_results_path, city_name)

        # Initialize logger
        logger = LoggerFacade(results_path, console=True, file=True)

        # Generate sample points
        sample_points = PointGenerator().run(
            logger=logger,
            data_path=data_path,
            results_path=os.path.join(results_path, "sample-points"),
            city=city_name,
            num_sample_points=area * points_per_sqkm,
            clean=clean,
            quiet=quiet
        )

        for means_of_transportation in ["bus", "subway", "light_rail", "tram"]:
            # Load stations
            OverpassStationLoader().run(
                logger=logger,
                results_path=os.path.join(results_path, "osm"),
                city=city_name,
                bounding_box=bounding_box,
                transport=means_of_transportation,
                clean=clean,
                quiet=quiet
            )

            # Load lines
            OverpassLineLoader().run(
                logger=logger,
                results_path=os.path.join(results_path, "osm"),
                city=city_name,
                bounding_box=bounding_box,
                transport=means_of_transportation,
                clean=clean,
                quiet=quiet
            )

            # Load routes
            OverpassRouteLoader().run(
                logger=logger,
                results_path=os.path.join(results_path, "osm"),
                city=city_name,
                bounding_box=bounding_box,
                transport=means_of_transportation,
                clean=clean,
                quiet=quiet
            )

            OsmToGeojsonConverter().run(
                logger=logger,
                data_path=os.path.join(results_path, "osm"),
                results_path=os.path.join(results_path, "geojson"),
                means_of_transportation=means_of_transportation,
                clean=clean,
                quiet=quiet
            )

        # Load walk graph
        graph_walk = OsmnxGraphLoader().run(
            logger=logger,
            results_path=os.path.join(results_path, "graphs", "osmnx"),
            query=query,
            transport="walk",
            simplify=True,
            enhance_with_speed=True,
            clean=clean,
            quiet=quiet
        )

        # Transform walk graph
        graph_walk = GraphTransformer().run(
            logger=logger,
            results_path=os.path.join(results_path, "graphs", "osmnx"),
            graph=graph_walk,
            clean=clean,
            quiet=quiet
        )

        # Iterate over start/end times
        for times in start_end_times:
            start_time = times[0]
            end_time = times[1]

            # Load transport graph
            graph = PeartreeGraphLoader().run(
                logger=logger,
                data_path=data_path,
                results_path=os.path.join(results_path, "graphs", "peartree"),
                transport_association=transport_association,
                start_time=start_time,
                end_time=end_time,
                existing_graph=graph_walk,
                clean=clean,
                quiet=quiet
            )

            # Iterate over travel times
            for travel_time in travel_times:
                # Build isochrones
                IsochroneBuilder().run(
                    logger=logger,
                    data_path=data_path,
                    results_path=os.path.join(results_path, "geojson"),
                    city=city_name,
                    graph=graph,
                    sample_points=sample_points,
                    travel_time=travel_time,
                    start_time=start_time,
                    end_time=end_time
                )

            # Upload results
            GoogleCloudPlatformBucketUploader().upload_data(
                logger=logger,
                data_path=results_path,
                city=city_name,
                project_id="open-public-transport",
                bucket_name="open-public-transport.appspot.com",
                quiet=quiet
            )


if __name__ == "__main__":
    main(sys.argv[1:])
