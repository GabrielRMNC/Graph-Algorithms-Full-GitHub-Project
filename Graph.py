import os
import time
import math
import heapq
from collections import deque

class Node:
    def __init__(self, label):
        self.label = label
        self.out_neighbors = set()
        self.in_neighbors = set()


class Graph:
    def __init__(self, directed=True, weighted=False):
        self._nodes = {}
        self._weights = {}  # Maps edge tuple (u, v) -> weight
        self._num_edges = 0
        self.directed = directed
        self.weighted = weighted

    def add_vertex(self, vertex_label):
        if vertex_label in self._nodes:
            raise ValueError(f"Vertex '{vertex_label}' already exists.")
        self._nodes[vertex_label] = Node(vertex_label)

    def add_edge(self, u, v, weight=0):
        if u not in self._nodes or v not in self._nodes:
            raise ValueError("Both vertices must exist.")
        if u == v:
            return

        u_node = self._nodes[u]
        v_node = self._nodes[v]

        edge_weight = weight if self.weighted else None

        if v not in u_node.out_neighbors:
            u_node.out_neighbors.add(v)
            v_node.in_neighbors.add(u)
            if self.weighted:
                self._weights[(u, v)] = edge_weight

            if not self.directed:
                v_node.out_neighbors.add(u)
                u_node.in_neighbors.add(v)
                if self.weighted:
                    self._weights[(v, u)] = edge_weight

            self._num_edges += 1

    def remove_edge(self, u, v):
        if u in self._nodes and v in self._nodes[u].out_neighbors:
            self._nodes[u].out_neighbors.remove(v)
            self._nodes[v].in_neighbors.remove(u)
            if (u, v) in self._weights:
                del self._weights[(u, v)]

            if not self.directed:
                self._nodes[v].out_neighbors.remove(u)
                self._nodes[u].in_neighbors.remove(v)
                if (v, u) in self._weights:
                    del self._weights[(v, u)]

            self._num_edges -= 1

    def remove_vertex(self, label):
        if label not in self._nodes:
            raise ValueError("Vertex does not exist.")

        node = self._nodes[label]

        for target in list(node.out_neighbors):
            self.remove_edge(label, target)
        for source in list(node.in_neighbors):
            self.remove_edge(source, label)

        del self._nodes[label]

    def set_weight(self, u, v, weight):
        if not self.weighted:
            raise ValueError("Graph is unweighted.")
        if u in self._nodes and v in self._nodes[u].out_neighbors:
            self._weights[(u, v)] = weight
            if not self.directed:
                self._weights[(v, u)] = weight
        else:
            raise ValueError("Edge does not exist.")

    def get_weight(self, u, v):
        if not self.weighted:
            raise ValueError("Graph is unweighted.")
        if u in self._nodes and v in self._nodes[u].out_neighbors:
            return self._weights[(u, v)]
        raise ValueError("Edge does not exist.")

    def change_if_directed(self, directed):
        if self.directed == directed: return
        self.directed = directed

        if not directed:  # Directed to Undirected
            for u in list(self._nodes.keys()):
                for v in list(self._nodes[u].out_neighbors):
                    if u not in self._nodes[v].out_neighbors:
                        self._nodes[v].out_neighbors.add(u)
                        self._nodes[u].in_neighbors.add(v)
                        if self.weighted:
                            self._weights[(v, u)] = self._weights.get((u, v), 0)
            self._num_edges = sum(len(n.out_neighbors) for n in self._nodes.values()) // 2
        else:  # Undirected to Directed
            self._num_edges = sum(len(n.out_neighbors) for n in self._nodes.values())

    def change_if_weighted(self, weighted):
        if self.weighted == weighted: return
        self.weighted = weighted

        if not weighted:
            self._weights.clear()
        else:
            for u in self._nodes.values():
                for v in u.out_neighbors:
                    self._weights[(u.label, v)] = 0

    def is_edge(self, u, v):
        if u not in self._nodes or v not in self._nodes: return False
        return v in self._nodes[u].out_neighbors

    def neighbors(self, label):
        if label not in self._nodes: raise ValueError("Vertex not found.")
        return list(self._nodes[label].out_neighbors)

    def inbound_neighbors(self, label):
        if label not in self._nodes: raise ValueError("Vertex not found.")
        return list(self._nodes[label].in_neighbors)

    def get_vertices(self):
        return list(self._nodes.keys())

    def get_e(self):
        return self._num_edges

    def get_v(self):
        return len(self._nodes)

    def __str__(self):
        dir_str = "directed" if self.directed else "undirected"
        weight_str = "weighted" if self.weighted else "unweighted"
        result = [f"{dir_str} {weight_str}"]

        printed_edges = set()
        for u, node in self._nodes.items():
            for v in node.out_neighbors:
                edge_id = tuple(sorted((u, v))) if not self.directed else (u, v)
                if edge_id not in printed_edges:
                    printed_edges.add(edge_id)
                    if self.weighted:
                        weight = self._weights.get((u, v), 0)
                        result.append(f"{u} {v} {weight}")
                    else:
                        result.append(f"{u} {v}")
            if not node.out_neighbors and not node.in_neighbors:
                result.append(str(u))
        return "\n".join(result)

    @classmethod
    def create_from_file(cls, filename):
        if not os.path.exists(filename): raise FileNotFoundError()
        with open(filename, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]

        if not lines: return cls()

        header = lines[0].split()
        is_dir = "undirected" not in header
        is_weight = "unweighted" not in header

        graph = cls(directed=is_dir, weighted=is_weight)

        for line in lines[1:]:
            parts = line.split()
            if len(parts) == 1:
                if parts[0] not in graph._nodes: graph.add_vertex(parts[0])
            elif len(parts) >= 2:
                u, v = parts[0], parts[1]
                if u not in graph._nodes: graph.add_vertex(u)
                if v not in graph._nodes: graph.add_vertex(v)
                w = float(parts[2]) if len(parts) == 3 and is_weight else 0
                graph.add_edge(u, v, weight=w)

        return graph


