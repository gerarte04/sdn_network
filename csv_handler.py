import csv

def write_csv_topology(filename, net_edges):
    def getattr_source(edge, attr):
        try:
            return getattr(edge.gml_edge.source_node, attr)
        except AttributeError:
            return '-'
        
    def getattr_target(edge, attr):
        try:
            return getattr(edge.gml_edge.target_node, attr)
        except AttributeError:
            return '-'
        
    net_edges = sorted(net_edges, key = lambda x: (x.gml_edge.source, x.gml_edge.target))

    with open(filename, mode='w') as file:
        fdnms = ['Node 1 (id)', 'Node 1 (label)', 'Node 1 (longitude)', 'Node 1 (latitude)',
                 'Node 2 (id)', 'Node 2 (label)', 'Node 2 (longitude)', 'Node 2 (latitude)',
                 'Distance (km)', 'Delay (mks)']
        writer = csv.writer(file)
        writer.writerow(fdnms)

        writer = csv.DictWriter(file, fieldnames=fdnms)

        for edge in net_edges:
            writer.writerow({
                fdnms[0]: edge.gml_edge.source,
                fdnms[1]: getattr_source(edge, 'label'),
                fdnms[2]: getattr_source(edge, 'Longitude'),
                fdnms[3]: getattr_source(edge, 'Latitude'),
                fdnms[4]: edge.gml_edge.target,
                fdnms[5]: getattr_target(edge, 'label'),
                fdnms[6]: getattr_target(edge, 'Longitude'),
                fdnms[7]: getattr_target(edge, 'Latitude'),
                fdnms[8]: edge.distance if edge.distance is not None else '-',
                fdnms[9]: edge.delay if edge.delay is not None else '-'
            })