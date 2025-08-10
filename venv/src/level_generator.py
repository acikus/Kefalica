import random
from constants import *
from tiles import TileType, Tile

class LevelGenerator:
    """Generates game levels with increasingly difficult configurations"""
    
    def __init__(self):
        self.current_level = 1
    
    def generate_level(self, level_number):
        """Generate a level of specified difficulty"""
        self.current_level = level_number
        
        # Create empty grid
        grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        # Add obstacles (mountains, water, etc.) depending on level
        self.add_obstacles(grid)
        
        # Create a base path from entry to exit
        entry_point, exit_point = self.create_base_path(grid)
        
        # Remove random tiles from the path to create gaps for the player to fill
        self.create_gaps(grid)
        
        return grid
    
    def add_obstacles(self, grid):
        """Add obstacles to the grid based on current level"""
        # Higher levels have more obstacles
        num_obstacles = min(5 + self.current_level, 15)
        
        for _ in range(num_obstacles):
            x = random.randint(1, GRID_WIDTH - 2)  # Avoid edges
            y = random.randint(1, GRID_HEIGHT - 2)
            
            # Mark as obstacle (None means empty, False means obstacle)
            # We'll use special tile later for visualization
            grid[y][x] = False
    
    def create_base_path(self, grid):
        """
        Create a guaranteed path from the left edge (entry) to the right edge (exit)
        using a simple BFS. Return the (entry_x, entry_y) and (exit_x, exit_y).
        """

        # Decide on entry and exit points (not obstacles).
        # For simplicity, pick a row on the left edge and a row on the right edge that aren’t obstacles.
        entry_y = random.randint(0, GRID_HEIGHT - 1)
        while grid[entry_y][0] is False:
            entry_y = random.randint(0, GRID_HEIGHT - 1)

        exit_y = random.randint(0, GRID_HEIGHT - 1)
        while grid[exit_y][GRID_WIDTH - 1] is False:
            exit_y = random.randint(0, GRID_HEIGHT - 1)

        # Mark entry/exit cells with placeholder road tiles so BFS knows they are free.
        if grid[entry_y][0] is None or grid[entry_y][0] is False:
            grid[entry_y][0] = Tile(TileType.HORIZONTAL)
        if grid[exit_y][GRID_WIDTH - 1] is None or grid[exit_y][GRID_WIDTH - 1] is False:
            grid[exit_y][GRID_WIDTH - 1] = Tile(TileType.HORIZONTAL)

        start = (0, entry_y)
        goal = (GRID_WIDTH - 1, exit_y)

        # --- BFS to find any valid path from start to goal ---
        from collections import deque
        queue = deque([start])
        visited = set([start])
        parent = dict()  # To reconstruct the path if found

        found_path = False
        while queue:
            x, y = queue.popleft()
            if (x, y) == goal:
                found_path = True
                break

            # Explore 4-directional neighbors
            for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT):
                    # Check the cell is not an obstacle and not visited
                    if (nx, ny) not in visited and grid[ny][nx] is not False:
                        visited.add((nx, ny))
                        parent[(nx, ny)] = (x, y)
                        queue.append((nx, ny))

        if not found_path:
            # If BFS fails to find a path, you can handle it gracefully
            print("No valid path found. Try fewer obstacles or a different approach.")
            return start, goal

        # --- Reconstruct path from goal back to start using 'parent' ---
        path = []
        cur = goal
        while cur in parent:
            path.append(cur)
            cur = parent[cur]
        path.append(start)
        path.reverse()  # So it goes from start -> goal

        # Now fill in the path with road tiles. Here, we do a minimal approach:  
        # If the next cell is horizontally adjacent, use HORIZONTAL; if vertically adjacent, use VERTICAL.
        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]
            if x2 == x1 + 1 or x2 == x1 - 1:
                # Horizontal neighbor
                grid[y1][x1] = Tile(TileType.HORIZONTAL)
            elif y2 == y1 + 1 or y2 == y1 - 1:
                # Vertical neighbor
                grid[y1][x1] = Tile(TileType.VERTICAL)

        # Place a tile on the last path cell as well
        x_last, y_last = path[-1]
        # If we ended up in the same row as start, it's probably horizontal, otherwise vertical:
        if path[-1][0] == path[-2][0]:  # same column => vertical movement
            grid[y_last][x_last] = Tile(TileType.VERTICAL)
        else:
            grid[y_last][x_last] = Tile(TileType.HORIZONTAL)

        return start, goal

    
    def create_gaps(self, grid):
        """Remove random tiles from the path to create gaps for the player to fill"""
        # Count road tiles in the grid
        road_tiles = []
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if grid[y][x] and grid[y][x] is not False:  # If it's a road tile
                    road_tiles.append((x, y))
        
        # Calculate number of gaps based on level
        num_gaps = min(MAX_EMPTY_TILES_LEVEL_1 + (self.current_level - 1) * EMPTY_TILES_INCREMENT, 
                      len(road_tiles) // 2)  # Don't remove more than half the road
        
        # Avoid removing edge tiles (entry/exit)
        internal_road_tiles = [tile for tile in road_tiles 
                             if tile[0] > 0 and tile[0] < GRID_WIDTH - 1]
        
        # If not enough internal tiles, reduce number of gaps
        num_gaps = min(num_gaps, len(internal_road_tiles))
        
        # Randomly select tiles to remove
        tiles_to_remove = random.sample(internal_road_tiles, num_gaps)
        
        # Remove selected tiles
        for x, y in tiles_to_remove:
            grid[y][x] = None