# --- ASSIGNMENT 3: ALGORITHMS & HELPERS ---

class PerformanceCounters:
    def __init__(self):
        self.cost_calls = 0
        self.pq_push = 0
        self.pq_pop = 0


def load_positions(filename):
    """Reads the vertex positions from the auxiliary CSV-like file."""
    positions = {}
    if not os.path.exists(filename):
        print(f"Warning: {filename} not found.")
        return positions

    with open(filename, 'r') as f:
        lines = f.readlines()
        for line in lines[1:]:  # Skip header
            parts = line.strip().split(',')
            if len(parts) == 3:
                positions[parts[0]] = (float(parts[1]), float(parts[2]))
    return positions


def heuristic(u, v, positions):
    """Euclidean distance heuristic for A*."""
    if u not in positions or v not in positions:
        return 0
    x1, y1 = positions[u]
    x2, y2 = positions[v]
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def a_star(graph, start, target, positions):
    """
    Time Complexity: O(E log V) in worst-case with a binary heap priority queue.
    Space Complexity: O(V) for tracking distances and parents.
    """
    counters = PerformanceCounters()
    pq = []

    # Priority Queue tuple format: (f_score, g_score, vertex_label)
    heapq.heappush(pq, (heuristic(start, target, positions), 0, start))
    counters.pq_push += 1

    dist = {start: 0}
    parent = {start: None}

    start_time = time.perf_counter()
    found = False

    while pq:
        f, g, current = heapq.heappop(pq)
        counters.pq_pop += 1

        # Stop early once we find the terminal vertex.
        if current == target:
            found = True
            break

        # Ignore outdated entries in the priority queue
        if g > dist.get(current, float('inf')):
            continue

        for neighbor in graph.neighbors(current):
            counters.cost_calls += 1
            cost = graph.get_weight(current, neighbor)
            tentative_g = dist[current] + cost

            if tentative_g < dist.get(neighbor, float('inf')):
                dist[neighbor] = tentative_g
                parent[neighbor] = current
                f_score = tentative_g + heuristic(neighbor, target, positions)

                heapq.heappush(pq, (f_score, tentative_g, neighbor))
                counters.pq_push += 1

    end_time = time.perf_counter()

    # Reconstruct path
    path = []
    if found or target in parent:
        curr = target
        while curr is not None:
            path.append(curr)
            curr = parent.get(curr)
        path.reverse()

    return {
        'cost': dist.get(target, float('inf')),
        'path': path,
        'time_ms': (end_time - start_time) * 1000,
        'counters': counters
    }


