import csv
import glob
import json
import os
import random

from geojson import FeatureCollection
from osgeo import ogr
from tqdm import tqdm

from tracking_decorator import TrackingDecorator


def read_geojson(file_path):
    file = open(file_path)
    return json.load(file)


def get_polygons(geojson):
    polygons = []

    # Extract polygons from inhabitants file
    features = geojson["features"]

    for feature in features:
        geom = feature["geometry"]
        geom = json.dumps(geom)
        polygon = ogr.CreateGeometryFromJson(geom)

        polygons.append(polygon)

    return polygons


def get_bounding_box(polygon):
    env = polygon.GetEnvelope()
    return env[0], env[2], env[1], env[3]


def get_random_points_in_polygons(valid_polygons, invalid_polygons, sample_points):
    points = []
    xmin = None
    ymin = None
    xmax = None
    ymax = None

    for polygon in valid_polygons:

        # Get bounding box
        boundingXmin, boundingYmin, boundingXmax, boundingYmax = get_bounding_box(polygon)

        if xmin == None or boundingXmin < xmin:
            xmin = boundingXmin
        if ymin == None or boundingYmin < ymin:
            ymin = boundingYmin
        if xmax == None or boundingXmax > xmax:
            xmax = boundingXmax
        if ymax == None or boundingYmax > ymax:
            ymax = boundingYmax

    counter = 0
    fail_counter = 0

    progress_bar = tqdm(iterable=range(1, sample_points + 1), unit="points", desc="Generate points")
    for _ in progress_bar:

        while True:
            point = ogr.Geometry(ogr.wkbPoint)
            point.AddPoint(random.uniform(xmin, xmax),
                           random.uniform(ymin, ymax))

            if is_in_desired_area(point, valid_polygons, invalid_polygons):
                points.append(point)
                counter += 1
                break
            else:
                fail_counter += 1

    return points


def is_in_desired_area(point, valid_polygons, invalid_polygons):
    in_district = False
    for polygon in valid_polygons:
        if point.Within(polygon):
            in_district = True
            break

    if not in_district:
        return False

    for polygon in invalid_polygons:
        if point.Within(polygon):
            return False

    return True


def get_coordinates(points):
    data = []
    for p in points:
        coord = {}
        coord["lon"] = p.GetX()
        coord["lat"] = p.GetY()
        data.append(coord)

    return data


def write_coords_to_json(coords, file_path, clean=False):
    if clean or not os.path.exists(file_path):
        json_data = json.dumps(coords)
        with open(file_path, "w") as f:
            f.write("%s" % json_data)


def write_coords_to_csv(coords, file_path, clean=False):
    if clean or not os.path.exists(file_path):
        with open(file_path, "w") as f:
            writer = csv.writer(f)
            for coord in coords:
                writer.writerow([coord["lon"], coord["lat"]])


def write_coords_to_geojson(coords, file_path, clean=False):
    if clean or not os.path.exists(file_path):
        features = []
        for coord in coords:
            feature = {}
            feature["geometry"] = {"type": "Point", "coordinates": [coord["lon"], coord["lat"]]}
            feature["type"] = "Feature"
            features.append(feature)

        collection = FeatureCollection(features)

        with open(file_path, "w") as f:
            f.write("%s" % collection)


#
# Main
#

class PointGenerator:

    @TrackingDecorator.track_time
    def run(self, logger, data_path, results_path, city="berlin", num_sample_points=10_000, quiet=False, clean=False):

        # Make results path
        os.makedirs(os.path.join(results_path), exist_ok=True)

        # Clean results path
        if clean:
            files = glob.glob(os.path.join(results_path, "*"))
            for f in files:
                os.remove(f)

        # Define valid polygons
        valid_polygons = get_polygons(
            read_geojson(os.path.join(data_path, city, "inhabitants", "inhabitants.geojson")))

        # Define invalid polygons
        invalid_polygons = []
        for invalid_polygon in ["cemetery.geojson", "farmland.geojson", "farmyard.geojson", "forest.geojson",
                                "garden.geojson", "park.geojson", "recreation_ground.geojson", "water.geojson",
                                "wood.geojson"]:
            invalid_polygons += get_polygons(read_geojson(os.path.join(data_path, city, "landuse", invalid_polygon)))

        # Generate points in polygons
        points = get_random_points_in_polygons(valid_polygons, invalid_polygons, num_sample_points)

        # Get coordinates
        coords = get_coordinates(points)

        # Write coords to file
        write_coords_to_json(coords, os.path.join(results_path, "sample-points.json"), clean=clean)
        write_coords_to_csv(coords, os.path.join(results_path, "sample-points.csv"), clean=clean)
        write_coords_to_geojson(coords, os.path.join(results_path, "sample-points.geojson"), clean=clean)

        if not quiet:
            logger.log_line("✓️ Generating " + str(num_sample_points) + " sample points in " + city)

        return coords
