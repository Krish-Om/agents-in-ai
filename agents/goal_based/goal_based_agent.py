import math
from typing import List, Tuple, Optional
from collections import deque
import heapq

SIZE = 40


# Explicit Goal Definitions
class Goals:
    REACH_APPLE = "reach_apple"
    AVOID_DEATH = "avoid_death"
    MAXIMIZE_SCORE = "maximize_score"
    MAINTAIN_SAFETY = "maintain_safety"


def goal_based_agent(game):
    print("Running goal_based_agent")
    """
    A true goal-based agent that:
    1. Defines explicit goals
    2. Plans sequences of actions using search algorithms
    3. Considers future states beyond immediate moves
    4. Uses A* pathfinding to achieve goals
    """

    # Get current state
    head_x, head_y = game.snake.x[0], game.snake.y[0]
    apple_x, apple_y = game.apple.x, game.apple.y

    # Goal Priority System
    current_goals = determine_active_goals(game)

    # Goal 1: PRIMARY - Find safe path to apple (REACH_APPLE + AVOID_DEATH)
    if Goals.REACH_APPLE in current_goals:
        path_to_apple = a_star_search(game, (head_x, head_y), (apple_x, apple_y))

        if path_to_apple and len(path_to_apple) > 1:
            # Verify the path is still safe after planning
            if is_path_safe(game, path_to_apple):
                next_move = get_direction_from_positions(
                    head_x, head_y, path_to_apple[1][0], path_to_apple[1][1]
                )
                execute_move(game, next_move)
                return

    # Goal 2: SAFETY - Maintain safe space when no direct path to apple
    if Goals.MAINTAIN_SAFETY in current_goals:
        safe_exploration_move = find_safe_exploration_move(game)
        if safe_exploration_move:
            execute_move(game, safe_exploration_move)
            return

    # Goal 3: MAXIMIZE_SCORE - Use BFS to find any reachable apple path
    if Goals.MAXIMIZE_SCORE in current_goals:
        bfs_path = bfs_search(game, (head_x, head_y), (apple_x, apple_y))
        if bfs_path and len(bfs_path) > 1:
            next_move = get_direction_from_positions(
                head_x, head_y, bfs_path[1][0], bfs_path[1][1]
            )
            execute_move(game, next_move)
            return

    # Goal 4: AVOID_DEATH - Emergency survival mode
    emergency_move(game)


def execute_move(game, direction: str):
    """Executes the chosen move direction using existing snake methods."""
    if direction == "left":
        game.snake.move_left()
    elif direction == "right":
        game.snake.move_right()
    elif direction == "up":
        game.snake.move_up()
    elif direction == "down":
        game.snake.move_down()


def emergency_move(game):
    """
    Emergency survival mode - tries any safe move to avoid immediate death.
    Uses existing methods to find any move that doesn't cause immediate collision.
    """
    emergency_directions = ["left", "right", "up", "down"]
    current_direction = game.snake.direction

    # Remove opposite direction to current to avoid reversing
    opposite_map = {"left": "right", "right": "left", "up": "down", "down": "up"}
    opposite = opposite_map.get(current_direction)
    if opposite in emergency_directions:
        emergency_directions.remove(opposite)

    # Try each direction using existing methods
    for direction in emergency_directions:
        next_x, next_y = game._get_potential_head(direction)
        if not game._is_potential_move_colliding(next_x, next_y):
            execute_move(game, direction)
            return

    # If no safe move found, continue current direction (last resort)
    pass


def determine_active_goals(game) -> List[str]:
    """
    Determines which goals are currently active based on game state.
    Returns list of active goals in priority order.
    """
    goals = []

    # Always prioritize avoiding death
    goals.append(Goals.AVOID_DEATH)

    # Check if apple is reachable safely
    head_x, head_y = game.snake.x[0], game.snake.y[0]
    apple_x, apple_y = game.apple.x, game.apple.y

    # Calculate available space
    available_space = count_available_space(game)
    snake_length = game.snake.length

    # If we have plenty of space, prioritize reaching apple
    if available_space > snake_length * 2:
        goals.append(Goals.REACH_APPLE)
        goals.append(Goals.MAXIMIZE_SCORE)

    # Always maintain safety
    goals.append(Goals.MAINTAIN_SAFETY)

    return goals


