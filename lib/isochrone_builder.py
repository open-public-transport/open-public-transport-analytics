import json
import os.path

import geopy.distance
import networkx as nx
import numpy as np
import osmnx as ox
from geojson import FeatureCollection
from osgeo import ogr
from shapely.geometry import MultiPoint, Polygon
from tqdm import tqdm

from tracking_decorator import TrackingDecorator


def get_isochrone(logger, graph, start_point, travel_time, distance_attribute="time"):
    try:
        return get_possible_routes(
            graph=graph,
            start_point=start_point,
            travel_time=travel_time,
            distance_attribute=distance_attribute,
            calculate_walking_distance=True
        )
    except Exception as e:
        logger.log_line(f"✗️ Exception: {str(e)}")
        return None, 0


def get_isochrone_metrics(logger, data_path, city, start_point, subgraph, walking_distance_meters):
    try:
        nodes, edges = ox.graph_to_gdfs(subgraph)

        # Define valid polygons
        polygon_file = os.path.join(data_path, "cities", city, "boundaries", "boundaries.geojson")
        valid_polygons = get_polygons(read_geojson(polygon_file))

        longitudes, latitudes = get_convex_hull(nodes=nodes)
        points = []
        for point in zip(longitudes, latitudes):

            p = ogr.Geometry(ogr.wkbPoint)
            p.AddPoint(point[0], point[1])

            # Check if point is within city limits
            if is_in_desired_area(p, valid_polygons):
                points.append([point[0], point[1]])
            else:
                logger.log_line(f"{city} point outside city {point[0]}, {point[1]}")

        convex_hull_polygon = Polygon(points)

        transport_distances_meters = get_distances(start_point=start_point, latitudes=latitudes, longitudes=longitudes)

        return np.mean(transport_distances_meters) + walking_distance_meters, \
               np.median(transport_distances_meters) + walking_distance_meters, \
               np.min(transport_distances_meters) + walking_distance_meters, \
               np.max(transport_distances_meters) + walking_distance_meters, \
               convex_hull_polygon.area
    except Exception as e:
        logger.log_line(f"✗️ Exception: {str(e)}")
        return 0, 0, 0, 0, 0


def is_in_desired_area(point, valid_polygons):
    for polygon in valid_polygons:
        if point.Within(polygon):
            return True

    return False


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


def get_possible_routes(graph, start_point, travel_time, distance_attribute, calculate_walking_distance=False):
    center_node, distance_to_nearest_node = ox.nearest_nodes(
        G=graph,
        X=start_point[1],
        Y=start_point[0],
        return_dist=True
    )

    if calculate_walking_distance:
        walking_speed_meters_per_minute = 100
        walking_time_minutes = distance_to_nearest_node / walking_speed_meters_per_minute

        walking_time_minutes_max = walking_time_minutes if walking_time_minutes < travel_time else travel_time
        walking_distance_meters = walking_time_minutes_max * walking_speed_meters_per_minute

        radius = travel_time - walking_time_minutes
    else:
        walking_distance_meters = 0
        radius = travel_time

    if radius > 0:
        return nx.ego_graph(graph, center_node, radius=radius, distance=distance_attribute), walking_distance_meters
    else:
        return None, walking_distance_meters


def get_convex_hull(nodes):
    return MultiPoint(nodes.reset_index()["geometry"]).convex_hull.exterior.coords.xy


def get_distances(start_point, latitudes, longitudes):
    return [geopy.distance.geodesic(point, start_point).meters for point in zip(latitudes, longitudes)]


def write_points_to_geojson(file_path, coords, travel_time):
    features = []
    for coord in coords:
        feature = {}
        feature["geometry"] = {"type": "Point", "coordinates": [coord["lon"], coord["lat"]]}
        feature["type"] = "Feature"
        feature["properties"] = {
            "mean_spatial_distance_" + str(travel_time) + "min": coord[
                "mean_spatial_distance_" + str(travel_time) + "min"],
            "median_spatial_distance_" + str(travel_time) + "min": coord[
                "median_spatial_distance_" + str(travel_time) + "min"],
            "min_spatial_distance_" + str(travel_time) + "min": coord[
                "min_spatial_distance_" + str(travel_time) + "min"],
            "max_spatial_distance_" + str(travel_time) + "min": coord[
                "max_spatial_distance_" + str(travel_time) + "min"],
            "area_" + str(travel_time) + "min": coord[
                "area_" + str(travel_time) + "min"],
        }
        features.append(feature)

    collection = FeatureCollection(features)

    with open(file_path, "w") as f:
        f.write("%s" % collection)


def write_nodes_to_geojson(file_path, graph):
    features = []

    if len(graph.nodes) > 0:
        for node_id in graph.nodes:
            node = graph.nodes[node_id]
            feature = {}
            feature["geometry"] = {"type": "Point", "coordinates": [node["x"], node["y"]]}
            feature["type"] = "Feature"
            features.append(feature)

    collection = FeatureCollection(features)

    with open(file_path, "w") as f:
        f.write("%s" % collection)


