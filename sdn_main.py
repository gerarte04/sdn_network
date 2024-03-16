from csv_handler import write_csv_topology
import gml  # source: https://github.com/icasdri/gml.py
import math
from net_edge import NetEdge
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

def find_closest_ways(net_edges, nodes_ids, id_src):    # Dijkstra's algorithm
    class NetNode:
        visited = False
        mark = math.inf
        path_to = [id_src]

        def __init__(self, id):
            self._id = id
            if id == id_src:
                self.mark = 0
        
        @property
        def id(self):
            return self._id
        
        def __repr__(self):
            return str(self._id)

    net_nodes = [NetNode(id) for id in nodes_ids]
    net_nodes = sorted(net_nodes, key = lambda n : (n.visited, n.mark))
    cur_nodes = []
    next_nodes = [net_nodes[0]]

    while len(next_nodes) > 0:
        cur_nodes = next_nodes
        next_nodes = []
        for cur in cur_nodes:
            if cur.id == 67:
                print('fuck')
            cur.visited = True
            cur_edges = list(filter(lambda n: (n.src == cur.id or n.tgt == cur.id), net_edges))

            for edge in cur_edges:
                if edge.delay is not None:
                    neighbor = None
                    if edge.src == cur.id:
                        neighbor = next(n for n in net_nodes if edge.tgt == n.id)
                    else:
                        neighbor = next(n for n in net_nodes if edge.src == n.id)

                    if not neighbor.visited:
                        next_nodes.append(neighbor)
                        new_mark = cur.mark + edge.delay

                        if new_mark < neighbor.mark:
                            neighbor.mark = new_mark
                            neighbor.path_to = cur.path_to + [neighbor.id]

    return {n.id: round(n.mark, 5) for n in net_nodes}, {n.id: n.path_to for n in net_nodes}

gml_parser = gml.Parser()
gml_parser.load_gml(sys.argv[1])
gml_parser.parse()

gml_graph = gml_parser.graph
net_edges = [NetEdge(edge) for edge in gml_graph.graph_edges]
nodes_ids = list(gml_graph.graph_nodes.keys())

tree = find_minimum_spanning_tree(net_edges)

dists, paths = find_closest_ways(tree, nodes_ids, 0)

for i in dists.keys():
    print(i, 'dist:', dists[i], 'path:', paths[i])

write_csv_topology('out/' + sys.argv[1].split('/')[1].replace('.gml', '') + '_topo.csv', net_edges)

visualize_network(net_edges, tree)
