import matplotlib.pyplot as plt

def visualize_network(net_edges, tree):
    def draw_edge(edge, color):
        x = [edge.src_node.lon, edge.tgt_node.lon]
        y = [edge.src_node.lat, edge.tgt_node.lat]

        plt.plot(x, y, lw=2, marker = 'o', color=color, mfc='White', mec='Black', mew='1.3')
        plt.text(x[0], y[0], edge.src_node.__repr__())
        plt.text(x[1], y[1], edge.tgt_node.__repr__())

    not_in_tree = list(filter(lambda e: e not in tree, net_edges))
    for edge in not_in_tree:
        draw_edge(edge, 'Green')
    for edge in tree:
        draw_edge(edge, 'Red')

    plt.axis('off')
    plt.show()
