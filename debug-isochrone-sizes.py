import os
import sys
import glob
import json
import numpy as np

file_path = os.path.realpath(__file__)
script_path = os.path.dirname(file_path)

# Make library available in path
library_paths = [
    os.path.join(script_path, "lib"),
]

for p in library_paths:
    if not (p in sys.path):
        sys.path.insert(0, p)

# Import library classes
from tracking_decorator import TrackingDecorator

#
# Main
#

@TrackingDecorator.track_time
def main(argv):

    # Set paths
    base_results_path = os.path.join(script_path, "results", "results")

    for file_path in glob.iglob(base_results_path + "/**/geojson/isochrones*.geojson"):
        if "failed" not in file_path:
            print(file_path)

            with open(file_path, "r") as f:
                text = f.read()

            geojson = json.loads(text.replace("'", ""))
            features = geojson["features"]

            list_area_15min = []
            list_max_spatial_distance_15min = []
            list_mean_spatial_distance_15min = []
            list_median_spatial_distance_15min = []
            list_min_spatial_distance_15min = []

            for feature in features:
                properties = feature["properties"]
                list_area_15min.append(properties["area_15min"])
                list_max_spatial_distance_15min.append(properties["max_spatial_distance_15min"])
                list_mean_spatial_distance_15min.append(properties["mean_spatial_distance_15min"])
                list_median_spatial_distance_15min.append(properties["median_spatial_distance_15min"])
                list_min_spatial_distance_15min.append(properties["min_spatial_distance_15min"])

            print(f"list_area_15min min {np.min(list_area_15min)}, max {np.max(list_area_15min)}")
            print(f"list_max_spatial_distance_15min min {np.min(list_max_spatial_distance_15min)}, max {np.max(list_max_spatial_distance_15min)}")
            print(f"list_mean_spatial_distance_15min min {np.min(list_mean_spatial_distance_15min)}, max {np.max(list_mean_spatial_distance_15min)}")
            print(f"list_median_spatial_distance_15min min {np.min(list_median_spatial_distance_15min)}, max {np.max(list_median_spatial_distance_15min)}")
            print(f"list_min_spatial_distance_15min min {np.min(list_min_spatial_distance_15min)}, max {np.max(list_min_spatial_distance_15min)}")

            # list_area_15min min 0.0, max 0.0
            # list_max_spatial_distance_15min min 513.6838317491002, max 76047.49935309424
            # list_mean_spatial_distance_15min min 270.0673718232583, max 48093.34648047457
            # list_median_spatial_distance_15min min 153.44633043893361, max 58865.54207809246
            # list_min_spatial_distance_15min min 1.0363824701244273, max 34241.156100123386

if __name__ == "__main__":
    main(sys.argv[1:])
