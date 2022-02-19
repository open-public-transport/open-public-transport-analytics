import random

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from shapely.geometry import Point, LineString #, MultiPoint, MultiLineString #, Polygon

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "https://open-public-transport-qa.web.app",
        "https://openpublictransport.de",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

### Storage Methods to Load from firebase
#
#
#
#-------------------------------------------------------------------------------
# Imports
def load_data_from_firebase():
    '''
    Connect to the Firebase Storage and load data to stateless container
    '''
    import pyrebase
    import os

    #-------------------------------------------------------------------------------
    # Variables & Setup
    filelist = [ f for f in os.listdir(".") if f.endswith(".JPG") ]
    for f in filelist:
        os.remove(os.path.join(".", f))

    config = {
        "apiKey": "API Key",
        "authDomain": "authdomain",
        "databaseURL": "https://??????.firebaseio.com",
        "projectId": "??????",
        "storageBucket": "????????.appspot.com",
        "serviceAccount": "serviceAccountKey.json"
    }

    firebase_storage = pyrebase.initialize_app(config)
    storage = firebase_storage.storage()

    #-------------------------------------------------------------------------------
    # Uploading And Downloading Images

    # storage.child("Guitar.JPG").put("Guitar.JPG")
    # storage.child("PlayingGuitar.JPG").download("PlayingGuitar.JPG")

    all_files = storage.list_files()

    # Download all Files to local dir in the stateless container
    for file in all_files:
        print(file.name)
        file.download_to_filename(file.name)

### LOAD GRAPHS ###
#
#
#
#

class CityBasicInformation:
    def __init__(self):
        self.city_name = ""
        self.federal_state_name = ""
        self.group = "",
        self.inhabitants = -1,
        self.area = -1,
        self.population_density = -1,


class RankedValue:
    def __init__(self):
        self.raw_value = -1
        self.overall_rank = -1  # Rank across all cities
        self.grouped_rank = -1  # Rank across cities of same group, e.g. metropolis, small town
        self.overall_percentile = -1  # Percentile across all cities
        self.grouped_percentile = -1  # Percentile across cities of same group, e.g. metropolis, small town


class StationInformation:
    def __init__(self):
        self.transport_type = ""  # all, bus, light_rail, subway, tram
        self.absolute_stations_count = RankedValue(),
        self.absolute_stations_accessibility_count = RankedValue(),
        self.relative_stations_accessibility_percentage = RankedValue(),
        self.relative_stations_per_sqkm = RankedValue(),
        self.relative_stations_per_inhabitant = RankedValue(),



class LineInformation:
    def __init__(self):
        self.transport_type = ""  # all, bus, light_rail, subway, tram
        self.absolute_line_count = RankedValue(),
        self.absolute_line_accessibility_count = RankedValue(),
        self.relative_line_accessibility_percentage = RankedValue(),
        self.relative_line_per_sqkm = RankedValue(),
        self.relative_line_per_inhabitant = RankedValue(),


class TravelDistanceInformation:
    def __init__(self):
        self.transport_type = ""  # all, bus, light_rail, subway, tram
        self.absolute_avg_isochrone_area = RankedValue(),
        self.absolute_avg_isochrone_area_rank = RankedValue(),


class PlaceMetrics:
    def __init__(self):
        self.mobility_index = random.randint(0, 100)
        self.station_information = [StationInformation()]
        self.line_information = [LineInformation()]
        self.travel_distance_information = [TravelDistanceInformation()]


class CityMetrics:
    def __init__(self):
        self.city_basic_information = CityBasicInformation()
        self.station_information = [StationInformation()]
        self.travel_distance_information = [TravelDistanceInformation()]


#
# Dashboard
#

@app.get("/isochrones")
def get_isochrones(city):
    # TODO Implement
    return {}


@app.get("/transport")
def get_isochrones(city, transport):
    # TODO Implement
    return {}


#
# Comparison
#

@app.get("/place")
def get_metrics(lat, lon):
    '''
    find or emit some information for same place with coordinates are given to the route/endpoint.
    functions ->
        It is nessecary to define an methode to find nearby stations.
        It is nessecary to define an methode to find nearby lines.
        It is nessecary to define an methode to calculate an index.
        It is nessecary to define an methode to calculate a travel distance.

    Parameters
    ----------
        lat: float
        lon: float
    Return
    ------
        returns an PlaceMetricsObject witch includes Stationinformation (as List), Lineinformation (as List), IndexScore and TravelDistanceInformation
    '''

    def find_nearby_entity(point, geometry, distance = 0.02):
        '''
        Global Method to find entities ind some GEO Stuff
        
        Parameters
        ----------
        lat: float
        lon: float
        geometry: geometry Object like a LineSting or a Point
        distance: float #round about 2KM

        Return
        ------
        Boolean: 
            True/False
        '''
        circle_buffer = point.buffer(distance)

        #All Version has different compute costs and the last Method (VERSION 3) has different numbers of lines

        #return geometry.within(circle_buffer) #VERSION 1 -> lines 3813 -> Wall time: 1.09 s
        #return circle_buffer.contains(geometry) #VERSION 2 -> lines 3813 -> Wall time: 1.13 s
        return point.distance(geometry) < distance #VERSION 3 -> lines 3898 -> Wall time: 1.31 s

    # TODO Implement methode to find nearby stations
    def find_nearby_stations(point, data):
        '''
        It is nessecary to define an methode to find nearby stations.
        Load an geojson with stations and find some stuff.
        
        Parameters
        ----------
        point: shapely PointObject
        data: GeoDataFrame - GeoJSON

        Return
        ------
        List: 
            of Stationinformation Classobjects
        '''
        stations = []
        #point = Point(lat, lon)
        for geom in data.geometry:
            if find_nearby_entity(lat, lon, geom):
                # TODO build an Object to store all the Information, COunt or Whatever
                stations.append('row with Data') 
                pass
        
        # TODO use ListComprehensions or Lambda Statements to reduce the compute cost
        #stations_object = [row for row in data if find_nearby_entity(lat, lon, geom)]
        
        # TODO implement return Objectstructure like GEOM + id + description 
        # ... id is nessecary to reference the lines/routes
        
        return

    # TODO Implement methode to find nearby lines
    def find_nearby_lines(point, data):
        '''
        It is nessecary to define an methode to find nearby lines.
        Load an geojson with stations and find some stuff.

        2 Ways ... with RouteID or with Coords from Point with Buffer or Distance

        Return
        ------
        List:
            of Lineinformation Classobjects
        '''
        lines = []
        #### VERSION ONE WITHIN #### 
        for geom in data.geometry:
            if find_nearby_entity(lat, lon, geom):
                # TODO build an Object to store all the Information, COunt or Whatever
                lines.append('row with Data') 
                pass
        
        # TODO use ListComprehensions or Lambda Statements to reduce the compute cost
        # lines_object = [row for row in data if find_nearby_entity(lat, lon, geom)]

        # TODO implement return Objectstructure like GEOM + id + description 
        return

    # TODO Implement methode to calculate an index
    def calculate_index():
        pass

    # TODO Implement methode to calculate a travel distance
    def calculate_travel_distance():
        pass

    return PlaceMetrics()


@app.get("/isochrone")
def get_isochrones(lat, lon, transport):
    # TODO Implement
    return {}


#
# Overview
#

@app.get("/cities")
def get_cities():
    # TODO Implement
    return [
        CityMetrics()
    ]