def bellman_ford(graph, start, target):
    """
    Time Complexity: O(V * E)
    Space Complexity: O(V) tracking distances and parents.
    """
    counters = PerformanceCounters()
    dist = {v: float('inf') for v in graph.get_vertices()}
    dist[start] = 0
    parent = {start: None}

    start_time = time.perf_counter()
    V = graph.get_v()

    for i in range(V - 1):
        any_changes = False
        for u in graph.get_vertices():
            if dist[u] == float('inf'): continue
            for v in graph.neighbors(u):
                counters.cost_calls += 1
                cost = graph.get_weight(u, v)

                if dist[u] + cost < dist[v]:
                    dist[v] = dist[u] + cost
                    parent[v] = u
                    any_changes = True

        # Standard early stop if no edges were relaxed in this pass.
        if not any_changes:
            break

        # (Optional) Literal translation of Assignment Problem 10 requirement:
        # "For both algorithms stop early once you find the terminal vertex."
        # If your instructor literally meant to break loop when target is found:
        # if dist[target] != float('inf'):
        #    break
        # Note: Uncommenting the above lines breaks standard Bellman-Ford paths!

    end_time = time.perf_counter()

    # Reconstruct path
    path = []
    if dist[target] != float('inf'):
        curr = target
        while curr is not None:
            path.append(curr)
            curr = parent.get(curr)
        path.reverse()

    return {
        'cost': dist.get(target, float('inf')),
        'path': path,
        'time_ms': (end_time - start_time) * 1000,
        'counters': counters
    }


# --- ITERATORS ---
# (Keeping your original iterators)
class BFS_iter:
    def __init__(self, graph, start_vertex):
        self.graph = graph
        self.start_vertex = start_vertex
        self.first()

    def first(self):
        if self.start_vertex not in self.graph.get_vertices():
            raise ValueError("Start vertex not found.")
        self.queue = [self.start_vertex]
        self.visited = {self.start_vertex}
        self.parent = {self.start_vertex: None}
        self.distance = {self.start_vertex: 0}
        self.current = self.start_vertex
        self._prepare_next()

    def _prepare_next(self):
        self.queue.pop(0)
        for neighbor in self.graph.neighbors(self.current):
            if neighbor not in self.visited:
                self.visited.add(neighbor)
                self.parent[neighbor] = self.current
                self.distance[neighbor] = self.distance[self.current] + 1
                self.queue.append(neighbor)

    def get_current(self):
        if not self.valid(): raise ValueError("Iterator is invalid.")
        return self.current

    def next(self):
        if not self.valid(): raise ValueError("Iterator is invalid.")
        if not self.queue:
            self.current = None
            return
        self.current = self.queue[0]
        self._prepare_next()

    def valid(self):
        return self.current is not None

    def get_path_length(self):
        if not self.valid(): raise ValueError("Iterator is invalid.")
        path = []
        curr = self.current
        while curr is not None:
            path.append(curr)
            curr = self.parent[curr]
        path.reverse()
        return self.distance[self.current], path


class DFS_iter:
    def __init__(self, graph, start_vertex):
        self.graph = graph
        self.start_vertex = start_vertex
        self.first()

    def first(self):
        if self.start_vertex not in self.graph.get_vertices():
            raise ValueError("Start vertex not found.")
        self.stack = [self.start_vertex]
        self.visited = {self.start_vertex}
        self.parent = {self.start_vertex: None}
        self.distance = {self.start_vertex: 0}
        self.current = self.start_vertex
        self._prepare_next()

    def _prepare_next(self):
        self.stack.pop()
        for neighbor in reversed(self.graph.neighbors(self.current)):
            if neighbor not in self.visited:
                self.visited.add(neighbor)
                self.parent[neighbor] = self.current
                self.distance[neighbor] = self.distance[self.current] + 1
                self.stack.append(neighbor)

    def get_current(self):
        if not self.valid(): raise ValueError("Iterator is invalid.")
        return self.current

    def next(self):
        if not self.valid(): raise ValueError("Iterator is invalid.")
        if not self.stack:
            self.current = None
            return
        self.current = self.stack[-1]
        self._prepare_next()

    def valid(self):
        return self.current is not None

    def get_path_length(self):
        if not self.valid(): raise ValueError("Iterator is invalid.")
        path = []
        curr = self.current
        while curr is not None:
            path.append(curr)
            curr = self.parent[curr]
        path.reverse()
        return self.distance[self.current], path


