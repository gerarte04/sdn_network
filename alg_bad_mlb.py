import math
from time import time

def find_minimum_spanning_tree(net_nodes):  # Prim's algorithm
    nodes_idx = [node.id for node in net_nodes]
    tree_edges = [min(net_nodes[0].edges, key=lambda e: e.delay)]
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
                min_edge = min(new_edges, key=lambda e: e.delay)
                if min_edge.delay < min_dist:
                    min_dist = min_edge.delay
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
    class NodeInfo:
        visited = False
        mark = math.inf
        path_to = [id_src]

    STEP = 1000
    MAX = 30000
    def scnd_idx(mark):
        div = math.inf if mark == math.inf else mark - mark % STEP
        return MAX if div > MAX else div

    buckets = {i: {} for i in range(0, MAX + 1, STEP)}
    buckets[MAX][math.inf] = []

    for node in net_nodes:
        node.meta = NodeInfo()
        if node.id == id_src:
            node.meta.mark = 0
            buckets[0][0] = [node]
        else:
            buckets[MAX][math.inf].append(node)

    lt, lb = 0, 0
    total = len(net_nodes)

    while total > 0 and lb <= MAX:
        if lt not in buckets[lb] or len(buckets[lb][lt]) == 0:
            lt += 1
            if lt >= lb + STEP:
                lb += STEP
                lt = lb
            continue

        cur = buckets[lb][lt][0]
        buckets[lb][lt].pop(0)
        cur.meta.visited = True
        total -= 1

        for edge in cur.edges:
            neighbor = edge.tgt_node if edge.src == cur.id else edge.src_node

            if not neighbor.meta.visited:
                new_mark = cur.meta.mark + edge.delay

                if new_mark < neighbor.meta.mark:
                    buckets[scnd_idx(neighbor.meta.mark)][neighbor.meta.mark].remove(neighbor)
                    neighbor.meta.mark = new_mark
                    neighbor.meta.path_to = cur.meta.path_to + [neighbor.id]
                    scnd = scnd_idx(new_mark)
                    if new_mark not in buckets[scnd]:
                        buckets[scnd][new_mark] = [neighbor]
                    else:
                        buckets[scnd][new_mark].append(neighbor)

    return {n.id: round(n.meta.mark, 5) for n in net_nodes}, {n.id: n.meta.path_to for n in net_nodes}
