from csv_handler import write_csv_topology, write_csv_spanning_tree
import gml  # source: https://github.com/icasdri/gml.py
import math
from net_edge import NetEdge, NetNode
import sys
from visualizer import visualize_network

def find_minimum_spanning_tree(net_edges):  # Kruskal's algorithm
    edges_idx = [i for i in range(len(net_edges))]   # pool of free edges indices
    tree_edges = []         # list of minimum spanning tree edges
    tree_nodes_ids = []     # list of connectivity components
    net_edges = sorted(net_edges, key = lambda n: n.distance if n.distance is not None else math.inf)
    found = True

    while found:
        found = False

        for i in edges_idx:
            comp_src, comp_tgt = None, None
            for j in range(len(tree_nodes_ids)):
                if net_edges[i].src in tree_nodes_ids[j]:
                    comp_src = j
                if net_edges[i].tgt in tree_nodes_ids[j]:
                    comp_tgt = j

                if comp_src is not None and comp_tgt is not None:
                    break
            
            try:
                if comp_src == comp_tgt:
                    if comp_src is not None:
                        continue

                    tree_nodes_ids.append([net_edges[i].src, net_edges[i].tgt])
                else:
                    tree_nodes_ids[comp_src] += tree_nodes_ids[comp_tgt]
                    tree_nodes_ids.pop(comp_tgt)
            except TypeError:
                if comp_src is not None:
                    tree_nodes_ids[comp_src].append(net_edges[i].tgt)
                else:
                    tree_nodes_ids[comp_tgt].append(net_edges[i].src)

            tree_edges.append(net_edges[i])
            edges_idx.remove(i)
            found = True
            break

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

net_nodes = []
net_edges = []
hyperlinked = {}

for node in gml_nodes.values():
    if hasattr(node, 'Latitude'):
        net_nodes.append(NetNode(node))
    else:
        linked_edges = list(filter(lambda edge: edge.source == node.id or edge.target == node.id, gml_edges))
        neighbors = [edge.source if edge.target == node.id else edge.target for edge in linked_edges]
        hyperlinked[node.id] = neighbors

for edge in gml_edges:
    try:
        src_node = next(n for n in net_nodes if n.id == edge.source)
        tgt_node = next(n for n in net_nodes if n.id == edge.target)
        new_edge = NetEdge(src_node, tgt_node)

        net_edges.append(new_edge)
        src_node.add_edge(new_edge)
        tgt_node.add_edge(new_edge)
    except StopIteration:
        pass

for e in hyperlinked.keys():
    for i in range(len(hyperlinked[e])):
        for j in range(i + 1, len(hyperlinked[e])):
            try:
                src_node = next(n for n in net_nodes if n.id == hyperlinked[e][i])
                tgt_node = next(n for n in net_nodes if n.id == hyperlinked[e][j])
                new_edge = NetEdge(src_node, tgt_node, hyperlink=[e])

                net_edges.append(new_edge)
                src_node.add_edge(new_edge)
                tgt_node.add_edge(new_edge)
            except StopIteration:
                pass

tree = find_minimum_spanning_tree(net_edges)

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
