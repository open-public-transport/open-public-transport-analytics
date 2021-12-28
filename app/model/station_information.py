from ranked_value import RankedValue


class StationInformation:
    def __init__(self, transport_type=""):
        self.transport_type = transport_type  # all, bus, light_rail, subway, tram
        self.absolute_stations_count = RankedValue()
        self.absolute_stations_accessibility_count = RankedValue()
        self.relative_stations_accessibility_percentage = RankedValue()
        self.relative_stations_per_sqkm = RankedValue()
        self.relative_stations_per_inhabitant = RankedValue()
