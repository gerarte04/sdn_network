#! /bin/python3
import argparse
from csv_handler import write_csv_topology, write_csv_spanning_tree
import gml  # source: https://github.com/icasdri/gml.py
import math
from net_edge import NetEdge, NetNode, calc_distance_km, calc_delay_mks
from visualizer import visualize_network
from time import time

def find_minimum_spanning_tree(net_nodes):  # Prim's algorithm
    hyperlinked = {}
    def dist_none(edge, cur_node):
        if edge.distance is not None:
            return edge.distance
        
        another = edge.tgt_node if edge.src == cur_node.id else edge.src_node
        if cur_node.lat is None:
            if another.lat is not None:
                return calc_distance_km(hyperlinked[cur_node.id], another)
            else:
                hyperlinked[another.id] = hyperlinked[cur_node.id]
        else:
            hyperlinked[another.id] = cur_node
        
        return 0

    nodes_idx = [node.id for node in net_nodes]   # pool of free nodes indices
    tree_edges = [min(net_nodes[0].edges, key=lambda e: 0 if e.distance is None else e.distance)]         # list of minimum spanning tree edges
    cur_nodes = [tree_edges[0].src_node, tree_edges[0].tgt_node]
    nodes_idx.remove(tree_edges[0].src)
    nodes_idx.remove(tree_edges[0].tgt)

    while len(nodes_idx) > 0:
        new_edge = cur_nodes[0].edges[0]
        first_node = cur_nodes[0]
        min_dist = math.inf
        pop_indices = []

        for i in range(len(cur_nodes)):
            new_edges = list(filter(lambda e: (e.src in nodes_idx) ^ (e.tgt in nodes_idx), cur_nodes[i].edges))

            if len(new_edges) == 0:
                pop_indices.append(i)
            else:
                min_edge = min(new_edges, key=lambda e: dist_none(e, cur_nodes[i]))
                dist = dist_none(min_edge, cur_nodes[i])
                if dist < min_dist:
                    min_dist = dist
                    new_edge = min_edge
                    first_node = cur_nodes[i]

        off = 0
        for i in pop_indices:
            cur_nodes.pop(i - off)
            off += 1

        tree_edges.append(new_edge)
        new_node = new_edge.tgt_node if new_edge.src == first_node.id else new_edge.src_node
        nodes_idx.remove(new_node.id)
        
        cur_nodes.append(new_node)

    return tree_edges 

def find_closest_ways(net_nodes, id_src):    # Dijkstra's algorithm with multi-buckets improvement
    hyperlinked = {}
    def delay_none(edge, cur_node):
        if edge.delay is not None:
            return edge.delay
        
        another = edge.tgt_node if edge.src == cur_node.id else edge.src_node
        if cur_node.lat is None:
            if another.lat is not None:
                return calc_delay_mks(calc_distance_km(hyperlinked[cur_node.id], another))
            else:
                hyperlinked[another.id] = hyperlinked[cur_node.id]
        else:
            hyperlinked[another.id] = cur_node
        
        return 0

    class NodeInfo:
        visited = False
        mark = math.inf
        path_to = [id_src]

    buckets = {math.inf: []}
    for node in net_nodes:
        node.meta = NodeInfo()
        if node.id == id_src:
            node.meta.mark = 0
            buckets[0] = [node]
        else:
            buckets[math.inf].append(node)

    L = 0
    total = len(net_nodes)

    while total > 0:
        L = min(buckets.keys(), key=lambda k: k if len(buckets[k]) > 0 else math.inf)
        cur = buckets[L][0]
        buckets[L].pop(0)
        cur.meta.visited = True
        total -= 1

        for edge in cur.edges:
            neighbor = edge.tgt_node if edge.src == cur.id else edge.src_node

            if not neighbor.meta.visited:
                new_mark = cur.meta.mark + delay_none(edge, cur)

                if new_mark < neighbor.meta.mark:
                    buckets[neighbor.meta.mark].remove(neighbor)
                    neighbor.meta.mark = new_mark
                    neighbor.meta.path_to = cur.meta.path_to + [neighbor.id]
                    if new_mark not in buckets.keys():
                        buckets[new_mark] = [neighbor]
                    else:
                        buckets[new_mark].append(neighbor)

    return {n.id: round(n.meta.mark, 5) for n in net_nodes}, {n.id: n.meta.path_to for n in net_nodes}

arg_parser = argparse.ArgumentParser(prog='SDN')
arg_parser.add_argument('-t', '--topology', required=True)
arg_parser.add_argument('-k', '--criteria', default=1)
arg_parser.add_argument('-v', '--vis', action='store_true')
args = arg_parser.parse_args()

gml_parser = gml.Parser()
gml_parser.load_gml(args.topology)
gml_parser.parse()

gml_graph = gml_parser.graph
gml_edges = gml_graph.graph_edges
gml_nodes = gml_graph.graph_nodes

net_edges = []

net_nodes = [NetNode(node) for node in gml_nodes.values()]

for edge in gml_edges:
    src_node = next(n for n in net_nodes if n.id == edge.source)
    tgt_node = next(n for n in net_nodes if n.id == edge.target)
    new_edge = NetEdge(src_node, tgt_node)

    net_edges.append(new_edge)
    src_node.add_edge(new_edge)
    tgt_node.add_edge(new_edge)

tree = []

if args.criteria == '2':
    tree = find_minimum_spanning_tree(net_nodes)

    for node in net_nodes:
        pop_indices = []
        for i in range(len(node.edges)):
            if node.edges[i] not in tree:
                pop_indices.append(i)

        off = 0
        for i in pop_indices:
            node.pop_edge(i - off)
            off += 1

min_delays, min_paths = {}, {}
max_delay = math.inf

start = time()
for id in gml_nodes.keys():
    if hasattr(gml_nodes[id], 'Latitude'):
        delays, paths = find_closest_ways(net_nodes, id)
        new_max_delay = max(delays.values())
        if new_max_delay < max_delay:
            min_delays = delays
            min_paths = paths
            max_delay = new_max_delay
print(time() - start)

prefix = 'out/' + args.topology.split('/')[-1].replace('.gml', '')
write_csv_topology(prefix + '_topo.csv', net_edges)
write_csv_spanning_tree(prefix + '_routes.csv', min_delays, min_paths)

if args.vis:
    visualize_network(net_edges, tree)
