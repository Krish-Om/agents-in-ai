"""
Utility-Based Agent for Snake Game

A utility-based agent makes decisions by evaluating the utility (satisfaction/happiness)
of each possible action and choosing the one that maximizes expected utility.

Key Characteristics:
1. Utility Function: Maps states to real numbers representing desirability
2. Multiple Criteria: Considers various factors (safety, food, efficiency)
3. Preference-Based: Reflects agent's preferences about different outcomes
4. Optimization: Chooses action that maximizes overall utility
"""

from typing import Dict, List, Tuple


def utility_based_agent(game):
    """
    Simple Utility-Based Agent for Snake Game

    Evaluates each possible action based on multiple utility factors:
    - Food attraction (getting closer to apple)
    - Safety (avoiding collisions)
    - Space preservation (maintaining maneuverability)
    - Efficiency (preferring shorter paths)
    """
    # Get current game state
    head_x, head_y = game.snake.x[0], game.snake.y[0]
    apple_x, apple_y = game.apple.x, game.apple.y
    current_direction = game.snake.direction

    # Define possible actions
    possible_actions = ["left", "right", "up", "down"]

    # Remove reverse direction to prevent immediate U-turn
    opposite_direction = {"left": "right", "right": "left", "up": "down", "down": "up"}
    if current_direction in opposite_direction:
        reverse_action = opposite_direction[current_direction]
        if reverse_action in possible_actions:
            possible_actions.remove(reverse_action)

    # Evaluate utility for each possible action
    best_action = None
    best_utility = float("-inf")

    for action in possible_actions:
        # Calculate utility for this action
        utility = calculate_utility(game, action, head_x, head_y, apple_x, apple_y)

        # Choose action with highest utility
        if utility > best_utility:
            best_utility = utility
            best_action = action

    # Execute the action with maximum utility
    if best_action:
        execute_action(game, best_action)
    else:
        # Fallback: continue current direction
        pass


def calculate_utility(
    game, action: str, head_x: int, head_y: int, apple_x: int, apple_y: int
) -> float:
    """
    Calculate the utility (desirability) of a specific action.

    Utility function combines multiple factors:
    1. Food Utility: Preference for getting closer to food
    2. Safety Utility: Preference for avoiding collisions
    3. Space Utility: Preference for maintaining maneuvering space
    4. Efficiency Utility: Preference for direct paths

    Returns:
        float: Utility score (higher = more desirable)
    """
    # Get potential next position using existing game function
    next_x, next_y = game._get_potential_head(action)

    # Check for immediate collision using existing game function
    if game._is_potential_move_colliding(next_x, next_y):
        return float("-inf")  # Collision has infinite negative utility

    # Initialize utility score
    total_utility = 0.0

    # 1. FOOD UTILITY: Preference for getting closer to apple
    food_utility = calculate_food_utility(
        game, head_x, head_y, next_x, next_y, apple_x, apple_y
    )
    total_utility += food_utility * 100  # Weight: 100

    # 2. SAFETY UTILITY: Preference for safe positions
    safety_utility = calculate_safety_utility(game, next_x, next_y)
    total_utility += safety_utility * 50  # Weight: 50

    # 3. SPACE UTILITY: Preference for positions with more options
    space_utility = calculate_space_utility(game, next_x, next_y)
    total_utility += space_utility * 30  # Weight: 30

    # 4. EFFICIENCY UTILITY: Preference for direct movement
    efficiency_utility = calculate_efficiency_utility(
        action, head_x, head_y, apple_x, apple_y
    )
    total_utility += efficiency_utility * 20  # Weight: 20

    return total_utility


def calculate_food_utility(
    game, head_x: int, head_y: int, next_x: int, next_y: int, apple_x: int, apple_y: int
) -> float:
    """
    Calculate utility based on food attraction.
    Higher utility for moves that get closer to the apple.
    """
    # Calculate distances using existing game function
    current_distance = game._calculate_distance(head_x, head_y, apple_x, apple_y)
    new_distance = game._calculate_distance(next_x, next_y, apple_x, apple_y)

    # Utility increases when distance to food decreases
    if new_distance < current_distance:
        return 1.0  # Moving closer to food
    elif new_distance == current_distance:
        return 0.0  # Maintaining same distance
    else:
        return -0.5  # Moving away from food


def calculate_safety_utility(game, x: int, y: int) -> float:
    """
    Calculate utility based on safety (avoiding dangerous positions).
    Uses existing game safety evaluation function.
    """
    # Use existing safety evaluation function from game
    safety_score = game._evaluate_safety(x, y)

    # Normalize safety score to utility range [0, 1]
    # Higher safety score = higher utility
    max_possible_safety = 4.0  # Maximum safety score (4 open directions)
    return safety_score / max_possible_safety


def calculate_space_utility(game, x: int, y: int) -> float:
    """
    Calculate utility based on available maneuvering space.
    Higher utility for positions with more movement options.
    """
    available_moves = 0
    directions = [("left", -40, 0), ("right", 40, 0), ("up", 0, -40), ("down", 0, 40)]

    for direction, dx, dy in directions:
        test_x, test_y = x + dx, y + dy
        if not game._is_potential_move_colliding(test_x, test_y):
            available_moves += 1

    # Normalize to [0, 1] range
    return available_moves / 4.0


def calculate_efficiency_utility(
    action: str, head_x: int, head_y: int, apple_x: int, apple_y: int
) -> float:
    """
    Calculate utility based on movement efficiency.
    Higher utility for actions that move directly toward the target.
    """
    # Determine if action moves in the optimal direction
    optimal_directions = []

    # Determine optimal horizontal movement
    if apple_x > head_x:
        optimal_directions.append("right")
    elif apple_x < head_x:
        optimal_directions.append("left")

    # Determine optimal vertical movement
    if apple_y > head_y:
        optimal_directions.append("down")
    elif apple_y < head_y:
        optimal_directions.append("up")

    # Return higher utility for optimal directions
    if action in optimal_directions:
        return 1.0  # Moving in optimal direction
    else:
        return 0.0  # Not moving in optimal direction


def execute_action(game, action: str) -> None:
    """
    Execute the chosen action using existing snake movement methods.
    """
    if action == "left":
        game.snake.move_left()
    elif action == "right":
        game.snake.move_right()
    elif action == "up":
        game.snake.move_up()
    elif action == "down":
        game.snake.move_down()


# Utility function weights explanation:
"""
UTILITY WEIGHTS RATIONALE:

1. Food Utility (Weight: 100)
   - Highest priority: getting food is the primary objective
   - Ensures agent actively pursues apples

2. Safety Utility (Weight: 50)
   - Second priority: survival is essential for continued play
   - Prevents immediate and near-future collisions

3. Space Utility (Weight: 30)
   - Third priority: maintaining options for future moves
   - Helps avoid getting trapped in tight spaces

4. Efficiency Utility (Weight: 20)
   - Lowest priority: prefer direct paths when other factors are equal
   - Encourages optimal movement patterns

These weights can be adjusted to change agent behavior:
- Higher food weight → more aggressive food pursuit
- Higher safety weight → more conservative, survival-focused
- Higher space weight → more space-preserving behavior
- Higher efficiency weight → more direct movement patterns
"""
