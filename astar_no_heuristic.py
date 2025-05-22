import heapq
import numpy as np

class AStarPathfinderNoHeuristic:
    def __init__(self, grid):
        self.grid = grid
        self.rows, self.cols = grid.shape

    def heuristic(self, a, b):
        # No heuristic — always returns 0
        return 0

    def get_neighbors(self, node):
        directions = [(0, 1), (1, 0), (-1, 0), (0, -1)]
        neighbors = []

        for dx, dy in directions:
            x, y = node[0] + dx, node[1] + dy
            if 0 <= x < self.rows and 0 <= y < self.cols:
                neighbors.append((x, y))
        return neighbors

    def find_path(self, start, goal):
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == goal:
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                return path

            for neighbor in self.get_neighbors(current):
                tentative = g_score[current] + 1
                if neighbor not in g_score or tentative < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative
                    f = tentative + self.heuristic(neighbor, goal)  # heuristic always 0
                    heapq.heappush(open_set, (f, neighbor))

        return []  # No path found
