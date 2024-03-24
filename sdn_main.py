#! /bin/python3
from algorithm import find_closest_ways, find_minimum_spanning_tree
import argparse
from csv_handler import write_csv_topology, write_csv_spanning_tree
import gml  # источник: https://github.com/icasdri/gml.py
import math
from net_edge import NetEdge, NetNode
from time import time
from tqdm.auto import tqdm
from visualizer import visualize_network

arg_parser = argparse.ArgumentParser()      # парсинг аргументов командной строки
arg_parser.add_argument('-t', '--topology', required=True,
                        help='topology .gml file')
arg_parser.add_argument('-k', '--criteria', default=1, choices=['1', '2'], 
                        help='criteria of controller placement (K1 of K2+K1)')
arg_parser.add_argument('-v', '--vis', action='store_true', 
                        help='enable visualization')
args = arg_parser.parse_args()

gml_parser = gml.Parser()       # парсинг gml-файла
gml_parser.load_gml(args.topology)
gml_parser.parse()

gml_graph = gml_parser.graph
gml_edges = gml_graph.graph_edges
gml_nodes = gml_graph.graph_nodes

# инициализация узлов, вершины без атрибутов Latitude и Longitude отбрасываются
net_nodes = [NetNode(node) for node in gml_nodes.values() if hasattr(node, 'Latitude') and hasattr(node, 'Longitude')]
net_edges = []

for edge in gml_edges:      # инициализация ребер
    try:
        src_node = next(n for n in net_nodes if n.id == edge.source)        # ищем объекты концов данного ребра
        tgt_node = next(n for n in net_nodes if n.id == edge.target)
    except StopIteration:
        continue
    new_edge = NetEdge(src_node, tgt_node)

    net_edges.append(new_edge)
    src_node.add_edge(new_edge)     # также добавим ссылки на ребра в соответствующие поля объектов NetNode
    tgt_node.add_edge(new_edge)

if args.criteria == '2':            # если был выбран критерий К2+К1,
    min_tree = find_minimum_spanning_tree(net_nodes)

    for node in net_nodes:          # то удалим ребра, не принадлежащие минимальному остовному дереву, из объектов NetNode
        pop_indices = []
        for i in range(len(node.edges)):
            if node.edges[i] not in min_tree:
                pop_indices.append(i)

        off = 0
        for i in pop_indices:
            node.pop_edge(i - off)
            off += 1

min_delays, min_paths, min_branches = {}, {}, {}
controller = None
max_delay = math.inf
start = time()

for _, node in tqdm(enumerate(net_nodes)):
    delays, paths, branches = find_closest_ways(net_nodes, node.id)     # для каждой вершины запустим алгоритм Дейкстры
    new_max_delay = max(delays.values())                                # и попробуем уменьшить максимальную задержку
    if new_max_delay < max_delay:
        min_delays, min_paths, min_branches = delays, paths, branches
        max_delay = new_max_delay
        controller = node

print('time:', time() - start)      # суммарное время, потребовавшееся на выполнение всех алгоритмов Дейкстры

prefix = 'tests/' + args.topology.split('/')[-1].replace('.gml', '')        # запишем в директорию ./tests выходные csv-файлы
write_csv_topology(prefix + '_topo.csv', net_edges)
write_csv_spanning_tree(prefix + '_routes.csv', min_delays, min_paths)

if args.vis:        # визуализация в случае необходимости
    tree = set()
    for b in min_branches.values():     # составим дерево из ребер всех найденных маршрутов от контроллера
        tree.update(b)

    visualize_network(net_edges, tree, controller)
