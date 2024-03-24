import math

def find_minimum_spanning_tree(net_nodes):  # Prim's algorithm
    nodes_idx = [node.id for node in net_nodes]   # pool of free nodes indices
    tree_edges = [min(net_nodes[0].edges, key=lambda e: e.delay)]         # list of minimum spanning tree edges
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

def find_closest_ways(net_nodes, id_src):    # Dijkstra's algorithm with buckets and caliber
    class NodeInfo:
        visited = False
        in_bucket = False
        mark = math.inf
        path_to = [id_src]
        branch = []

    mu = 0
    def caliber(node):
        return min(node.edges, key=lambda e: e.delay).delay
    def lemma(node):
        return mu + caliber(node) >= node.meta.mark

    buckets = {}
    exact = []
    routes = []
    for node in net_nodes:
        node.meta = NodeInfo()
        if node.id == id_src:
            node.meta.mark = 0
            exact.append(node)
            routes.append(node.meta.mark)

    L = 0
    total = len(net_nodes)

    while total > 0:
        if len(exact) > 0:
            cur = exact[0]
            exact.pop(0)
        else:
            if len(buckets.keys()) == 0:
                raise RuntimeError('there is probably several connectivity components')
            L = min(buckets.keys())
            cur = buckets[L][0]
            buckets[L].pop(0)
            if len(buckets[L]) == 0:
                buckets.pop(L)
        
        cur.meta.visited = True
        total -= 1
        mu = min(routes)
        routes.remove(cur.meta.mark)

        for edge in cur.edges:
            neighbor = edge.tgt_node if edge.src == cur.id else edge.src_node

            if not neighbor.meta.visited:
                new_mark = cur.meta.mark + edge.delay

                if new_mark < neighbor.meta.mark:
                    if neighbor.meta.in_bucket:
                        buckets[neighbor.meta.mark].remove(neighbor)
                        if len(buckets[neighbor.meta.mark]) == 0:
                            buckets.pop(neighbor.meta.mark)

                    neighbor.meta.mark = new_mark
                    neighbor.meta.path_to = cur.meta.path_to + [neighbor.id]
                    neighbor.meta.branch = cur.meta.branch + [edge]
                    routes.append(new_mark)

                    if lemma(neighbor):
                        neighbor.meta.in_bucket = False
                        exact.append(neighbor)
                    else:
                        neighbor.meta.in_bucket = True
                        if new_mark not in buckets.keys():
                            buckets[new_mark] = [neighbor]
                        else:
                            buckets[new_mark].append(neighbor)

    delays = {n.id: round(n.meta.mark, 5) for n in net_nodes if n.meta.mark > 0}
    paths = {n.id: n.meta.path_to for n in net_nodes if len(n.meta.path_to) > 1}
    branches = {n.id: n.meta.branch for n in net_nodes if len(n.meta.branch) > 0}

    return delays, paths, branches
