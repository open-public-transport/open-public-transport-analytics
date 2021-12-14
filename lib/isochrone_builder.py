import os.path

import geopy.distance
import networkx as nx
import numpy as np
import osmnx as ox
from geojson import FeatureCollection
from shapely.geometry import MultiPoint, Polygon
from tqdm import tqdm

from tracking_decorator import TrackingDecorator


def get_spatial_distance(logger, graph, start_point, travel_time, distance_attribute="time"):
    try:
        nodes, edges, walking_distance_meters = get_possible_routes(
            graph=graph,
            start_point=start_point,
            travel_time=travel_time,
            distance_attribute=distance_attribute,
            calculate_walking_distance=True
        )

        longitudes, latitudes = get_convex_hull(nodes=nodes)
        points = []
        for point in zip(latitudes, longitudes):
            points.append([point[0],point[1]]) 
        
        polygon = Polygon(points)

        transport_distances_meters = get_distances(start_point=start_point, latitudes=latitudes, longitudes=longitudes)

        return np.mean(transport_distances_meters) + walking_distance_meters, \
               np.median(transport_distances_meters) + walking_distance_meters, \
               np.min(transport_distances_meters) + walking_distance_meters, \
               np.max(transport_distances_meters) + walking_distance_meters, \
                polygon.area
    except Exception as e:
        logger.log_line(f"✗️ Exception: {str(e)}")
        return 0, 0, 0, 0, 0


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
        subgraph = nx.ego_graph(graph, center_node, radius=radius, distance=distance_attribute)
        nodes, edges = ox.graph_to_gdfs(subgraph)
        return nodes, edges, walking_distance_meters
    else:
        return [], [], walking_distance_meters


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
        }
        features.append(feature)

    collection = FeatureCollection(features)

    with open(file_path, "w") as f:
        f.write("%s" % collection)


#
# Main
#

class IsochroneBuilder:

    @TrackingDecorator.track_time
    def run(self, logger, results_path, graph, sample_points, travel_time, clean=False, quiet=False):
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

            mean_spatial_distance, \
            median_spatial_distance, \
            min_spatial_distance, \
            max_spatial_distance, \
                area = get_spatial_distance(
                logger=logger,
                graph=graph,
                start_point=start_point,
                travel_time=travel_time
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
            file_path=os.path.join(results_path, "isochrones-" + str(travel_time)),
            coords=points_with_spatial_distance,
            travel_time=travel_time
        )

        write_points_to_geojson(
            file_path=os.path.join(results_path, "isochrones-" + str(travel_time)) + "-failed",
            coords=failed_points,
            travel_time=travel_time
        )

        return points_with_spatial_distance, failed_points
