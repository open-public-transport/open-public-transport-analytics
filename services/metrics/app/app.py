import random

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "https://openpublictransport.de",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PointOnInterest(BaseModel):
    lat = 0
    lon = 0


class Metrics:
    index = 0

    def __init__(self, index):
        self.index = index

@app.get("/index")
def get_mobility_index(lat, lon):
    return Metrics(
        index=random.randint(0, 100)
    )


@app.post("/index")
def post_mobility_index(data: PointOnInterest):
    data = data.dict()
    lat = data["lat"]
    lon = data["lon"]

    return Metrics(
        index=random.randint(0, 100)
    )
