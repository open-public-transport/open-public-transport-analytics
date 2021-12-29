import glob
import json
import os

import osm2geojson
from tracking_decorator import TrackingDecorator


def load_json(file_path):
    with open(file_path, "r") as f:
        text = f.read()

    return json.loads(text.replace("'", ""))


def convert_json_to_geojson(file_path, json_content):
    geojson = osm2geojson.json2geojson(json_content)

    with open(file_path, "w") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=4)

    return geojson


#
# Main
#

class OsmToGeojsonConverter:

    @TrackingDecorator.track_time
    def run(self, logger, data_path, results_path, public_transport_type, clean=False, quiet=False):

        # Make results path
        os.makedirs(os.path.join(results_path), exist_ok=True)

        for file_path in glob.iglob(data_path + "/*.json"):

            results_file_path = os.path.join(results_path, os.path.basename(file_path).replace(".json", ".geojson"))

            # Check if result needs to be generated
            if clean or not os.path.exists(results_file_path):

                json_content = load_json(file_path)
                convert_json_to_geojson(
                    file_path=results_file_path,
                    json_content=json_content
                )

                if not quiet:
                    logger.log_line(f"✓ Convert {public_transport_type} to GeoJSON")
