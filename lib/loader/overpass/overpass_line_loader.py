import json
import os
from urllib.parse import quote

import requests
from tracking_decorator import TrackingDecorator


def download_line_json(logger, file_path, bounding_box, public_transport_type):
    bbox = f"({bounding_box[1]}, {bounding_box[0]}, {bounding_box[3]}, {bounding_box[2]})"

    try:
        if public_transport_type == "bus":
            data = f"""
[out:json][timeout:25];
(
  way["highway"~"secondary|tertiary|residential|bus_stop"]{bbox};  
);
out geom;
                """
        elif public_transport_type == "light_rail":
            data = f"""
[out:json][timeout:25];
(
  way["railway"~"light_rail"]{bbox};  
);
out geom;
                """
        elif public_transport_type == "subway":
            data = f"""
[out:json][timeout:25];
(
  way["railway"~"subway"]{bbox};  
);
out geom;
                """
        elif public_transport_type == "tram":
            data = f"""
[out:json][timeout:25];
(
  way["railway"~"tram"]{bbox};  
);
out geom;
                """
        else:
            raise Exception

        formatted_data = quote(data.lstrip("\n"))

        url = f"https://overpass-api.de/api/interpreter?data={formatted_data}"
        response = requests.get(url)
        text = response.text.replace("'", "")
        json_content = json.loads(text)

        if len(json_content["elements"]) > 0:
            with open(file_path, "w") as f:
                json.dump(json_content, f, ensure_ascii=False, indent=4)

            return json_content
        else:
            return None

    except Exception as e:
        logger.log_line(f"✗️ Exception: {str(e)}")
        return None


def load_json(file_path):
    with open(file_path, "r") as f:
        text = f.read()

    return json.loads(text.replace("'", ""))


#
# Main
#

class OverpassLineLoader:

    @TrackingDecorator.track_time
    def run(self, logger, results_path, city, bounding_box, public_transport_type, clean=False, quiet=False):
        # Make results path
        os.makedirs(os.path.join(results_path), exist_ok=True)

        # Define file path
        file_path = os.path.join(results_path, "lines-" + public_transport_type + ".json")

        # Check if result needs to be generated
        if clean or not os.path.exists(file_path):

            # Download json
            json_content = download_line_json(
                logger=logger,
                file_path=file_path,
                bounding_box=bounding_box,
                public_transport_type=public_transport_type
            )

            if json_content is not None:
                if not quiet:
                    logger.log_line(f"✓ Download {city} line {public_transport_type}")

                return json_content
            else:
                if not quiet:
                    logger.log_line(f"✗️ Failed to download {city} line {public_transport_type}")

                return None
        else:
            # Load graph
            json_content = load_json(file_path=file_path)

            if not quiet:
                logger.log_line(f"✓ Load {city} line {public_transport_type}")

            return json_content
