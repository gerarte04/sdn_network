import matplotlib.pyplot as plt

def visualize_network(net_edges, tree, controller):
    def draw_edge(edge, color):
        x = (edge.src_node.lon, edge.tgt_node.lon)
        y = (edge.src_node.lat, edge.tgt_node.lat)

        plt.plot(x, y, lw=2, marker='o', color=color, mfc='White', mec='Black', mew='1.3')
        plt.text(x[0], y[0], edge.src_node.__repr__())
        plt.text(x[1], y[1], edge.tgt_node.__repr__())
        plt.text((x[0] + x[1]) / 2, (y[0] + y[1]) / 2, edge.delay, fontsize=9)

    not_in_tree = list(filter(lambda e: e not in tree, net_edges))
    for edge in not_in_tree:
        draw_edge(edge, 'Green')
    for edge in tree:
        draw_edge(edge, 'Red')

    plt.plot((controller.lon, controller.lon), (controller.lat, controller.lat),
             marker='o', markersize=8, mfc='Yellow', mec='Red', mew='2')

    plt.axis('off')
    plt.show()
