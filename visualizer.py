import matplotlib.pyplot as plt
import matplotlib.patheffects as pe

def visualize_network(net_edges, tree):
    def draw(src_node, tgt_node, color):
        path_effects = []
        x = [src_node.lon, tgt_node.lon]
        y = [src_node.lat, tgt_node.lat]
        # if len(edge.hyperlink) > 0:
        #     path_effects=[pe.Stroke(linewidth=3.5, foreground='Blue'), pe.Normal()]
        plt.plot(x, y, lw=2, marker = 'o', path_effects=path_effects, color=color, mfc='White', mec='Black', mew='1.3')

        plt.text(x[0], y[0], edge.src_node.label + '(' + str(edge.src) + ')')
        plt.text(x[1], y[1], edge.tgt_node.label + '(' + str(edge.tgt) + ')')
    hyperlinked = {}
    for edge in list(filter(lambda e: e not in tree, net_edges)) + tree:
        if edge.distance is not None:
            color = 'Green'
            if edge in tree:
                color = 'Red'
            draw(x, y, color)
        elif edge.src_node.lat is None:
            if edge.src in hyperlinked.keys():
        
    plt.axis('off')
    plt.show()