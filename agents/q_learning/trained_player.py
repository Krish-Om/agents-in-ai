#!/usr/bin/env python3
"""
Trained Agent Player for Snake Game
Plays the game using the Q-table trained by auto_trainer.py
"""

import pygame
import json
import math
import time
import sys
import os
from collections import defaultdict

# Add parent directories to path to import the game
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from core_game.source import Game, SIZE


class TrainedSnakePlayer:
    def __init__(self, q_table_file="trained_q_table.json"):
        self.q_table = defaultdict(lambda: [0.0, 0.0, 0.0])
        self.load_q_table(q_table_file)

    def load_q_table(self, filename):
        """Load the trained Q-table"""
        try:
            with open(filename, "r") as f:
                q_table_dict = json.load(f)

            # Convert string keys back to tuples
            for key_str, values in q_table_dict.items():
                key = eval(key_str)  # Convert string representation back to tuple
                self.q_table[key] = values

            print(f"✅ Loaded Q-table with {len(self.q_table)} states")

            # Load and display training stats
            try:
                with open("training_stats.json", "r") as f:
                    stats = json.load(f)
                print(f"📊 Training Stats:")
                print(f"   Episodes Trained: {stats['episode']}")
                print(f"   Best Score: {stats['best_score']}")
                print(f"   Average Score: {stats['average_score']:.2f}")
                print(f"   Total States: {stats['total_states']}")
            except FileNotFoundError:
                print("⚠️  Training stats not found")

        except FileNotFoundError:
            print(f"❌ Q-table file '{filename}' not found!")
            print("🚀 Please run auto_trainer.py first to train the agent")
            exit(1)

    def get_state(self, game):
        """Get the current state representation from the game (same as trainer)"""
        head_x, head_y = game.snake.x[0], game.snake.y[0]
        apple_x, apple_y = game.apple.x, game.apple.y
        direction = game.snake.direction

        # Convert to grid coordinates
        head_grid_x = head_x // SIZE
        head_grid_y = head_y // SIZE
        apple_grid_x = apple_x // SIZE
        apple_grid_y = apple_y // SIZE

        # Get potential next positions for danger detection
        straight_x, straight_y = self._get_next_position(head_x, head_y, direction)
        right_dir = self._get_relative_direction(direction, "right")
        left_dir = self._get_relative_direction(direction, "left")
        right_x, right_y = self._get_next_position(head_x, head_y, right_dir)
        left_x, left_y = self._get_next_position(head_x, head_y, left_dir)

        # Check for dangers
        danger_straight = self._is_dangerous_position(game, straight_x, straight_y)
        danger_right = self._is_dangerous_position(game, right_x, right_y)
        danger_left = self._is_dangerous_position(game, left_x, left_y)

        # Apple direction relative to current direction
        apple_direction = self._get_apple_direction(
            head_grid_x, head_grid_y, apple_grid_x, apple_grid_y, direction
        )

        # Distance to apple (bucketed)
        distance = math.sqrt(
            (head_grid_x - apple_grid_x) ** 2 + (head_grid_y - apple_grid_y) ** 2
        )
        dist_bucket = min(3, int(distance / 5))  # 0, 1, 2, 3

        state = (
            danger_straight,
            danger_right,
            danger_left,
            apple_direction,
            dist_bucket,
        )
        return state

    def _get_next_position(self, x, y, direction):
        """Get next position based on direction"""
        if direction == "up":
            return x, y - SIZE
        elif direction == "down":
            return x, y + SIZE
        elif direction == "left":
            return x - SIZE, y
        elif direction == "right":
            return x + SIZE, y
        return x, y

    def _get_relative_direction(self, current_dir, relative):
        """Get direction relative to current direction"""
        directions = ["up", "right", "down", "left"]
        current_idx = directions.index(current_dir)

        if relative == "right":
            return directions[(current_idx + 1) % 4]
        elif relative == "left":
            return directions[(current_idx - 1) % 4]
        return current_dir

    def _is_dangerous_position(self, game, x, y):
        """Check if position would cause collision"""
        # Wall collision
        if x < 0 or x >= 1000 or y < 0 or y >= 800:
            return True

        # Self collision (check against body segments excluding tail which will move)
        for i in range(1, min(game.snake.length - 1, len(game.snake.x) - 1)):
            if x == game.snake.x[i] and y == game.snake.y[i]:
                return True

        return False

    def _get_apple_direction(self, head_x, head_y, apple_x, apple_y, current_dir):
        """Get apple direction relative to current direction (0=straight, 1=right, 2=left, 3=back)"""
        dx = apple_x - head_x
        dy = apple_y - head_y

        # Determine absolute direction to apple
        if abs(dx) > abs(dy):
            apple_abs_dir = "right" if dx > 0 else "left"
        else:
            apple_abs_dir = "down" if dy > 0 else "up"

        # Convert to relative direction
        directions = ["up", "right", "down", "left"]
        current_idx = directions.index(current_dir)
        apple_idx = directions.index(apple_abs_dir)

        relative = (apple_idx - current_idx) % 4
        return relative

    def choose_action(self, state):
        """Choose the best action based on Q-table (no exploration)"""
        q_values = self.q_table[state]
        return q_values.index(max(q_values))

    def execute_action(self, game, action):
        """Execute the chosen action in the game"""
        if action == 0:  # Go straight - do nothing
            pass
        elif action == 1:  # Turn right
            if game.snake.direction == "up":
                game.snake.move_right()
            elif game.snake.direction == "right":
                game.snake.move_down()
            elif game.snake.direction == "down":
                game.snake.move_left()
            elif game.snake.direction == "left":
                game.snake.move_up()
        elif action == 2:  # Turn left
            if game.snake.direction == "up":
                game.snake.move_left()
            elif game.snake.direction == "left":
                game.snake.move_down()
            elif game.snake.direction == "down":
                game.snake.move_right()
            elif game.snake.direction == "right":
                game.snake.move_up()

    def play_game(self, num_games=10, show_game=True):
        """Play the game using trained agent"""
        print("\n🎮 Starting Trained Agent Gameplay")
        print(f"🎯 Playing {num_games} games")
        print("⌨️  Press ESC to quit early")
        print("=" * 50)

        scores = []

        for game_num in range(num_games):
            if show_game:
                game = Game()  # Create game with display
            else:
                # For batch testing without display
                pygame.init()
                game = Game()
                game.game_speed = 0.01  # Very fast for batch testing

            step_count = 0
            max_steps = 2000  # Prevent infinite loops

            print(f"🎮 Starting Game {game_num + 1}")

            try:
                while step_count < max_steps:
                    # Handle events (for ESC key)
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                print("🛑 Game interrupted by user")
                                return scores
                        elif event.type == pygame.QUIT:
                            print("🛑 Window closed by user")
                            return scores

                    # Get current state and choose action
                    current_state = self.get_state(game)
                    action = self.choose_action(current_state)

                    # Execute action and play one step
                    self.execute_action(game, action)
                    game.play()

                    step_count += 1

                    # Control game speed
                    if show_game:
                        time.sleep(game.game_speed)

                # If we reach max steps, it's probably an infinite loop
                print(f"⚠️  Game {game_num + 1} reached max steps ({max_steps})")
                final_score = game.snake.length - 1

            except Exception as e:
                # Game over
                final_score = game.snake.length - 1
                print(
                    f"🎯 Game {game_num + 1}: Score = {final_score} | Reason: {str(e)}"
                )

            scores.append(final_score)
            pygame.quit()

            # Brief pause between games
            if game_num < num_games - 1:
                time.sleep(1)
                pygame.init()

        return scores

    def analyze_performance(self, scores):
        """Analyze and display performance statistics"""
        if not scores:
            print("❌ No games completed for analysis")
            return

        print("\n📊 Performance Analysis")
        print("=" * 30)
        print(f"🎮 Games Played: {len(scores)}")
        print(f"🏆 Best Score: {max(scores)}")
        print(f"📉 Worst Score: {min(scores)}")
        print(f"📈 Average Score: {sum(scores) / len(scores):.2f}")
        print(f"📊 Scores: {scores}")

        # Score distribution
        score_counts = {}
        for score in scores:
            score_counts[score] = score_counts.get(score, 0) + 1

        print(f"📋 Score Distribution:")
        for score in sorted(score_counts.keys()):
            print(f"   Score {score}: {score_counts[score]} times")


def main():
    # Create the trained player
    player = TrainedSnakePlayer()

    print("🤖 Trained Snake Agent Ready!")
    print("Choose an option:")
    print("1. Play 1 game with display")
    print("2. Play 10 games with display")
    print("3. Test 20 games quickly (minimal display)")
    print("4. Performance test 50 games (no display)")

    choice = input("Enter choice (1-4): ").strip()

    if choice == "1":
        scores = player.play_game(num_games=1, show_game=True)
    elif choice == "2":
        scores = player.play_game(num_games=10, show_game=True)
    elif choice == "3":
        scores = player.play_game(num_games=20, show_game=True)
    elif choice == "4":
        scores = player.play_game(num_games=50, show_game=False)
    else:
        print("❌ Invalid choice, playing 1 game by default")
        scores = player.play_game(num_games=1, show_game=True)

    # Analyze performance
    player.analyze_performance(scores)


if __name__ == "__main__":
    main()