class DSU:
    """
    Disjoint Set Union (Union-Find) data structure to detect cycles
    during Kruskal's Algorithm.

    Space Complexity: O(V) where V is the number of vertices,
                      since we store parent and rank dictionaries for each vertex.
    """

    def __init__(self, vertices):
        """
        Time Complexity: O(V) to initialize the sets.
        """
        self.parent = {v: v for v in vertices}
        self.rank = {v: 0 for v in vertices}

    def find(self, item):
        """
        Finds the representative of the set that 'item' belongs to.
        Uses path compression to flatten the structure of the tree.

        Time Complexity: Amortized O(α(V)), where α is the Inverse Ackermann function.
                         For all practical purposes, this operates in O(1) time.
        """
        if self.parent[item] == item:
            return item
        self.parent[item] = self.find(self.parent[item])
        return self.parent[item]

    def union(self, set1, set2):
        """
        Unions two sets based on their rank.

        Time Complexity: Amortized O(α(V)), effectively O(1).
        """
        root1 = self.find(set1)
        root2 = self.find(set2)

        if root1 != root2:
            # Union by rank keeps the tree shallow
            if self.rank[root1] > self.rank[root2]:
                self.parent[root2] = root1
            elif self.rank[root1] < self.rank[root2]:
                self.parent[root1] = root2
            else:
                self.parent[root2] = root1
                self.rank[root1] += 1
            return True
        return False


def kruskal_mst(graph):
    """
    Constructs a minimal spanning tree of the graph using Kruskal's algorithm.
    Returns the MST (as a new Graph object) and the total cost.

    Time Complexity:
        - Extracting edges: O(V + E)
        - Sorting edges: O(E log E)
        - DSU operations (Find/Union): O(E * α(V))
        - Overall Time Complexity: O(E log E) or O(E log V) since E <= V^2

    Space Complexity: O(V + E) for storing the edges list, the DSU structure,
                      and the resulting MST graph.
    """
    if graph.directed:
        raise ValueError("Graph must be undirected to find an MST.")

    edges = []
    visited_edges = set()

    # Extract all edges from the graph
    for u in graph.get_vertices():
        for v in graph.neighbors(u):
            # Use sorted tuple to ensure we don't process undirected edges twice
            edge_id = tuple(sorted((u, v)))
            if edge_id not in visited_edges:
                visited_edges.add(edge_id)
                weight = graph.get_weight(u, v) if graph.weighted else 1
                edges.append((weight, u, v))

    # Sort edges by weight in ascending order
    edges.sort(key=lambda x: x[0])

    dsu = DSU(graph.get_vertices())
    mst = Graph(directed=False, weighted=graph.weighted)

    # Add all vertices to the MST
    for v in graph.get_vertices():
        mst.add_vertex(v)

    mst_cost = 0

    # Process edges and add them if they don't form a cycle
    for weight, u, v in edges:
        if dsu.union(u, v):
            mst.add_edge(u, v, weight=weight)
            mst_cost += weight

    return mst, mst_cost


def get_tree_height(tree, root):
    """
    Finds the height of a tree for a given root using BFS.

    Time Complexity: O(V + E) where V is the number of vertices and E is the number of edges.
                     Since it's a tree, E = V - 1, making the strictly bounded time O(V).

    Space Complexity: O(V) to store the BFS queue and the visited set in the worst-case.
    """
    if root not in tree.get_vertices():
        raise ValueError(f"Root vertex '{root}' not found in the tree.")

    # BFS queue stores tuples of (current_vertex, current_depth)
    queue = deque([(root, 0)])
    visited = {root}
    max_depth = 0

    while queue:
        current, depth = queue.popleft()

        # Update the maximum depth found so far
        if depth > max_depth:
            max_depth = depth

        for neighbor in tree.neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, depth + 1))

    return max_depth

# --- INTERACTIVE CLI MENU ---

