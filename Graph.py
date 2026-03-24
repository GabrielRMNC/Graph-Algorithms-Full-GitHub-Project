import os


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
        """Adds an edge. Weight is optional, default 0 if weighted[cite: 65]."""
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
        """Sets the weight for an edge. Raises error if not weighted[cite: 63, 64]."""
        if not self.weighted:
            raise ValueError("Graph is unweighted.")
        if u in self._nodes and v in self._nodes[u].out_neighbors:
            self._weights[(u, v)] = weight
            if not self.directed:
                self._weights[(v, u)] = weight
        else:
            raise ValueError("Edge does not exist.")

    def get_weight(self, u, v):
        """Returns edge weight. Raises exception if missing or unweighted[cite: 67, 68]."""
        if not self.weighted:
            raise ValueError("Graph is unweighted.")
        if u in self._nodes and v in self._nodes[u].out_neighbors:
            return self._weights[(u, v)]
        raise ValueError("Edge does not exist.")

    def change_if_directed(self, directed):
        """Changes directed state[cite: 55]."""
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
        """Changes weighted state. Resets to 0 or removes weights[cite: 60, 61, 62]."""
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
        """Prints graph properties correctly on the first line[cite: 54, 66]."""
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
        """Creates a graph with data read from a file[cite: 86]."""
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


# --- ITERATORS ---

class BFS_iter:
    def __init__(self, graph, start_vertex):
        """BFS Iterator running in O(e)[cite: 80]."""
        self.graph = graph
        self.start_vertex = start_vertex
        self.first()

    def first(self):
        """Sets the iterator on the first vertex[cite: 72]."""
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
        """Returns current vertex. Raises error if invalid[cite: 72, 73]."""
        if not self.valid(): raise ValueError("Iterator is invalid.")
        return self.current

    def next(self):
        """Goes to the next vertex[cite: 74]."""
        if not self.valid(): raise ValueError("Iterator is invalid.")
        if not self.queue:
            self.current = None
            return
        self.current = self.queue[0]
        self._prepare_next()

    def valid(self):
        """Returns True if the iterator is valid[cite: 75]."""
        return self.current is not None

    def get_path_length(self):
        """Returns the path length and path from the initial vertex[cite: 81, 84]."""
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
                filename = input("Enter filename (e.g., graph.txt): ")
                graph = Graph.create_from_file(filename)
                print(f"Graph loaded successfully. {graph.get_v()} vertices, {graph.get_e()} edges.")

            elif choice == '0':
                print("Exiting test menu.")
                break

            else:
                print("Invalid choice.")

        except Exception as e:
            print(f"ERROR: {e}")


if __name__ == "__main__":
    run_test_menu()