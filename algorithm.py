import math

def find_minimum_spanning_tree(net_nodes):      # алгоритм Прима
    nodes_idx = [node.id for node in net_nodes]                         # список непросмотренных вершин
    tree_edges = [min(net_nodes[0].edges, key=lambda e: e.delay)]       # список ребер дерева, сначала кладем ребро с минимальным весом (задержкой)
    cur_nodes = [tree_edges[0].src_node, tree_edges[0].tgt_node]        # список вершин, из которых потенциально могут выходить подходящие ребра
    nodes_idx.remove(tree_edges[0].src)     # вершины первого ребра уже просмотрены                           # (у которых один конец принадлежит дереву, другой - нет)
    nodes_idx.remove(tree_edges[0].tgt)

    while len(nodes_idx) > 0:       # пока есть непросмотренные вершины
        new_edge = cur_nodes[0].edges[0]    # очередное ребро, которое добавим в дерево
        first_node = cur_nodes[0]           # конец этого ребра, принадлежащий дереву
        min_dist = math.inf             # вес такого ребра (выбираем минимальный)
        pop_indices = []                # индексы вершин, которые удалим из cur_nodes на этом шаге

        for i in range(len(cur_nodes)):
            new_edges = list(filter(lambda e: (e.src in nodes_idx) ^ (e.tgt in nodes_idx), cur_nodes[i].edges)) # ищем ребра вершин из cur_nodes, у которых не принадлежит дереву только один конец
                                                                                                                
            if len(new_edges) == 0:     # если таких ребер не нашлось, то позже удалим эту вершину из cur_nodes
                pop_indices.append(i)
            else:
                min_edge = min(new_edges, key=lambda e: e.delay)    # иначе выберем ребро с минимальным весом
                if min_edge.delay < min_dist:                       # если вес меньше, чем у new_edge, то заменяем на min_edge
                    min_dist = min_edge.delay
                    new_edge = min_edge
                    first_node = cur_nodes[i]

        off = 0
        for i in pop_indices:   # производим процесс удаления из cur_nodes
            cur_nodes.pop(i - off)
            off += 1

        tree_edges.append(new_edge)         # найденное ребро добавляем в ребра дерева
        new_node = new_edge.tgt_node if new_edge.src == first_node.id else new_edge.src_node
        nodes_idx.remove(new_node.id)       # конец, не принадлежащий дереву, убираем из непросмотренных
        
        cur_nodes.append(new_node)      # и добавляем в cur_nodes

    return tree_edges

def find_closest_ways(net_nodes, id_src):    # алгоритм Дейкстры с одноуровневыми корзинами и калибровкой
    class NodeInfo:         # метаданные, хранящиеся в объекте каждого узла
        visited = False         # вершина уже посещена или нет
        in_bucket = False       # находится ли она в данный момент в одной из корзин
        mark = math.inf         # текущая метка вершины
        path_to = [id_src]      # путь от id_src до этой вершины
        branch = []             # cписок ребер этого пути

    mu = 0              # минимальная метка из еще не посещенных вершин
    def caliber(node):
        return min(node.edges, key=lambda e: e.delay).delay
    def lemma(node):
        return mu + caliber(node) >= node.meta.mark

    buckets = {}    # корзины
    exact = []      # вершины с точными метками
    routes = []     # список для обновления коэффициента mu
    for node in net_nodes:      # инициализация метаданных вершин
        node.meta = NodeInfo()
        if node.id == id_src:
            node.meta.mark = 0
            exact.append(node)
            routes.append(node.meta.mark)

    L = 0                       # индекс корзины
    total = len(net_nodes)      # количество непосещенных вершин

    while total > 0:            # пока есть непосещенные вершины
        if len(exact) > 0:      # если есть точные вершины, то берем оттуда
            cur = exact[0]
            exact.pop(0)
        else:                   # иначе берем из корзины с минимальным весом
            if len(buckets.keys()) == 0:        # отсутствие вершин и в корзинах, и в exact может быть при наличии нескольких компонент связности в графе
                raise RuntimeError('there is probably several connectivity components')
            L = min(buckets.keys())
            cur = buckets[L][0]
            buckets[L].pop(0)
            if len(buckets[L]) == 0:
                buckets.pop(L)
        
        cur.meta.visited = True
        total -= 1
        mu = min(routes)        # обновляем коэффициент
        routes.remove(cur.meta.mark)

        for edge in cur.edges:
            neighbor = edge.tgt_node if edge.src == cur.id else edge.src_node   # проходимся по всем соседям текущей вершины

            if not neighbor.meta.visited:
                new_mark = cur.meta.mark + edge.delay   # рассчитываем метку вершины, если идти от текущей

                if new_mark < neighbor.meta.mark:       # если получается уменьшить метку вершины
                    if neighbor.meta.in_bucket:         # удаляем соседа из корзины, если он там находился
                        buckets[neighbor.meta.mark].remove(neighbor)
                        if len(buckets[neighbor.meta.mark]) == 0:
                            buckets.pop(neighbor.meta.mark)

                    neighbor.meta.mark = new_mark       # обновляем метаданные соседа
                    neighbor.meta.path_to = cur.meta.path_to + [neighbor.id]
                    neighbor.meta.branch = cur.meta.branch + [edge]
                    routes.append(new_mark)             # обновляем значения меток для обновления mu

                    if lemma(neighbor):                     # в зависимости от того, выполняется ли условие леммы,
                        neighbor.meta.in_bucket = False     # записываем соседа либо в точные вершины, либо в одну из корзин
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

    return delays, paths, branches      # возвращаем итоговые метки вершин и получившиеся маршруты
