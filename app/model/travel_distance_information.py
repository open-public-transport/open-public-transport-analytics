from ranked_value import RankedValue


class TravelDistanceInformation:
    def __init__(self):
        self.public_transport_type = ""  # all, bus, light_rail, subway, tram
        self.absolute_avg_isochrone_area = RankedValue()
        self.absolute_avg_isochrone_area_rank = RankedValue()
