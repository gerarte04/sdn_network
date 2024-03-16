import matplotlib.pyplot as plt

def visualize_network(net_edges, tree):
    for edge in net_edges:
        if edge.distance is not None:
            x = [getattr(edge.gml_edge.source_node, 'Longitude'), getattr(edge.gml_edge.target_node, 'Longitude')]
            y = [getattr(edge.gml_edge.source_node, 'Latitude'), getattr(edge.gml_edge.target_node, 'Latitude')]
            color = 'Green'
            if edge in tree:
                color = 'Red'
            plt.plot(x, y, marker = 'o', color=color)
            plt.text(x[0], y[0], edge.gml_edge.source)
            plt.text(x[1], y[1], edge.gml_edge.target)
    plt.axis('off')
    plt.show()