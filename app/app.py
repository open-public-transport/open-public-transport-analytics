import os
import sys

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

file_path = os.path.realpath(__file__)
script_path = os.path.dirname(file_path)

# Make library available in path
library_paths = [
    os.path.join(script_path, "model"),
    os.path.join(script_path, "..", "lib"),
    os.path.join(script_path, "..", "lib", "config"),
    os.path.join(script_path, "..", "lib", "cloud"),
    os.path.join(script_path, "..", "lib", "loader", "osmnx"),
    os.path.join(script_path, "..", "lib", "loader", "overpass"),
    os.path.join(script_path, "..", "lib", "loader", "peartree"),
    os.path.join(script_path, "..", "lib", "converter"),
    os.path.join(script_path, "..", "lib", "metrics"),
    os.path.join(script_path, "..", "lib", "log"),
]

for p in library_paths:
    if not (p in sys.path):
        sys.path.insert(0, p)

# Import library classes
from place_metrics_builder import PlaceMetricsBuilder
from city_metrics_builder import CityMetricsBuilder

# Set paths
data_path = os.path.join(script_path, "..", "data", "data")
base_results_path = os.path.join(script_path, "..", "results", "results")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # LOCAL
        "http://localhost:4200",
        # QA
        "https://open-public-transport-qa.web.app",
        "https://open-public-transport-qa.firebaseapp.com",
        # PROD
        "https://open-public-transport-prod.web.app",
        "https://open-public-transport-prod.firebaseapp.com",
        "https://openpublictransport.de"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#
# Dashboard
#

@app.get("/isochrones")
def get_isochrones(city):
    # TODO Implement
    return {}


@app.get("/transport")
def get_isochrones(city, public_transport_type):
    # TODO Implement
    return {}


#
# Comparison
#

@app.get("/place")
def get_place_metrics(city_id="berlin", lat=52.516389, lon=13.377778):
    return PlaceMetricsBuilder(results_path=os.path.join(base_results_path, city_id.lower())).run(
        city_id=city_id,
        lat=lat,
        lon=lon
    )


@app.get("/isochrone")
def get_isochrones(lat, lon, public_transport_type):
    # TODO Implement
    return {}


#
# Overview
#

@app.get("/cities")
def get_cities():
    return CityMetricsBuilder(results_path=base_results_path).run(clean=False)


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
