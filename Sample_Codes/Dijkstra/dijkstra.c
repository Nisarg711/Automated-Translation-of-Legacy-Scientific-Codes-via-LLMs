#include <stdio.h>
#include <limits.h>
#define MAX_V 100

int minDistance(int dist[], int visited[], int V) {
    int min = INT_MAX, min_index = 0;

    for (int v = 0; v < V; v++) {
        if (!visited[v] && dist[v] <= min) {
            min = dist[v];
            min_index = v;
        }
    }
    return min_index;
}

void dijkstra(int graph[MAX_V][MAX_V], int src, int V) {
    int dist[MAX_V];
    int visited[MAX_V] = {0};

    for (int i = 0; i < V; i++)
        dist[i] = INT_MAX;

    dist[src] = 0;

    for (int count = 0; count < V - 1; count++) {
        int u = minDistance(dist, visited, V);
        visited[u] = 1;

        for (int v = 0; v < V; v++) {
            if (!visited[v] && graph[u][v] &&
                dist[u] != INT_MAX &&
                dist[u] + graph[u][v] < dist[v]) {

                dist[v] = dist[u] + graph[u][v];
            }
        }
    }

    for (int i = 0; i < V; i++) {
        if (dist[i] == INT_MAX)
            printf("%d INF\n", i);
        else
            printf("%d %d\n", i, dist[i]);
    }
}

int main() {
    int V;
    scanf("%d", &V);
    
    int graph[MAX_V][MAX_V];
    for (int i = 0; i < V; i++) {
        for (int j = 0; j < V; j++) {
            scanf("%d", &graph[i][j]);
        }
    }
    
    int src;
    scanf("%d", &src);

    dijkstra(graph, src, V);
    return 0;
}
