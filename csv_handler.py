import csv

def write_csv_topology(filename, net_edges):
    net_edges = sorted(net_edges, key = lambda x: (x.src, x.tgt))

    with open(filename, mode='w') as file:
        fdnms = ['Node 1 (id)', 'Node 1 (label)', 'Node 1 (longitude)', 'Node 1 (latitude)',
                 'Node 2 (id)', 'Node 2 (label)', 'Node 2 (longitude)', 'Node 2 (latitude)',
                 'Distance (km)', 'Delay (mks)']
        writer = csv.writer(file)
        writer.writerow(fdnms)

        writer = csv.DictWriter(file, fieldnames=fdnms)

        none_val = lambda v: '<hyperedge>' if v is None else v
        for edge in net_edges:
            row = {
                fdnms[0]: edge.src,
                fdnms[1]: edge.src_node.label,
                fdnms[2]: edge.src_node.lon,
                fdnms[3]: edge.src_node.lat,
                fdnms[4]: edge.tgt,
                fdnms[5]: edge.tgt_node.label,
                fdnms[6]: edge.tgt_node.lon,
                fdnms[7]: edge.tgt_node.lat,
                fdnms[8]: edge.distance,
                fdnms[9]: edge.delay
            }
            row = {k: none_val(row[k]) for k in row.keys()}
            writer.writerow(row)

def write_csv_spanning_tree(filename, delays, paths):
    delays = dict(sorted(delays.items()))

    with open(filename, mode='w') as file:
        fdnms = ['Node 1 (id)', 'Node 2 (id)', 'Path', 'Delay (mks)']
        writer = csv.writer(file)
        writer.writerow(fdnms)

        writer = csv.DictWriter(file, fieldnames=fdnms)

        for id in delays.keys():
            writer.writerow({
                fdnms[0]: paths[id][0],
                fdnms[1]: id,
                fdnms[2]: paths[id],
                fdnms[3]: delays[id]
            })