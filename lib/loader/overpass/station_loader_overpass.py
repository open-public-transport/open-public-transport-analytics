import glob
import json
import os
from os import path
from urllib.parse import quote

import requests
from tracking_decorator import TrackingDecorator


def download_station_json(logger, results_path, city, transport):
    try:
        if transport == "all":
            return download_complete_json(logger, results_path, city)
        elif transport == "bus":
            return download_json(
                file_path=os.path.join(results_path, transport + ".json"),
                data=f"""
[out:json][timeout:25];
(
  node["highway"~"bus_stop"]{get_bbox(city)};  
);
out geom;
                """
            )
        elif transport == "light_rail":
            return download_json(
                file_path=os.path.join(results_path, transport + ".json"),
                data=f"""
[out:json][timeout:25];
(
  node["railway"~"station|halt"]["station"~"light_rail"]{get_bbox(city)};  
);
out geom;
                """
            )
        elif transport == "subway":
            return download_json(
                file_path=os.path.join(results_path, transport + ".json"),
                data=f"""
[out:json][timeout:25];
(
  node["railway"~"station|halt"]["station"~"subway"]{get_bbox(city)};  
);
out geom;
                """
            )
        elif transport == "tram":
            return download_json(
                file_path=os.path.join(results_path, transport + ".json"),
                data=f"""
[out:json][timeout:25];
(
  node["railway"~"tram_stop"]{get_bbox(city)};  
);
out geom;
                """
            )

    except Exception as e:
        logger.log_line(f"✗️ Exception: {str(e)}")
        return None


def get_bbox(city):
    if city == "berlin":
        return "(52.33488609760638, 13.091992716067702, 52.67626223889507, 13.742786470433)"
    if city == "hamburg":
        return "(53.739442, 9.7341703, 53.396905, 10.324022)"
    else:
        return None


def download_json(file_path, data, clean=False):
    formatted_data = quote(data.lstrip("\n"))

    if clean or not path.exists(file_path):
        url = f"https://overpass-api.de/api/interpreter?data={formatted_data}"
        response = requests.get(url)
        text = response.text.replace("'", "")
        data = json.loads(text)
        elements = data["elements"]

        with open(file_path, "w") as f:
            json.dump(elements, f, ensure_ascii=False, indent=4)

        return elements


def download_complete_json(logger, results_path, city):
    stations = []
    stations_bus = download_station_json(logger=logger, results_path=results_path, city=city,
                                         transport="bus")
    stations_light_rail = download_station_json(logger=logger, results_path=results_path, city=city,
                                                transport="light_rail")
    stations_subway = download_station_json(logger=logger, results_path=results_path, city=city,
                                            transport="subway")
    stations_tram = download_station_json(logger=logger, results_path=results_path, city=city,
                                          transport="tram")

    if stations_bus is not None:
        stations += stations_bus
    if stations_light_rail is not None:
        stations += stations_light_rail
    if stations_subway is not None:
        stations += stations_subway
    if stations_tram is not None:
        stations += stations_tram

    file_path=os.path.join(results_path, "all.json")
    with open(file_path, "w") as f:
        json.dump(stations, f, ensure_ascii=False, indent=4)

    return stations


def load_station_json(file_path):
    with open(file_path, "r") as f:
        text = f.read()

    data = json.loads(text.replace("\'", "\""))
    elements = data

    return elements


#
# Main
#

class StationLoaderOverpass:

    @TrackingDecorator.track_time
    def run(self, logger, results_path, city, transport, clean=False, quiet=False):
        # Make results path
        os.makedirs(os.path.join(results_path), exist_ok=True)

        # Define file path
        file_path = os.path.join(results_path, transport + ".json")

        # Check if result needs to be generated
        if clean or not os.path.exists(file_path):

            # Clean results path
            files = glob.glob(os.path.join(results_path, "*.json"))
            for f in files:
                os.remove(f)

            # Download graph
            json = download_station_json(
                logger=logger,
                results_path=results_path,
                city=city,
                transport=transport
            )

            if json is not None:
                if not quiet:
                    logger.log_line(f"✓ Combine {file_path} with {len(json)} entries")

                return json
            else:
                return None
        else:
            # Load graph
            json = load_station_json(file_path=file_path)

            if not quiet:
                logger.log_line(f"✓ Load {file_path} with {len(json)} entries")

            return json
