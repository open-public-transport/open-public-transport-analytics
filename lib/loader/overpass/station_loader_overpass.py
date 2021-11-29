import json
import os
from os import path
from urllib.parse import quote

import requests

from tracking_decorator import TrackingDecorator


def get_station_json(logger, results_path, city, transport, clean=False, quiet=False):
    try:
        if transport == "all":
            stations = []
            stations_bus = get_station_json(logger=logger, results_path=results_path, city=city, transport="bus",
                                            clean=False,
                                            quiet=False)
            stations_light_rail = get_station_json(logger=logger, results_path=results_path, city=city,
                                                   transport="light_rail",
                                                   clean=False, quiet=False)
            stations_subway = get_station_json(logger=logger, results_path=results_path, city=city, transport="subway",
                                               clean=False,
                                               quiet=False)
            stations_tram = get_station_json(logger=logger, results_path=results_path, city=city, transport="tram",
                                             clean=False,
                                             quiet=False)

            if stations_bus is not None:
                stations += stations_bus
            if stations_light_rail is not None:
                stations += stations_light_rail
            if stations_subway is not None:
                stations += stations_subway
            if stations_tram is not None:
                stations += stations_tram

            return stations
        elif transport == "bus":
            return load_json(
                logger=logger,
                file_path=os.path.join(results_path, transport + ".json"),
                data=f"""
[out:json][timeout:25];
(
  node["highway"~"bus_stop"]{get_bbox(city)};  
);
out geom;
                """,
                clean=clean,
                quiet=quiet
            )
        elif transport == "light_rail":
            return load_json(
                logger=logger,
                file_path=os.path.join(results_path, transport + ".json"),
                data=f"""
[out:json][timeout:25];
(
  node["railway"~"station|halt"]["station"~"light_rail"]{get_bbox(city)};  
);
out geom;
                """,
                clean=clean,
                quiet=quiet
            )
        elif transport == "subway":
            return load_json(
                logger=logger,
                file_path=os.path.join(results_path, transport + ".json"),
                data=f"""
[out:json][timeout:25];
(
  node["railway"~"station|halt"]["station"~"subway"]{get_bbox(city)};  
);
out geom;
                """,
                clean=clean,
                quiet=quiet
            )
        elif transport == "tram":
            return load_json(
                logger=logger,
                file_path=os.path.join(results_path, transport + ".json"),
                data=f"""
[out:json][timeout:25];
(
  node["railway"~"tram_stop"]{get_bbox(city)};  
);
out geom;
                """,
                clean=clean,
                quiet=quiet
            )

    except Exception as e:
        print(e)
        return None


def get_bbox(city):
    if city == "berlin":
        return "(52.33488609760638, 13.091992716067702, 52.67626223889507, 13.742786470433)"
    else:
        return None


def load_json(logger, file_path, data, clean=False, quiet=False):
    formatted_data = quote(data.lstrip("\n"))

    if clean or not path.exists(file_path):

        url = f"https://overpass-api.de/api/interpreter?data={formatted_data}"
        response = requests.get(url)
        text = response.text.replace("'", "")
        data = json.loads(text)
        elements = data["elements"]

        with open(file_path, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        if not quiet:
            logger.log_line(f"✓ Download {file_path} with {len(elements)} entries")

        return elements
    else:
        with open(file_path, "r") as f:
            text = f.read()

        data = json.loads(text.replace("\'", "\""))
        elements = data["elements"]

        if not quiet:
            logger.log_line(f"✓ Load {file_path} with {len(elements)} entries")

        return elements


#
# Main
#

class StationLoaderOverpass:

    @TrackingDecorator.track_time
    def run(self, logger, results_path, city, transport, clean=False, quiet=False):
        # Make results path
        os.makedirs(os.path.join(results_path), exist_ok=True)

        # Load graph
        json = get_station_json(
            logger=logger,
            results_path=results_path,
            city=city,
            transport=transport,
            clean=clean,
            quiet=quiet
        )

        return json
