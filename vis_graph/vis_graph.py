"""
The MIT License (MIT)

Copyright (c) 2016 Christian August Reksten-Monsen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from collections import defaultdict
from graph import Graph, Point, Edge
from visible_vertices import visible_vertices
from timeit import default_timer
import sys
from multiprocessing import Pool

# TODO: refector so only one object to call
# TODO: build the obstacle graph on various inputs, list of polys,
# shapefile (given index points where coordinates are)
def vis_graph(graph, origin=None, destination=None, workers=2):
    visibility_graph = Graph([])
    points = graph.get_points()
    n = int(len(points) / workers)
    batches = [(graph, points[i:i + n], origin, destination) for i in xrange(0, len(points), n)]
    pool = Pool(workers)
    result = pool.map_async(vis_graph_worker_wrap, batches)
    for job in result.get():
        for edge in job:
            visibility_graph.add_edge(edge)
    return visibility_graph

def vis_graph_worker_wrap(args):
    return vis_graph_worker(*args)

# TODO: keep vis_graph as it was, then make a separate worker and processing
# function.
def vis_graph_worker(graph, points, origin=None, destination=None):
    time_elapsed = 0
    total_points = len(points)
    points_done = 0
    visible_edges = []
    for i, p1 in enumerate(points):
        t0 = default_timer()
        for p2 in visible_vertices(p1, graph, origin, destination, 'half'):
            visible_edges.append(Edge(p1, p2))
        t1 = default_timer()

        time_elapsed += t1 - t0
        points_done += 1
        avg_time = time_elapsed / points_done
        rem_time = avg_time * (total_points - points_done)
        time_stat = (points_done, rem_time, avg_time, time_elapsed)
        status = 'Points completed: %d time[remaining: %f, avg: %f, elapsed: %f]        \r'%time_stat
        sys.stdout.write(status)
        sys.stdout.flush()
    sys.stdout.write('\n')
    sys.stdout.flush()
    return visible_edges