def run_test_menu():
    graph = Graph()

    while True:
        print("\n" + "=" * 30)
        print(f" GRAPH MENU | Directed: {graph.directed} | Weighted: {graph.weighted}")
        print("=" * 30)
        print("1. Add Vertex")
        print("2. Add Edge")
        print("3. Remove Vertex / Edge")
        print("4. Toggle Directed/Undirected")
        print("5. Toggle Weighted/Unweighted")
        print("6. Set/Get Edge Weight")
        print("7. Print Graph Format")
        print("8. Run BFS Traversal")
        print("9. Run DFS Traversal")
        print("10. Load Graph from File")
        print("11. Run Assignment 3 Problem 10 (Bellman-Ford & A*)")
        print("12. Run Assignment 4 Problem 4 (minimal spanning tree of the graph using Kruskal's algorithm + height of the tree for a given root, in O(e+v))")
        print("0. Exit")

        choice = input("\nSelect an operation: ")

        try:
            if choice == '1':
                v = input("Enter vertex label: ")
                graph.add_vertex(v)
                print("Vertex added.")

            elif choice == '2':
                u = input("Initial vertex: ")
                v = input("Terminal vertex: ")
                w = 0
                if graph.weighted:
                    w = float(input("Enter weight: "))
                graph.add_edge(u, v, weight=w)
                print("Edge added.")

            elif choice == '3':
                sub = input("Remove (v)ertex or (e)dge? ").lower()
                if sub == 'v':
                    graph.remove_vertex(input("Vertex label: "))
                    print("Vertex removed.")
                elif sub == 'e':
                    graph.remove_edge(input("Initial vertex: "), input("Terminal vertex: "))
                    print("Edge removed.")

            elif choice == '4':
                is_dir = input("Make directed? (y/n): ").lower() == 'y'
                graph.change_if_directed(is_dir)
                print("Direction state updated.")

            elif choice == '5':
                is_weight = input("Make weighted? (y/n): ").lower() == 'y'
                graph.change_if_weighted(is_weight)
                print("Weight state updated.")

            elif choice == '6':
                u = input("Initial vertex: ")
                v = input("Terminal vertex: ")
                action = input("(s)et or (g)et weight? ").lower()
                if action == 's':
                    w = float(input("Enter new weight: "))
                    graph.set_weight(u, v, w)
                    print("Weight updated.")
                else:
                    print(f"Weight is: {graph.get_weight(u, v)}")

            elif choice == '7':
                print("\n--- Graph Output ---")
                print(graph)

            elif choice in ['8', '9']:
                start = input("Enter starting vertex: ")
                iterator = BFS_iter(graph, start) if choice == '8' else DFS_iter(graph, start)
                print(f"\n--- {'BFS' if choice == '8' else 'DFS'} Traversal ---")
                while iterator.valid():
                    curr = iterator.get_current()
                    dist, path = iterator.get_path_length()
                    print(f"Visited: {curr} | Distance: {dist} | Path: {' -> '.join(path)}")
                    iterator.next()

            elif choice == '10':
                filename = input("Enter filename (e.g., positives_1_v10_e40.txt): ")
                graph = Graph.create_from_file(filename)
                print(f"Graph loaded successfully. {graph.get_v()} vertices, {graph.get_e()} edges.")

            elif choice == '11':
                if not graph.get_vertices():
                    print("Please load a graph using Option 10 first.")
                    continue

                start = input("Enter starting vertex (e.g., '1'): ")
                target = input("Enter terminal vertex (e.g., '10'): ")
                pos_file = input("Enter positions filename (e.g., positives_1_vertex_positions.txt): ")

                positions = load_positions(pos_file)

                print(f"\nMinimum cost walk {start} to {target}:")

                # Run the two algorithms
                res_astar = a_star(graph, start, target, positions)
                res_bf = bellman_ford(graph, start, target)

                # Format printing
                print(
                    f"A*: time: {res_astar['time_ms']:.2f}ms, cost: {res_astar['cost']}, path: {', '.join(map(str, res_astar['path']))}")
                print(
                    f"Bellman-Ford: time: {res_bf['time_ms']:.2f}ms, cost: {res_bf['cost']}, path: {', '.join(map(str, res_bf['path']))}")

                print("\nComparison:")
                print(f"{'':<15} {'g.cost':<10} {'pq.push':<10} {'pq.pop':<10}")
                print(
                    f"{'A*':<15} {res_astar['counters'].cost_calls:<10} {res_astar['counters'].pq_push:<10} {res_astar['counters'].pq_pop:<10}")
                print(f"{'Bellman-Ford':<15} {res_bf['counters'].cost_calls:<10} {'N/A':<10} {'N/A':<10}")

            elif choice == '12':
                if not graph.get_vertices():
                    print("Please load or create a graph first.")
                    continue
                if graph.directed:
                    print("Please convert the graph to undirected (Option 4) first.")
                    continue

                print("\n--- Assignment 4: Kruskal's MST & Tree Height ---")
                try:
                    mst, total_cost = kruskal_mst(graph)
                    print(f"MST computed successfully. Total Cost: {total_cost}")
                    print(f"MST Edges: {mst.get_e()} | MST Vertices: {mst.get_v()}")

                    root = input("Enter root vertex to calculate tree height: ")
                    height = get_tree_height(mst, root)
                    print(f"The height of the tree from root '{root}' is: {height}")
                except Exception as e:
                    print(f"Error executing Assignment 4: {e}")

            elif choice == '0':
                print("Exiting test menu.")
                break

            else:
                print("Invalid choice.")

        except Exception as e:
            print(f"ERROR: {e}")


if __name__ == "__main__":
    run_test_menu()