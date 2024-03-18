import matplotlib.pyplot as plt
import matplotlib.patheffects as pe

def visualize_network(net_edges, tree):
    for edge in net_edges:
        if edge.distance is not None:
            x = [edge.src_node.lon, edge.tgt_node.lon]
            y = [edge.src_node.lat, edge.tgt_node.lat]

            color = 'Green'
            path_effects = None
            if edge in tree:
                color = 'Red'
            # if len(edge.hyperlink) > 0:
            #     path_effects=[pe.Stroke(linewidth=3.5, foreground='Blue'), pe.Normal()]
            plt.plot(x, y, lw=2, marker = 'o', path_effects=path_effects, color=color, mfc='White', mec='Black', mew='1.3')

            plt.text(x[0], y[0], edge.src_node.label + '(' + str(edge.src) + ')')
            plt.text(x[1], y[1], edge.tgt_node.label + '(' + str(edge.tgt) + ')')
    plt.axis('off')
    plt.show()