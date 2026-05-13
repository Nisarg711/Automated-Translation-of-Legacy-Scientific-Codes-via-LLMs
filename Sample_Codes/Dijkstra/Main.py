import sys

def dijkstra(graph, start):
    # Create a distance array and initialize it with infinity
    distances = [sys.maxsize] * len(graph)
    distances[start] = 0  # Distance to the start node is 0

    # Create a visited array to keep track of visited nodes
    visited = [False] * len(graph)

    # Iterate over all nodes
    for _ in range(len(graph)):
        # Find the unvisited node with the minimum distance
        min_distance = sys.maxsize
        min_index = -1
        for i in range(len(graph)):
            if not visited[i] and distances[i] < min_distance:
                min_distance = distances[i]
                min_index = i

        # Mark the node as visited
        visited[min_index] = True

        # Update distances of neighboring nodes
        for i in range(len(graph)):
            if (not visited[i] and graph[min_index][i] > 0 and
                    distances[min_index] + graph[min_index][i] < distances[i]):
                distances[i] = distances[min_index] + graph[min_index][i]

    # Return the distances
    return distances


# Read input
num_nodes = int(input())
graph = [[int(x) for x in input().split()] for _ in range(num_nodes)]
start_node = int(input())

# Run Dijkstra's algorithm
distances = dijkstra(graph, start_node)

# Print output
for i in range(len(distances)):
    print(f"{i} {distances[i]}")