import pygame
import random
import heapq

# Constants
WIDTH, HEIGHT = 600, 600
ROWS, COLS = 20, 20
CELL_SIZE = WIDTH // COLS

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)  # Player
GREEN = (0, 255, 0)  # AI Path
BLUE = (0, 0, 255)  # Exit

# Generate a perfect maze with a guaranteed path
def generate_maze(rows, cols):
    maze = [[1] * cols for _ in range(rows)]  # Start with walls
    
    def carve_maze(x, y):
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            nx, ny = x + dx * 2, y + dy * 2
            if 0 <= nx < rows and 0 <= ny < cols and maze[nx][ny] == 1:
                maze[nx - dx][ny - dy] = 0  # Open path
                maze[nx][ny] = 0
                carve_maze(nx, ny)

    # Start carving from (0,0)
    maze[0][0] = 0
    carve_maze(0, 0)

    # Ensure exit is reachable
    maze[rows-1][cols-1] = 0
    maze[rows-2][cols-1] = 0
    maze[rows-1][cols-2] = 0
    
    return maze

# A* Pathfinding Algorithm
class Node:
    def __init__(self, position, parent=None):
        self.position = position
        self.parent = parent
        self.g = 0
        self.h = 0
        self.f = 0

    def __lt__(self, other):
        return self.f < other.f

def astar(maze, start, end):
    open_list = []
    closed_list = set()
    
    start_node = Node(start)
    end_node = Node(end)
    
    heapq.heappush(open_list, start_node)
    
    while open_list:
        current_node = heapq.heappop(open_list)
        
        if current_node.position == end_node.position:
            path = []
            while current_node:
                path.append(current_node.position)
                current_node = current_node.parent
            return path[::-1]
        
        closed_list.add(current_node.position)
        
        for move in [(0, -1), (0, 1), (-1, 0), (1, 0)]:  # Up, Down, Left, Right
            node_pos = (current_node.position[0] + move[0], current_node.position[1] + move[1])
            
            if 0 <= node_pos[0] < len(maze) and 0 <= node_pos[1] < len(maze[0]) and maze[node_pos[0]][node_pos[1]] == 0:
                if node_pos in closed_list:
                    continue
                
                new_node = Node(node_pos, current_node)
                new_node.g = current_node.g + 1
                new_node.h = abs(node_pos[0] - end_node.position[0]) + abs(node_pos[1] - end_node.position[1])
                new_node.f = new_node.g + new_node.h
                
                heapq.heappush(open_list, new_node)
    
    return None  # No path found

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Solver AI")

while True:  # Infinite game loop
    maze = generate_maze(ROWS, COLS)  # Generate a fresh maze every round
    player_pos = [0, 0]  # Reset player position
    path = astar(maze, (0, 0), (ROWS-1, COLS-1))  # Solve new maze
    
    running = True
    while running:
        screen.fill(WHITE)

        # Draw maze
        for row in range(ROWS):
            for col in range(COLS):
                color = WHITE if maze[row][col] == 0 else BLACK
                pygame.draw.rect(screen, color, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        
        
        # Draw exit
        pygame.draw.rect(screen, BLUE, ((ROWS-1) * CELL_SIZE, (COLS-1) * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        
        # Draw player
        pygame.draw.rect(screen, RED, (player_pos[1] * CELL_SIZE, player_pos[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                new_pos = player_pos[:]
                if event.key == pygame.K_UP:
                    new_pos[0] -= 1
                elif event.key == pygame.K_DOWN:
                    new_pos[0] += 1
                elif event.key == pygame.K_LEFT:
                    new_pos[1] -= 1
                elif event.key == pygame.K_RIGHT:
                    new_pos[1] += 1

                # Ensure movement is valid
                if 0 <= new_pos[0] < ROWS and 0 <= new_pos[1] < COLS and maze[new_pos[0]][new_pos[1]] == 0:
                    player_pos = new_pos

                # **Restart when player wins**
                if player_pos == [ROWS-1, COLS-1]:
                    print("🎉 You won! Generating a new maze...")
                    running = False

        pygame.display.flip()
