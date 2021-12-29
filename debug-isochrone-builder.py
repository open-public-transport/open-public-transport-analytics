import os
import sys

file_path = os.path.realpath(__file__)
script_path = os.path.dirname(file_path)

# Make library available in path
library_paths = [
    os.path.join(script_path, "lib"),
    os.path.join(script_path, "lib", "cloud"),
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
from peartree_graph_loader import PeartreeGraphLoader
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
        # {"name": "berlin", "query": "Berlin, Germany", "area": 891, "inhabitants": 3_600_000,
        #  "bounding_box": [13.088333218007715, 52.33824183586156, 13.759587218876971, 52.67491714954712],
        #  "transport_association": "vbb"},
        {"name": "koeln", "query": "Köln, Germany", "area": 405, "inhabitants": 1_083_000,
         "bounding_box": [6.772530403000076, 50.83044939600006, 7.162027995000074, 51.08497434000003],
         "transport_association": "vrs"},
    ]
    places = [
        # {"name": "gesundbrunnen", "coords": (13.389444444444, 52.548611111111)},
        # {"name": "ahrensfelde", "coords": (13.565, 52.571667)},
        # {"name": "hauptbahnhof", "coords": (13.369444, 52.525)},
        {"name": "köln hauptbahnhof", "coords": (6.958056, 50.9425)}
    ]
    start_end_times = [(7 * 60 * 60, 8 * 60 * 60)]
    travel_times = [15]

    # Set paths
    data_path = os.path.join(script_path, "data", "data")
    base_results_path = os.path.join(script_path, "results", "debug")

    # Iterate over cities
    for city in cities:

        city_id = city["id"]
        city_name = city["name"]
        query = city["query"]
        area = city["area"]
        inhabitants = city["inhabitants"]
        bounding_box = city["bounding_box"]
        transport_association = city["transport_association"]

        results_path = os.path.join(base_results_path, city_id)

        # Initialize logger
        logger = LoggerFacade(results_path, console=True, file=True)

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
                existing_graph=None,
                clean=True,
                quiet=quiet
            )

            # Iterate over travel times
            for travel_time in travel_times:

                # Iterate over places
                for place in places:
                    place_name = place["name"]
                    coords = place["coords"]
                    results_path = os.path.join(base_results_path, place_name)

                    # Build isochrone
                    IsochroneBuilder().run_for_place(
                        logger=logger,
                        data_path=data_path,
                        results_path=os.path.join(results_path, "geojson"),
                        city_id=city_id,
                        graph=graph,
                        travel_time=travel_time,
                        place=coords
                    )


if __name__ == "__main__":
    main(sys.argv[1:])
