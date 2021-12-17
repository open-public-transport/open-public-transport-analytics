import getopt
import os
import sys

# Make library available in path
library_paths = [
    os.path.join(os.getcwd(), "lib"),
    os.path.join(os.getcwd(), "lib", "loader", "osmnx"),
    os.path.join(os.getcwd(), "lib", "loader", "overpass"),
    os.path.join(os.getcwd(), "lib", "loader", "peartree"),
    os.path.join(os.getcwd(), "lib", "converter"),
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
from overpass_route_loader import OverpassRouteLoader
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
         "bounding_box": [13.088333218007715, 52.33824183586156, 13.759587218876971, 52.67491714954712],
         "transport_association": "vbb"},
        {"name": "bochum", "query": "Bochum, Germany", "area": 145, "inhabitants": 364_000,
         "bounding_box": [7.102082282000026, 51.41051770900003, 7.349335097000051, 51.531372340000075],
         "transport_association": "vrr"},
        {"name": "bonn", "query": "Bonn, Germany", "area": 141, "inhabitants": 330_000,
         "bounding_box": [7.022537442000043, 50.63268994200007, 7.210679743000071, 50.77437020800005],
         "transport_association": "vrs"},
        # {"name": "bremen", "query": "Bremen, Germany", "area": 318, "inhabitants": 566_000,
        # "bounding_box": [8.481735118728654, 53.01102137832358, 8.990780355986436, 53.60761767768827],
        # "transport_association": None },
        {"name": "cottbus", "query": "Cottbus, Germany", "area": 165, "inhabitants": 89_000,
         "bounding_box": [14.273306525769822, 51.69248183636231, 14.501295507607326, 51.86416174658669],
         "transport_association": "vbb"},
        {"name": "dortmund", "query": "Dortmund, Germany", "area": 280, "inhabitants": 597_000,
         "bounding_box": [7.303593755474529, 51.416072806289165, 7.637115868651861, 51.59952017917111],
         "transport_association": "vrr"},
        {"name": "duesseldorf", "query": "Düsseldorf, Germany", "area": 217, "inhabitants": 620_000,
         "bounding_box": [6.68881312000002, 51.124375875000055, 6.939933901000074, 51.352486457000055],
         "transport_association": "vrr"},
        {"name": "duisburg", "query": "Duisburg, Germany", "area": 232, "inhabitants": 495_000,
         "bounding_box": [6.625616443645652, 51.333198590659165, 6.83045999817622, 51.560220016593334],
         "transport_association": "vrr"},
        # {"name": "frankfurt-main", "query": "Frankfurt (Main), Germany", "area": 248, "inhabitants": 764_000,
        # "bounding_box": [8.47276067000007, 50.01524884200006, 8.800381926000057, 50.22712951500006],
        # "transport_association": None},
        {"name": "frankfurt-oder", "query": "Frankfurt (Oder), Germany", "area": 147, "inhabitants": 57_000,
         "bounding_box": [14.394834417176915, 52.25277200883128, 14.600891619659311, 52.39823335093446],
         "transport_association": "vbb"},
        {"name": "hamburg", "query": "Hamburg, Germany", "area": 755, "inhabitants": 1_851_000,
         "bounding_box": [9.73031519588174, 53.39507758854026, 10.325959157503767, 53.73808674380358],
         "transport_association": "hhv"},
        {"name": "hamm", "query": "Hamm, Germany", "area": 226, "inhabitants": 178_000,
         "bounding_box": [7.675536280292723, 51.57805231922079, 7.997528913639968, 51.744766475157476],
         "transport_association": "vrr"},
        {"name": "koeln", "query": "Köln, Germany", "area": 405, "inhabitants": 1_083_000,
         "bounding_box": [6.772530403000076, 50.83044939600006, 7.162027995000074, 51.08497434000003],
         "transport_association": "vrs"},
        {"name": "muenchen", "query": "München, Germany", "area": 310, "inhabitants": 1_488_000,
         "bounding_box": [11.36087720838895, 48.06223277978042, 11.723082533270206, 48.24814577602209],
         "transport_association": "mvv"},
        {"name": "muenster", "query": "Münster, Germany", "area": 303, "inhabitants": 316_000,
         "bounding_box": [7.473962942770497, 51.840191151329854, 7.774221787742102, 52.060175509627584],
         "transport_association": "nwl "},
        {"name": "potsdam", "query": "Potsdam, Germany", "area": 188, "inhabitants": 182_000,
         "bounding_box": [12.888410253169791, 52.342942127472284, 13.165897844431854, 52.51476310782476],
         "transport_association": "vbb"},
        {"name": "stuttgart", "query": "Stuttgart, Germany", "area": 207, "inhabitants": 630_000,
         "bounding_box": [9.03899379817525, 48.69015070969232, 9.315387276070416, 48.86724862272663],
         "transport_association": "vvs"},
        {"name": "wuppertal", "query": "Wuppertal, Germany", "area": 168, "inhabitants": 355_000,
         "bounding_box": [7.01407471400006, 51.165736174000074, 7.313426359000061, 51.31809703300007],
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

        for means_of_transportation in ["bus", "subway", "light_train", "tram"]:
            # Load routes
            OverpassRouteLoader().run(
                logger=logger,
                results_path=results_path,
                city=city_name,
                bounding_box=bounding_box,
                transport=means_of_transportation,
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
                    clean=clean,
                    quiet=quiet
                )


if __name__ == "__main__":
    main(sys.argv[1:])
