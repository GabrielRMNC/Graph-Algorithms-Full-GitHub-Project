class Node:

    def __init__(self, label):
        self.label = label
        self.out_neighbors = set()
        self.in_neighbors = set()


class DirectedGraph:
    def __init__(self):
        """
        Time Complexity: O(1)
        """
        self._nodes = {}
        self._num_edges = 0

    def add_vertex(self, vertex_label):
        """
        Time Complexity: O(1) average
        """
        if vertex_label in self._nodes:
            raise ValueError(f"Vertex '{vertex_label}' already exists.")

        self._nodes[vertex_label] = Node(vertex_label)

    def add_edge(self, initial_vertex, terminal_vertex):
        """
        Time Complexity: O(1) average
        """
        if initial_vertex not in self._nodes or terminal_vertex not in self._nodes:
            raise ValueError("Both vertices must exist in the graph.")

        if initial_vertex == terminal_vertex:
            return  # Simple graph: no self loops allowed [cite: 4]

        init_node = self._nodes[initial_vertex]
        term_node = self._nodes[terminal_vertex]


        if terminal_vertex not in init_node.out_neighbors:

            init_node.out_neighbors.add(terminal_vertex)
            term_node.in_neighbors.add(initial_vertex)
            self._num_edges += 1

    def remove_edge(self, initial_vertex, terminal_vertex):
        """
        Time Complexity: O(1) average
        """
        if initial_vertex in self._nodes and terminal_vertex in self._nodes:
            init_node = self._nodes[initial_vertex]
            term_node = self._nodes[terminal_vertex]

            if terminal_vertex in init_node.out_neighbors:
                init_node.out_neighbors.remove(terminal_vertex)
                term_node.in_neighbors.remove(initial_vertex)
                self._num_edges -= 1

    def remove_vertex(self, vertex_label):
        """
        Time Complexity: O(out_degree + in_degree) average
        """
        if vertex_label not in self._nodes:
            raise ValueError(f"Vertex '{vertex_label}' does not exist.")

        node_to_remove = self._nodes[vertex_label]

        for target_label in node_to_remove.out_neighbors:
            self._nodes[target_label].in_neighbors.remove(vertex_label)
            self._num_edges -= 1

        for source_label in node_to_remove.in_neighbors:
            self._nodes[source_label].out_neighbors.remove(vertex_label)
            self._num_edges -= 1

        del self._nodes[vertex_label]

    def get_v(self):
        """
        Time Complexity: O(1)
        """
        return len(self._nodes)

    def get_e(self):
        """
        Time Complexity: O(1)
        """
        return self._num_edges

    def is_edge(self, initial_vertex, terminal_vertex):
        """
        Time Complexity: O(1) average
        """
        if initial_vertex not in self._nodes or terminal_vertex not in self._nodes:
            return False
        return terminal_vertex in self._nodes[initial_vertex].out_neighbors

    def neighbors(self, vertex_label):
        """
        Time Complexity: O(out_degree)
        """
        if vertex_label not in self._nodes:
            raise ValueError(f"Vertex '{vertex_label}' is not in the graph.")
        return list(self._nodes[vertex_label].out_neighbors)

    def inbound_neighbors(self, vertex_label):
        """
        Time Complexity: O(in_degree)
        """
        if vertex_label not in self._nodes:
            raise ValueError(f"Vertex '{vertex_label}' is not in the graph.")
        return list(self._nodes[vertex_label].in_neighbors)

    def get_vertices(self):
        """
        Time Complexity: O(V)
        """
        return list(self._nodes.keys())

    def get_edges(self):
        """
        Time Complexity: O(V + E)
        """
        edges = []
        for label, node in self._nodes.items():
            for target in node.out_neighbors:
                edges.append((label, target))
        return edges

    def __str__(self):
        """
        Time Complexity: O(V + E)
        """
        result = ["directed unweighted"]

        for label, node in self._nodes.items():
            for target in node.out_neighbors:
                result.append(f"{label} {target}")

            if len(node.out_neighbors) == 0 and len(node.in_neighbors) == 0:
                result.append(str(label))

        return "\n".join(result)


def run_test_menu():

    graph = DirectedGraph()

    while True:
        print("\n--- Directed Graph Test Menu ---")
        print("1. Add Vertex")
        print("2. Add Edge")
        print("3. Remove Vertex")
        print("4. Remove Edge")
        print("5. Get Number of Vertices (get_v)")
        print("6. Get Number of Edges (get_e)")
        print("7. Check if Edge Exists (is_edge)")
        print("8. Get Outbound Neighbors (neighbors)")
        print("9. Get Inbound Neighbors (inbound_neighbors)")
        print("10. List All Vertices")
        print("11. List All Edges")
        print("12. Print Graph Format (for CS Academy)")
        print("0. Exit")

        choice = input("Select an operation (0-12): ")

        try:
            if choice == '1':
                v = input("Enter new vertex label: ")
                graph.add_vertex(v)
                print(f"Vertex '{v}' added.")

            elif choice == '2':
                u = input("Enter initial vertex: ")
                v = input("Enter terminal vertex: ")
                graph.add_edge(u, v)
                print(f"Edge ({u} -> {v}) added (if vertices exist and it's not a self-loop).")

            elif choice == '3':
                v = input("Enter vertex label to remove: ")
                graph.remove_vertex(v)
                print(f"Vertex '{v}' and its edges removed.")

            elif choice == '4':
                u = input("Enter initial vertex: ")
                v = input("Enter terminal vertex: ")
                graph.remove_edge(u, v)
                print(f"Edge ({u} -> {v}) removed (if it existed).")

            elif choice == '5':
                print(f"Total vertices: {graph.get_v()}")

            elif choice == '6':
                print(f"Total edges: {graph.get_e()}")

            elif choice == '7':
                u = input("Enter initial vertex: ")
                v = input("Enter terminal vertex: ")
                exists = graph.is_edge(u, v)
                print(f"Edge ({u} -> {v}) exists? {exists}")

            elif choice == '8':
                v = input("Enter vertex label: ")
                print(f"Outbound neighbors of '{v}': {graph.neighbors(v)}")

            elif choice == '9':
                v = input("Enter vertex label: ")
                print(f"Inbound neighbors of '{v}': {graph.inbound_neighbors(v)}")

            elif choice == '10':
                print(f"All Vertices: {graph.get_vertices()}")

            elif choice == '11':
                print(f"All Edges: {graph.get_edges()}")

            elif choice == '12':
                print("\n--- Graph String Output ---")
                print(graph)
                print("---------------------------")

            elif choice == '0':
                print("Exiting test menu.")
                break

            else:
                print("Invalid choice. Please enter a number between 0 and 12.")


        except ValueError as e:
            print(f"ERROR: {e}")


if __name__ == "__main__":
    run_test_menu()