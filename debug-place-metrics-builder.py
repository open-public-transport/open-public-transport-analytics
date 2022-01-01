import os
import sys

file_path = os.path.realpath(__file__)
script_path = os.path.dirname(file_path)

# Make library available in path
library_paths = [
    os.path.join(script_path, "app", "model"),
    os.path.join(script_path, "lib"),
    os.path.join(script_path, "lib", "config"),
    os.path.join(script_path, "lib", "cloud"),
    os.path.join(script_path, "lib", "loader", "osmnx"),
    os.path.join(script_path, "lib", "loader", "overpass"),
    os.path.join(script_path, "lib", "loader", "peartree"),
    os.path.join(script_path, "lib", "converter"),
    os.path.join(script_path, "lib", "log"),
    os.path.join(script_path, "lib", "metrics"),
]

for p in library_paths:
    if not (p in sys.path):
        sys.path.insert(0, p)

# Import library classes
from tracking_decorator import TrackingDecorator
from place_metrics_builder import PlaceMetricsBuilder

# Set paths
data_path = os.path.join(script_path, "..", "data", "data")
base_results_path = os.path.join(script_path, "..", "results", "results")

#
# Main
#

@TrackingDecorator.track_time
def main(argv):
    PlaceMetricsBuilder(results_path=os.path.join(base_results_path, "berlin".lower())).run(
        city_id="berlin",
        lat=52.516389,
        lon=13.377778
    )


if __name__ == "__main__":
    main(sys.argv[1:])
