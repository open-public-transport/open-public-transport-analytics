import getopt
import os
import sys

# Make library available in path
library_paths = [
    os.path.join(os.getcwd(), "lib"),
    os.path.join(os.getcwd(), "lib", "loader", "osmnx"),
    os.path.join(os.getcwd(), "lib", "loader", "overpass"),
    os.path.join(os.getcwd(), "lib", "loader", "peartree"),
    os.path.join(os.getcwd(), "lib", "log"),
]

for p in library_paths:
    if not (p in sys.path):
        sys.path.insert(0, p)

# Import library classes
from tracking_decorator import TrackingDecorator
from point_generator import PointGenerator
from peartree_graph_loader import PeartreeGraphLoader
from osmnx_graph_loader import OsmnxGraphLoader
from graph_transformer import GraphTransformer
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
    points_per_sqkm = 100
    cities = [
        {"name": "berlin", "query": "Berlin, Germany", "area": 891, "inhabitants": 3_600_000,
         "transport_association": "vbb"},
        {"name": "bonn", "query": "Bonn, Germany", "area": 141, "inhabitants": 330_000, "transport_association": "vrs"},
        {"name": "bochum", "query": "Bochum, Germany", "area": 145, "inhabitants": 364_000,
         "transport_association": "vrr"},
        # {"name": "bremen", "query": "Bremen, Germany", "area": 318, "inhabitants": 566_000, "transport_association": None },
        {"name": "cottbus", "query": "Cottbus, Germany", "area": 165, "inhabitants": 89_000,
         "transport_association": "vbb"},
        {"name": "dortmund", "query": "Dortmund, Germany", "area": 280, "inhabitants": 597_000,
         "transport_association": "vrr"},
        {"name": "duesseldorf", "query": "Düsseldorf, Germany", "area": 217, "inhabitants": 620_000,
         "transport_association": "vrr"},
        {"name": "duisburg", "query": "Duisburg, Germany", "area": 232, "inhabitants": 495_000,
         "transport_association": "vrr"},
        # {"name": "frankfurt-main", "query": "Frankfurt (Main), Germany", "area": 248, "inhabitants": 764_000, "transport_association": None},
        {"name": "frankfurt-oder", "query": "Frankfurt (Oder), Germany", "area": 147, "inhabitants": 57_000,
         "transport_association": "vbb"},
        {"name": "hamburg", "query": "Hamburg, Germany", "area": 755, "inhabitants": 1_851_000,
         "transport_association": "hhv"},
        {"name": "hamm", "query": "Hamm, Germany", "area": 226, "inhabitants": 178_000, "transport_association": "vrr"},
        {"name": "koeln", "query": "Köln, Germany", "area": 405, "inhabitants": 1_083_000,
         "transport_association": "vrs"},
        {"name": "muenchen", "query": "München, Germany", "area": 310, "inhabitants": 1_488_000,
         "transport_association": "mvv"},
        {"name": "muenster", "query": "Münster, Germany", "area": 303, "inhabitants": 316_000,
         "transport_association": "nwl "},
        {"name": "potsdam", "query": "Potsdam, Germany", "area": 188, "inhabitants": 182_000,
         "transport_association": "vbb"},
        {"name": "stuttgart", "query": "Stuttgart, Germany", "area": 207, "inhabitants": 630_000,
         "transport_association": "vvs"},
        {"name": "wuppertal", "query": "Wuppertal, Germany", "area": 168, "inhabitants": 355_000,
         "transport_association": "vrr"},
    ]
    start_end_times = [(7 * 60 * 60, 8 * 60 * 60)]
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
    file_path = os.path.realpath(__file__)
    script_path = os.path.dirname(file_path)
    data_path = os.path.join(script_path, "data", "data")
    base_results_path = os.path.join(script_path, "results", "results")

    # Iterate over cities
    for city in cities:

        city_name = city["name"]
        query = city["query"]
        area = city["area"]
        inhabitants = city["inhabitants"]
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
                    results_path=os.path.join(results_path, "geojson"),
                    graph=graph,
                    sample_points=sample_points,
                    travel_time=travel_time,
                    clean=clean,
                    quiet=quiet
                )


if __name__ == "__main__":
    main(sys.argv[1:])
