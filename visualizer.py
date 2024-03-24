import matplotlib.pyplot as plt
import math

def visualize_network(net_edges, tree, controller):
    REL_TOL = 1e-6
    drown = {}      # список названий узлов

    def draw_edge(edge, color):
        x = (edge.src_node.lon, edge.tgt_node.lon)
        y = (edge.src_node.lat, edge.tgt_node.lat)

        labels = [edge.src_node.__repr__(), edge.tgt_node.__repr__()]
        found = [False, False]
        for c in drown.keys():      # если существует несколько узлов с одной геолокацией, то их названия отображаются через запятую
            for i in range(2):
                if math.isclose(c[0], x[i], rel_tol=REL_TOL) and math.isclose(c[1], y[i], rel_tol=REL_TOL):
                    if not labels[i] in drown[c]:
                        drown[c] += ', ' + labels[i]
                    found[i] = True

        for i in range(2):
            if not found[i]:
                drown[(x[i], y[i])] = labels[i]

        plt.plot(x, y, lw=2, marker='o', color=color, mfc='White', mec='Black', mew='1.3')      # само ребро
        plt.text((x[0] + x[1]) / 2, (y[0] + y[1]) / 2, edge.delay, fontsize=9, fontstyle='italic')                  # задержка соединения

    not_in_tree = list(filter(lambda e: e not in tree, net_edges))
    for edge in not_in_tree:            # сначала отобразим ребра, не принадлежащие дереву, зеленым цветом
        draw_edge(edge, 'Green')
    for edge in tree:                   # затем принадлежащие красным
        draw_edge(edge, 'Red')

    plt.plot((controller.lon, controller.lon), (controller.lat, controller.lat),    # отобразим контроллер
             marker='o', markersize=8, mfc='Yellow', mec='Red', mew='2')

    for c in drown.keys():              # отобразим все названия узлов
        plt.text(c[0], c[1], drown[c])

    plt.axis('off')
    plt.show()
