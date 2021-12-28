from ranked_value import RankedValue


class LineInformation:
    def __init__(self, transport_type=""):
        self.transport_type = transport_type  # all, bus, light_rail, subway, tram
        self.absolute_line_count = RankedValue()
        self.absolute_line_accessibility_count = RankedValue()
        self.relative_line_accessibility_percentage = RankedValue()
        self.relative_line_per_sqkm = RankedValue()
        self.relative_line_per_inhabitant = RankedValue()
