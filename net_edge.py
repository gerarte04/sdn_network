import math

def calc_distance_km(gml_edge):    # based on formula from http://www.movable-type.co.uk/scripts/latlong.html
    def deg2rad(angle):
        return angle * math.pi / 180
    
    R = 6371    # Earth radius in km

    try:
        lat1 = deg2rad(getattr(gml_edge.source_node, 'Latitude'))
        lat2 = deg2rad(getattr(gml_edge.target_node, 'Latitude'))
        lon1 = deg2rad(getattr(gml_edge.source_node, 'Longitude'))
        lon2 = deg2rad(getattr(gml_edge.target_node, 'Longitude'))
    except AttributeError:
        return None

    a = (
        math.pow(math.sin((lat2 - lat1) / 2), 2) +
        math.cos(lat1) *
        math.cos(lat2) *
        math.pow(math.sin((lon2 - lon1) / 2), 2)
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = R * c

    return round(d, 5)

def calc_delay_mks(distance_km):
    return None if distance_km is None else round(distance_km * 4.8, 5)

class NetEdge:
    def __init__(self, gml_edge):
        self._gml_edge = gml_edge
        self._src = gml_edge.source
        self._tgt = gml_edge.target
        self._distance = calc_distance_km(gml_edge)
        self._delay = calc_delay_mks(self._distance)

    @property
    def gml_edge(self):
        return self._gml_edge
    
    @property
    def distance(self):
        return self._distance
    
    @property
    def delay(self):
        return self._delay
    
    @property
    def src(self):
        return self._src
    
    @property
    def tgt(self):
        return self._tgt
