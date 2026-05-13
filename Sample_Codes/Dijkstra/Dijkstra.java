import java.util.Scanner;

public class Dijkstra {
    private static final int MAX_V = 100;
    private static final int INF = Integer.MAX_VALUE;

    /**
     * Finds the vertex with the minimum distance that has not been visited yet.
     * 
     * @param dist    array of distances from the source vertex to all other vertices
     * @param visited array indicating whether a vertex has been visited or not
     * @param V       number of vertices
     * @return index of the vertex with the minimum distance
     */
    private static int minDistance(int[] dist, boolean[] visited, int V) {
        int min = INF;
        int minIndex = -1;

        // Iterate over all vertices to find the one with the minimum distance
        for (int v = 0; v < V; v++) {
            if (!visited[v] && dist[v] <= min) {
                min = dist[v];
                minIndex = v;
            }
        }
        return minIndex;
    }

    /**
     * Implements Dijkstra's algorithm to find the shortest distances from the source vertex to all other vertices.
     * 
     * @param graph array representing the graph, where graph[i][j] is the weight of the edge from vertex i to vertex j
     * @param src   index of the source vertex
     * @param V     number of vertices
     */
    public static void dijkstra(int[][] graph, int src, int V) {
        int[] dist = new int[V];
        boolean[] visited = new boolean[V];

        // Initialize all distances to infinity and mark all vertices as unvisited
        for (int i = 0; i < V; i++) {
            dist[i] = INF;
        }

        // Distance from the source vertex to itself is 0
        dist[src] = 0;

        // Iterate over all vertices
        for (int count = 0; count < V - 1; count++) {
            int u = minDistance(dist, visited, V);
            visited[u] = true;

            // Update distances for all adjacent vertices
            for (int v = 0; v < V; v++) {
                if (!visited[v] && graph[u][v] > 0 && dist[u] != INF && dist[u] + graph[u][v] < dist[v]) {
                    dist[v] = dist[u] + graph[u][v];
                }
            }
        }

        // Print the shortest distances from the source vertex to all other vertices
        for (int i = 0; i < V; i++) {
            if (dist[i] == INF) {
                System.out.println(i + " INF");
            } else {
                System.out.println(i + " " + dist[i]);
            }
        }
    }

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        // Read the number of vertices
        int V = scanner.nextInt();

        // Read the graph
        int[][] graph = new int[MAX_V][MAX_V];
        for (int i = 0; i < V; i++) {
            for (int j = 0; j < V; j++) {
                graph[i][j] = scanner.nextInt();
            }
        }

        // Read the source vertex
        int src = scanner.nextInt();

        // Run Dijkstra's algorithm
        dijkstra(graph, src, V);

        scanner.close();
    }
}