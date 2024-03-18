from csv_handler import write_csv_topology, write_csv_spanning_tree
import gml  # source: https://github.com/icasdri/gml.py
import math
from net_edge import NetEdge, NetNode, calc_distance_km, calc_delay_mks
import sys
from visualizer import visualize_network

def find_minimum_spanning_tree(net_nodes):  # Kruskal's algorithm
    nodes_idx = [node.id for node in net_nodes]   # pool of free nodes indices
    tree_edges = [min(net_nodes[nodes_idx[0]].edges, key=lambda e: 0 if e.distance is None else e.distance)]         # list of minimum spanning tree edges
    nodes_idx.pop(0)
    cur_nodes = [tree_edges[0].src_node, tree_edges[0].tgt_node]

    while len(nodes_idx) > 0:
        new_edge = cur_nodes[0].edges[0]
        first_node = cur_nodes[0]
        min_dist = math.inf

        for node in cur_nodes:
            dist_none = lambda e: 0 if e.distance is None else e.distance
            new_edges = list(filter(lambda e: e not in tree_edges, node.edges))
            min_edge = min(new_edges, key=dist_none)
            if dist_none(min_edge) < min_dist:
                min_dist = dist_none(min_edge)
                new_edge = min_edge
                first_node = node

        tree_edges.append(new_edge)
        cur_nodes.remove(first_node)
        nodes_idx.remove(first_node.id)
        cur_nodes.append(new_edge.tgt_node if new_edge.src == first_node.id else new_edge.src_node)

    return tree_edges 

def find_closest_ways(net_nodes, id_src):    # Dijkstra's algorithm
    class NodeInfo:
        visited = False
        mark = math.inf
        path_to = [id_src]

    for node in net_nodes:
        node.meta = NodeInfo()
        if node.id == id_src:
            node.meta.mark = 0

    net_nodes = sorted(net_nodes, key = lambda n: (n.meta.visited, n.meta.mark))
    cur_nodes = []
    next_nodes = [net_nodes[0]]

    while len(next_nodes) > 0:
        cur_nodes = next_nodes
        next_nodes = []

        for cur in cur_nodes:
            cur.meta.visited = True
            for edge in cur.edges:
                neighbor = edge.tgt_node if edge.src == cur.id else edge.src_node

                if not neighbor.meta.visited:
                    next_nodes.append(neighbor)
                    new_mark = cur.meta.mark + edge.delay

                    if new_mark < neighbor.meta.mark:
                        neighbor.meta.mark = new_mark
                        neighbor.meta.path_to = cur.meta.path_to + edge.hyperlink + [neighbor.id]

    return {n.id: round(n.meta.mark, 5) for n in net_nodes}, {n.id: n.meta.path_to for n in net_nodes}

gml_parser = gml.Parser()
gml_parser.load_gml(sys.argv[1])
gml_parser.parse()

gml_graph = gml_parser.graph
gml_edges = gml_graph.graph_edges
gml_nodes = gml_graph.graph_nodes

net_edges = []
hyperlinked = {}

net_nodes = [NetNode(node) for node in gml_nodes.values()]

for edge in gml_edges:
    src_node = next(n for n in net_nodes if n.id == edge.source)
    tgt_node = next(n for n in net_nodes if n.id == edge.target)
    new_edge = NetEdge(src_node, tgt_node)

    net_edges.append(new_edge)
    src_node.add_edge(new_edge)
    tgt_node.add_edge(new_edge)

tree = find_minimum_spanning_tree(net_nodes)

min_delays, min_paths = {}, {}
max_delay = math.inf

for id in gml_nodes.keys():
    delays, paths = find_closest_ways(net_nodes, id)
    new_max_delay = max(delays.values())
    if new_max_delay < max_delay:
        min_delays = delays
        min_paths = paths
        max_delay = new_max_delay

prefix = 'out/' + sys.argv[1].split('/')[1].replace('.gml', '')
write_csv_topology(prefix + '_topo.csv', net_edges)
write_csv_spanning_tree(prefix + '_routes.csv', min_delays, min_paths)

visualize_network(net_edges, tree)