def write_polygon_to_geojson(file_path, graph):
    features = []
    coordinates = []

    for node_id in graph.nodes:
        node = graph.nodes[node_id]
        coordinates.append([node["x"], node["y"]])

    if len(graph.nodes) > 0:
        feature = {}
        feature["geometry"] = {"type": "Polygon", "coordinates": coordinates}
        feature["type"] = "Feature"
        features.append(feature)

    collection = FeatureCollection(features)

    with open(file_path, "w") as f:
        f.write("%s" % collection)


#
# Main
#

class IsochroneBuilder:

    @TrackingDecorator.track_time
    def run(self, logger, data_path, results_path, city, graph, sample_points, travel_time, start_time, end_time):
        points_with_spatial_distance = []
        failed_points = []

        # Make results path
        os.makedirs(os.path.join(results_path), exist_ok=True)

        for point_index in tqdm(iterable=range(len(sample_points)),
                                total=len(sample_points),
                                desc="Build isochrone",
                                unit="point"):
            point = sample_points[point_index]
            start_point = (float(point["lat"]), float(point["lon"]))

            # Calculate isochrone
            subgraph, walking_distance_meters = get_isochrone(
                logger=logger,
                graph=graph,
                start_point=start_point,
                travel_time=travel_time
            )

            # Determine isochrone metrics
            mean_spatial_distance, median_spatial_distance, min_spatial_distance, max_spatial_distance, area = get_isochrone_metrics(
                logger=logger,
                data_path=data_path,
                city=city,
                start_point=start_point,
                subgraph=subgraph,
                walking_distance_meters=walking_distance_meters
            )

            point_with_spatial_distance = {
                "lon": point["lon"],
                "lat": point["lat"],
                "mean_spatial_distance_" + str(travel_time) + "min": mean_spatial_distance,
                "median_spatial_distance_" + str(travel_time) + "min": median_spatial_distance,
                "min_spatial_distance_" + str(travel_time) + "min": min_spatial_distance,
                "max_spatial_distance_" + str(travel_time) + "min": max_spatial_distance,
                "area_" + str(travel_time) + "min": area
            }

            if mean_spatial_distance > 0:
                points_with_spatial_distance.append(point_with_spatial_distance)
            else:
                failed_points.append(point_with_spatial_distance)

        write_points_to_geojson(
            file_path=os.path.join(results_path, f"isochrones-{str(travel_time)}min-{start_time}-{end_time}.geojson"),
            coords=points_with_spatial_distance,
            travel_time=travel_time
        )

        write_points_to_geojson(
            file_path=os.path.join(results_path, f"isochrones-{str(travel_time)}min-{start_time}-{end_time}-failed.geojson"),
            coords=failed_points,
            travel_time=travel_time
        )

        return points_with_spatial_distance, failed_points

    @TrackingDecorator.track_time
    def run_for_place(self, logger, data_path, results_path, city, graph, travel_time, place):
        points_with_spatial_distance = []
        failed_points = []
        start_point = (place[1], place[0])

        # Make results path
        os.makedirs(os.path.join(results_path), exist_ok=True)

        # Calculate isochrone
        subgraph, walking_distance_meters = get_isochrone(
            logger=logger,
            graph=graph,
            start_point=start_point,
            travel_time=travel_time
        )

        # Determine isochrone metrics
        mean_spatial_distance, median_spatial_distance, min_spatial_distance, max_spatial_distance, area = get_isochrone_metrics(
            logger=logger,
            data_path=data_path,
            city=city,
            start_point=start_point,
            subgraph=subgraph,
            walking_distance_meters=walking_distance_meters
        )

        write_nodes_to_geojson(file_path=os.path.join(results_path, "isochrone-nodes-" + str(travel_time) + ".geojson"), graph=subgraph)
        write_polygon_to_geojson(file_path=os.path.join(results_path, "isochrone-hull-" + str(travel_time) + ".geojson"), graph=subgraph)

        point_with_spatial_distance = {
            "lon": start_point[1],
            "lat": start_point[0],
            "mean_spatial_distance_" + str(travel_time) + "min": mean_spatial_distance,
            "median_spatial_distance_" + str(travel_time) + "min": median_spatial_distance,
            "min_spatial_distance_" + str(travel_time) + "min": min_spatial_distance,
            "max_spatial_distance_" + str(travel_time) + "min": max_spatial_distance,
            "area_" + str(travel_time) + "min": area
        }

        if mean_spatial_distance > 0:
            points_with_spatial_distance.append(point_with_spatial_distance)
        else:
            failed_points.append(point_with_spatial_distance)

        write_points_to_geojson(
            file_path=os.path.join(results_path, "isochrones-" + str(travel_time) + ".geojson"),
            coords=points_with_spatial_distance,
            travel_time=travel_time
        )

        write_points_to_geojson(
            file_path=os.path.join(results_path, "isochrones-" + str(travel_time)) + "-failed.geojson",
            coords=failed_points,
            travel_time=travel_time
        )

        return points_with_spatial_distance, failed_points
