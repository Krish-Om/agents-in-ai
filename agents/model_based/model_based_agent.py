import math
from typing import Dict, List, Tuple, Set

SIZE = 40
# Global world model storage
_world_model = None


def model_based_agent(game):
    # print("Running Model based agent")
    """
    Minimal Model-Based Agent for Snake Game

    Key Requirements Met:
    1. Internal State Storage
    2. World Model (game mechanics understanding)
    3. Learning from Experience
    4. Model-based Decision Making
    """
    global _world_model

    # REQUIREMENT 1: Internal State Storage
    # Initialize persistent world model (survives between function calls)
    if _world_model is None:
        _world_model = {
            "apple_positions": [],  # Track apple movement pattern
            "danger_zones": set(),  # Remember dangerous positions
            "safe_moves": {},  # Remember successful moves
            "collision_near_misses": [],  # Learn from close calls
            "movement_history": [],  # Track movement patterns
            "step_count": 0,  # Track game progression
        }

    world_model = _world_model
    world_model["step_count"] += 1

    # Get current game state
    current_state = {
        "head_pos": (game.snake.x[0], game.snake.y[0]),
        "apple_pos": (game.apple.x, game.apple.y),
        "snake_length": game.snake.length,
        "direction": game.snake.direction,
    }

    # REQUIREMENT 2: World Model - Update understanding of game mechanics
    update_world_model(world_model, current_state, game)

    # REQUIREMENT 3: Learning from Experience
    learn_from_experience(world_model, current_state, game)

    # REQUIREMENT 4: Model-based Decision Making
    action = make_model_based_decision(world_model, current_state, game)

    # Execute the chosen action
    execute_action(game, action)

    # Store this state for next iteration
    world_model["last_state"] = current_state
    world_model["last_action"] = action


def update_world_model(world_model: Dict, current_state: Dict, game) -> None:
    """
    REQUIREMENT 2: Maintain world model - understand how the game works
    """
    # Learn apple movement patterns
    apple_pos = current_state["apple_pos"]
    world_model["apple_positions"].append(apple_pos)

    # Keep only recent apple positions (sliding window)
    if len(world_model["apple_positions"]) > 10:
        world_model["apple_positions"].pop(0)

    # Update movement history
    head_pos = current_state["head_pos"]
    direction = current_state["direction"]
    world_model["movement_history"].append((head_pos, direction))

    # Keep recent movement history
    if len(world_model["movement_history"]) > 20:
        world_model["movement_history"].pop(0)


def learn_from_experience(world_model: Dict, current_state: Dict, game) -> None:
    """
    REQUIREMENT 3: Learn from experience - update model based on outcomes
    """
    head_x, head_y = current_state["head_pos"]

    # Learn from near-collision experiences using existing game functions
    for direction in ["left", "right", "up", "down"]:
        # Use existing _get_potential_head function instead of our own
        next_x, next_y = game._get_potential_head(direction)

        # If a move would cause collision, mark as danger zone
        if game._is_potential_move_colliding(next_x, next_y):
            world_model["danger_zones"].add((next_x, next_y))
            world_model["collision_near_misses"].append(
                {"position": (next_x, next_y), "step": world_model["step_count"]}
            )

    # Learn successful moves
    if "last_state" in world_model and "last_action" in world_model:
        last_pos = world_model["last_state"]["head_pos"]
        last_action = world_model["last_action"]

        # If we successfully moved without collision, remember this as safe
        world_model["safe_moves"][last_pos] = last_action

    # Forget old danger zones (environment changes as snake grows)
    current_step = world_model["step_count"]
    world_model["collision_near_misses"] = [
        miss
        for miss in world_model["collision_near_misses"]
        if current_step - miss["step"] < 50  # Forget after 50 steps
    ]


def predict_apple_next_position(
    apple_history: List[Tuple[int, int]],
) -> Tuple[int, int]:
    """
    Use learned apple pattern to predict next apple position
    """
    if len(apple_history) < 2:
        return apple_history[-1] if apple_history else (0, 0)

    # Simple pattern: check if apple moves in a predictable sequence
    # This works because the apple follows a predefined list in source.py
    return apple_history[-1]  # Simplified - could implement pattern recognition


def make_model_based_decision(world_model: Dict, current_state: Dict, game) -> str:
    """
    REQUIREMENT 4: Use internal model to make better decisions
    """
    head_x, head_y = current_state["head_pos"]
    apple_x, apple_y = current_state["apple_pos"]
    current_direction = current_state["direction"]

    # Get possible actions (avoid reversing)
    possible_actions = ["left", "right", "up", "down"]
    opposite_direction = {"left": "right", "right": "left", "up": "down", "down": "up"}

    if current_direction in opposite_direction:
        reverse_action = opposite_direction[current_direction]
        if reverse_action in possible_actions:
            possible_actions.remove(reverse_action)

    # Evaluate each action using the world model
    best_action = None
    best_score = float("-inf")

    for action in possible_actions:
        score = evaluate_action_with_model(world_model, current_state, action, game)
        if score > best_score:
            best_score = score
            best_action = action

    return best_action if best_action else "right"  # Fallback


def evaluate_action_with_model(
    world_model: Dict, current_state: Dict, action: str, game
) -> float:
    """
    Evaluate an action using the internal world model
    """
    head_x, head_y = current_state["head_pos"]
    apple_x, apple_y = current_state["apple_pos"]

    # Predict next position using world model
    # Use existing game function to predict next position
    next_x, next_y = game._get_potential_head(action)

    # Check immediate collision using game's collision detection
    if game._is_potential_move_colliding(next_x, next_y):
        return float("-inf")  # Avoid immediate death

    score = 0.0

    # Use model: Avoid learned danger zones
    if (next_x, next_y) in world_model["danger_zones"]:
        score -= 100  # Penalize moves toward known danger

    # Use model: Prefer moves that worked before
    if (head_x, head_y) in world_model["safe_moves"]:
        if world_model["safe_moves"][(head_x, head_y)] == action:
            score += 50  # Reward previously successful moves

    # Basic apple pursuit (enhanced with prediction)
    current_distance = game._calculate_distance(head_x, head_y, apple_x, apple_y)
    new_distance = game._calculate_distance(next_x, next_y, apple_x, apple_y)

    if new_distance < current_distance:
        score += 100  # Reward getting closer to apple

    # Use model: Consider future safety
    future_safety = evaluate_future_safety_with_model(world_model, next_x, next_y, game)
    score += future_safety * 20

    return score


def evaluate_future_safety_with_model(world_model: Dict, x: int, y: int, game) -> float:
    """
    Use world model to evaluate future safety from a position
    """
    safety_score = 0.0

    # Check how many safe moves are available from this position
    for direction in ["left", "right", "up", "down"]:
        # Calculate future position based on direction
        if direction == "left":
            future_x, future_y = x - SIZE, y
        elif direction == "right":
            future_x, future_y = x + SIZE, y
        elif direction == "up":
            future_x, future_y = x, y - SIZE
        elif direction == "down":
            future_x, future_y = x, y + SIZE
        else:
            continue

        # Avoid known danger zones
        if (future_x, future_y) in world_model["danger_zones"]:
            continue

        # Check collision with game state
        if not game._is_potential_move_colliding(future_x, future_y):
            safety_score += 1.0

    return safety_score


def execute_action(game, action: str) -> None:
    """Execute the chosen action"""
    if action == "left":
        game.snake.move_left()
    elif action == "right":
        game.snake.move_right()
    elif action == "up":
        game.snake.move_up()
    elif action == "down":
        game.snake.move_down()
