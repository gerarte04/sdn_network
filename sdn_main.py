from csv_handler import write_csv_topology
import gml  # source: https://github.com/icasdri/gml.py
import math
import sys

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

def find_minimum_spanning_tree(net_edges):  # Kruskal's algorithm
    edges_idx = [i for i in range(len(net_edges))]   # pool of free edges indices
    tree_edges = []         # list of minimum spanning tree edges
    tree_nodes_ids = []     # list of id's of its nodes

    while True:     # while there is edges that doesn't forming a cycle after adding to tree
        min_idx = None
        min_weight = 0

        for i in edges_idx:
            if (net_edges[i].distance is not None and                           # if attribute is not none
                    not (net_edges[i].gml_edge.source in tree_nodes_ids and     # and no cycle is forming after adding the edge
                    net_edges[i].gml_edge.target in tree_nodes_ids) and
                    (min_idx is None or net_edges[i].distance < min_weight)):   # and the edge has less weight
                min_idx = i
                min_weight = net_edges[i].distance  # then we found new candidate

        if min_idx is None: # if not found any then break
            break

        if net_edges[min_idx].gml_edge.source not in tree_nodes_ids:    # adding new nodes
            tree_nodes_ids.append(net_edges[min_idx].gml_edge.source)
        if net_edges[min_idx].gml_edge.target not in tree_nodes_ids:
            tree_nodes_ids.append(net_edges[min_idx].gml_edge.target)

        tree_edges.append(net_edges[min_idx])   # adding new edge
        edges_idx.remove(min_idx)  # removing from pool of free edges

    return tree_edges

gml_parser = gml.Parser()
gml_parser.load_gml(sys.argv[1])
gml_parser.parse()

gml_graph = gml_parser.graph
net_edges = [NetEdge(edge) for edge in gml_graph.graph_edges]

tree = find_minimum_spanning_tree(net_edges)

write_csv_topology('out/' + sys.argv[1].split('/')[1].replace('.gml', '') + '_topo.csv', net_edges)
