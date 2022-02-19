import json
import os
from urllib.parse import quote

import requests
from tracking_decorator import TrackingDecorator


def download_json(logger, file_path, bounding_box, query):
    bbox = f"({bounding_box[1]}, {bounding_box[0]}, {bounding_box[3]}, {bounding_box[2]})"

    try:
        data = f"""
[out:json][timeout:25];
(
  {query}{bbox};  
);
out geom;
                """

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
        if logger is not None:
            logger.log_line(f"✗️ Exception: {str(e)}")
        return None


def load_json(file_path):
    with open(file_path, "r") as f:
        text = f.read()

    return json.loads(text.replace("'", ""))


#
# Main
#

class OverpassLoader:

    def __init__(self, logger, results_path, city_id, bounding_box, clean, quiet):
        self.logger = logger
        self.results_path = results_path
        self.city_id = city_id
        self.bounding_box = bounding_box
        self.clean = clean
        self.quiet = quiet

    @TrackingDecorator.track_time
    def run(self, result_file_name, query, bounding_box=None, clean=False):
        # Make results path
        os.makedirs(os.path.join(self.results_path), exist_ok=True)

        # Define file path
        file_path = os.path.join(self.results_path, result_file_name)

        # Check if result needs to be generated
        if self.clean or clean or not os.path.exists(file_path):

            # Override bounding box if necessary
            if bounding_box is None:
                bounding_box = self.bounding_box

            # Download json
            json_content = download_json(
                logger=self.logger,
                file_path=file_path,
                bounding_box=bounding_box,
                query=query
            )

            if json_content is not None:
                if not self.quiet:
                    self.logger.log_line(f"✓ Download {self.city_id} {result_file_name}")

                return json_content
            else:
                if not self.quiet:
                    self.logger.log_line(f"✗️ Failed to download {self.city_id} {result_file_name}")

                return None
        else:
            # Load graph
            json_content = load_json(file_path=file_path)

            if not self.quiet:
                self.logger.log_line(f"✓ Load {self.city_id} {result_file_name}")

            return json_content
