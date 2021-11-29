import getopt
import os
import sys

# Make library available in path
library_paths = [
    os.path.join(os.getcwd(), "lib"),
    os.path.join(os.getcwd(), "lib", "loader", "osmnx"),
    os.path.join(os.getcwd(), "lib", "loader", "overpass"),
    os.path.join(os.getcwd(), "lib", "log"),
]

for p in library_paths:
    if not (p in sys.path):
        sys.path.insert(0, p)

# Import library classes
from tracking_decorator import TrackingDecorator
from point_generator import PointGenerator
from graph_loader import GraphLoader
from station_loader_overpass import StationLoaderOverpass
from graph_combiner import GraphCombiner
from logger_facade import LoggerFacade
from isochrone_builder import IsochroneBuilder


#
# Main
#

@TrackingDecorator.track_time
def main(argv):
    # Set default values
    clean = False
    quiet = False
    num_sample_points = 10_000
    cities = ["berlin", "hamburg"]
    travel_times = [15]

    # Read command line arguments
    try:
        opts, args = getopt.getopt(argv, "hcqp:", ["help", "clean", "quiet", "points="])
    except getopt.GetoptError:
        print("main.py --help --clean --quiet --points <points>")
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print("main.py")
            print("--help                           show this help")
            print("--clean                          clean intermediate results before start")
            print("--quiet                          do not log outputs")
            print("--points                         number of sample points to use")
            sys.exit()
        elif opt in ("-c", "--clean"):
            clean = True
        elif opt in ("-q", "--quiet"):
            quiet = True
        elif opt in ("-p", "--points"):
            num_sample_points = int(arg)

    # Set paths
    file_path = os.path.realpath(__file__)
    script_path = os.path.dirname(file_path)
    data_path = os.path.join(script_path, "data", "data")
    results_path = os.path.join(script_path, "results", "results")

    # Iterate over cities
    for city in cities:

        results_path = os.path.join(results_path, "city")

        # Initialize logger
        logger = LoggerFacade(results_path, console=True, file=True)

        # Generate sample points
        sample_points = PointGenerator().run(
            logger=logger,
            data_path=data_path,
            results_path=os.path.join(results_path, city, "sample-points"),
            city=city,
            num_sample_points=num_sample_points,
            clean=clean,
            quiet=quiet
        )

        # Load transport graph
        graph_transport = GraphLoader().run(
            logger=logger,
            results_path=os.path.join(results_path, city, "graphs"),
            city=city,
            transport="all",
            enhance_with_speed=False,
            clean=clean,
            quiet=quiet
        )

        # Load transport stations
        stations = StationLoaderOverpass().run(
            logger=logger,
            results_path=os.path.join(results_path, city, "stations"),
            city=city,
            transport="all",
            clean=clean,
            quiet=quiet
        )

        # Load walk graph
        graph_walk = GraphLoader().run(
            logger=logger,
            results_path=os.path.join(results_path, city, "graphs"),
            city=city,
            transport="walk",
            enhance_with_speed=False,
            clean=clean,
            quiet=quiet
        )

        # Combine transport graph and walk graph
        graph = GraphCombiner().run(
            logger=logger,
            results_path=os.path.join(results_path, city, "graphs"),
            graph_transport=graph_transport,
            graph_walk=graph_walk,
            stations=stations,
            clean=clean,
            quiet=quiet
        )

        # Iterate over travel times
        for travel_time in travel_times:
            # Generate points
            IsochroneBuilder().run(
                logger=logger,
                results_path=os.path.join(results_path, city, "geojson"),
                graph=graph,
                sample_points=sample_points,
                travel_time=travel_time,
                clean=clean,
                quiet=quiet
            )


if __name__ == "__main__":
    main(sys.argv[1:])
