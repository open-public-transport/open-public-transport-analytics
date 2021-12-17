import json
import os
from urllib.parse import quote

import osm2geojson
import requests
from tracking_decorator import TrackingDecorator


def download_station_json(logger, bounding_box, transport):
    bbox = f"({bounding_box[1]}, {bounding_box[0]}, {bounding_box[3]}, {bounding_box[2]})"

    try:
        data = f"""
[out:json][timeout:25];
(
  relation["route"~"{transport}"]{bbox};  
);
out geom;
"""

        formatted_data = quote(data.lstrip("\n"))

        url = f"https://overpass-api.de/api/interpreter?data={formatted_data}"
        response = requests.get(url)
        text = response.text.replace("'", "")
        return json.loads(text)

    except Exception as e:
        logger.log_line(f"✗️ Exception: {str(e)}")
        return None


def load_geojson(file_path):
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

class OverpassRouteLoader:

    @TrackingDecorator.track_time
    def run(self, logger, results_path, city, bounding_box, transport, clean=False, quiet=False):
        # Make results path
        os.makedirs(os.path.join(results_path), exist_ok=True)

        # Define file path
        file_path = os.path.join(results_path, transport + ".geojson")

        # Check if result needs to be generated
        if clean or not os.path.exists(file_path):

            # Download graph
            json_content = download_station_json(
                logger=logger,
                bounding_box=bounding_box,
                transport=transport
            )

            geojson = convert_json_to_geojson(
                file_path=file_path,
                json_content=json_content
            )

            if geojson is not None:
                if not quiet:
                    logger.log_line(f"✓ Download {city} transport {transport}")

                return geojson
            else:
                return None
        else:
            # Load graph
            geojson = load_geojson(file_path=file_path)

            if not quiet:
                logger.log_line(f"✓ Load {city} transport {transport}")

            return geojson
