import math

def calc_distance_km(src_node, tgt_node):    # based on formula from http://www.movable-type.co.uk/scripts/latlong.html
    def deg2rad(angle):
        return angle * math.pi / 180
    
    R = 6371    # Earth radius in km

    lat1 = deg2rad(src_node.lat)
    lat2 = deg2rad(tgt_node.lat)
    lon1 = deg2rad(src_node.lon)
    lon2 = deg2rad(tgt_node.lon)

    a = (
        math.pow(math.sin((lat2 - lat1) / 2), 2) +
        math.cos(lat1) *
        math.cos(lat2) *
        math.pow(math.sin((lon2 - lon1) / 2), 2)
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = R * c

    return round(d, 2)

def calc_delay_mks(distance_km):
    return round(distance_km * 4.8)  # 4.8 is delay per km (in mks/km)

class NetNode:
    meta = None

    def __init__(self, gml_node):
        self._id = getattr(gml_node, 'id')
        self._lat = getattr(gml_node, 'Latitude')
        self._lon = getattr(gml_node, 'Longitude')

        try:
            self._label = getattr(gml_node, 'label')
        except AttributeError:
            self._label = '-'

        self._edges = []

    def add_edge(self, net_edge):
        self._edges.append(net_edge)

    def pop_edge(self, i):
        self._edges.pop(i)

    @property
    def id(self):
        return self._id
    
    @property
    def lat(self):
        return self._lat
    
    @property
    def lon(self):
        return self._lon
    
    @property
    def label(self):
        return self._label
    
    @property
    def edges(self):
        return self._edges
    
    def __repr__(self):
        return self._label + '(' + str(self._id) + ')'

class NetEdge:
    def __init__(self, src_node, tgt_node):
        self._src = src_node.id
        self._tgt = tgt_node.id
        self._src_node = src_node
        self._tgt_node = tgt_node

        self._distance = calc_distance_km(self._src_node, self._tgt_node)
        self._delay = calc_delay_mks(self._distance)
    
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
    
    @property
    def src_node(self):
        return self._src_node
    
    @property
    def tgt_node(self):
        return self._tgt_node

    def __repr__(self):
        return '(' + str(self._src) + ',' + str(self._tgt) + ')'