def count_available_space(game) -> int:
    """Count total available spaces on the game board."""
    screen_width = game.surface.get_width()
    screen_height = game.surface.get_height()

    total_cells = (screen_width // SIZE) * (screen_height // SIZE)
    occupied_cells = game.snake.length

    return total_cells - occupied_cells


def a_star_search(
    game, start: Tuple[int, int], goal: Tuple[int, int]
) -> Optional[List[Tuple[int, int]]]:
    """
    A* pathfinding algorithm to find optimal path from start to goal.
    Returns list of (x, y) coordinates representing the path.
    """

    def heuristic(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Manhattan distance heuristic"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def get_neighbors(pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get valid neighboring positions"""
        x, y = pos
        neighbors = []

        for dx, dy in [(-SIZE, 0), (SIZE, 0), (0, -SIZE), (0, SIZE)]:
            new_x, new_y = x + dx, y + dy

            # Check bounds and collisions
            if not game._is_potential_move_colliding(new_x, new_y):
                neighbors.append((new_x, new_y))

        return neighbors

    # A* algorithm implementation
    open_set = [(0, start)]  # (f_score, position)
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}
    closed_set = set()

    while open_set:
        current_f, current_pos = heapq.heappop(open_set)

        if current_pos in closed_set:
            continue

        closed_set.add(current_pos)

        if current_pos == goal:
            # Reconstruct path
            path = []
            while current_pos in came_from:
                path.append(current_pos)
                current_pos = came_from[current_pos]
            path.append(start)
            return list(reversed(path))

        for neighbor in get_neighbors(current_pos):
            if neighbor in closed_set:
                continue

            tentative_g = g_score[current_pos] + SIZE

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current_pos
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor, goal)

                heapq.heappush(open_set, (int(f_score[neighbor]), neighbor))

    return None  # No path found


def bfs_search(
    game, start: Tuple[int, int], goal: Tuple[int, int]
) -> Optional[List[Tuple[int, int]]]:
    """
    Breadth-First Search to find any path from start to goal.
    Useful as fallback when A* fails.
    """

    def get_neighbors(pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get valid neighboring positions"""
        x, y = pos
        neighbors = []

        for dx, dy in [(-SIZE, 0), (SIZE, 0), (0, -SIZE), (0, SIZE)]:
            new_x, new_y = x + dx, y + dy

            if not game._is_potential_move_colliding(new_x, new_y):
                neighbors.append((new_x, new_y))

        return neighbors

    queue = deque([(start, [start])])
    visited = {start}

    while queue:
        current_pos, path = queue.popleft()

        if current_pos == goal:
            return path

        for neighbor in get_neighbors(current_pos):
            if neighbor not in visited:
                visited.add(neighbor)
                new_path = path + [neighbor]
                queue.append((neighbor, new_path))

    return None  # No path found


def is_path_safe(game, path: List[Tuple[int, int]]) -> bool:
    """
    Checks if following a path would still leave escape options.
    Considers future snake positions after following the path.
    """
    if len(path) < 2:
        return False

    # Simulate following the path
    final_pos = path[-1]  # Where we'll end up (apple position)

    # Check if we'd have escape options after reaching the apple
    escape_count = 0
    for dx, dy in [(-SIZE, 0), (SIZE, 0), (0, -SIZE), (0, SIZE)]:
        escape_x, escape_y = final_pos[0] + dx, final_pos[1] + dy

        # Don't count positions that would be occupied by snake body
        if not game._is_potential_move_colliding(escape_x, escape_y):
            escape_count += 1

    # Require at least 1 escape option (could be made more sophisticated)
    return escape_count >= 1


def find_safe_exploration_move(game) -> Optional[str]:
    """
    Finds a move that maximizes future options and maintains safety.
    Uses look-ahead to avoid getting trapped.
    """
    head_x, head_y = game.snake.x[0], game.snake.y[0]
    current_direction = game.snake.direction

    possible_moves = ["left", "right", "up", "down"]

    # Remove reverse direction
    opposite_map = {"left": "right", "right": "left", "up": "down", "down": "up"}
    opposite = opposite_map.get(current_direction)
    if opposite in possible_moves:
        possible_moves.remove(opposite)

    best_move = None
    best_score = -1

    for move in possible_moves:
        next_x, next_y = game._get_potential_head(move)

        if game._is_potential_move_colliding(next_x, next_y):
            continue

        # Look ahead 2-3 steps to evaluate future options
        future_score = evaluate_future_options(game, next_x, next_y, depth=3)

        if future_score > best_score:
            best_score = future_score
            best_move = move

    return best_move


def evaluate_future_options(game, x: int, y: int, depth: int) -> float:
    """
    Recursively evaluates future movement options from a position.
    Higher score means more future flexibility.
    """
    if depth <= 0:
        return 0

    options = 0
    total_future_score = 0

    for dx, dy in [(-SIZE, 0), (SIZE, 0), (0, -SIZE), (0, SIZE)]:
        future_x, future_y = x + dx, y + dy

        if not game._is_potential_move_colliding(future_x, future_y):
            options += 1
            # Recursively check future options
            total_future_score += evaluate_future_options(
                game, future_x, future_y, depth - 1
            )

    # Combine immediate options with future options
    return options + (total_future_score * 0.5)  # Weight future less than immediate


def get_direction_from_positions(
    current_x: int, current_y: int, target_x: int, target_y: int
) -> str:
    """
    Converts two positions into a movement direction.
    """
    if target_x > current_x:
        return "right"
    elif target_x < current_x:
        return "left"
    elif target_y > current_y:
        return "down"
    elif target_y < current_y:
        return "up"

    return "right"  # Default fallback
