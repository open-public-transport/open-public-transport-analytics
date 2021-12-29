from ranked_value import RankedValue


class LineInformation:
    def __init__(self, public_transport_type=""):
        self.public_transport_type = public_transport_type  # all, bus, light_rail, subway, tram
        self.absolute_line_count = RankedValue()
        self.absolute_line_accessibility_count = RankedValue()
        self.relative_line_accessibility_percentage = RankedValue()
        self.relative_line_per_sqkm = RankedValue()
        self.relative_line_per_inhabitant = RankedValue()
