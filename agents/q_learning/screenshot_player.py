#!/usr/bin/env python3
"""
Screenshot-friendly Trained Player for Snake Game
Modified version for capturing final performance screenshots
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


class ScreenshotPlayer:
    def __init__(self, q_table_file="trained_q_table.json"):
        self.q_table = defaultdict(lambda: [0.0, 0.0, 0.0])
        self.load_q_table(q_table_file)

        # For display
        pygame.init()
        self.font = pygame.font.SysFont("arial", 24)
        self.big_font = pygame.font.SysFont("arial", 32)

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
                    self.stats = json.load(f)
                print(f"📊 Training Stats:")
                print(f"   Episodes Trained: {self.stats['episode']}")
                print(f"   Best Score: {self.stats['best_score']}")
                print(f"   Average Score: {self.stats['average_score']:.2f}")
                print(f"   Total States: {self.stats['total_states']}")
            except FileNotFoundError:
                print("⚠️  Training stats not found")
                self.stats = None

        except FileNotFoundError:
            print(f"❌ Q-table file '{filename}' not found!")
            print("🚀 Please run auto_trainer.py first to train the agent")
            exit(1)

    def display_performance_info(self, game, current_score, game_num, total_games):
        """Display performance information on the game screen"""
        # Background for text
        info_surface = pygame.Surface((450, 250))
        info_surface.set_alpha(220)
        info_surface.fill((0, 0, 0))
        game.surface.blit(info_surface, (530, 10))

        # Performance info
        y_offset = 20

        # Handle stats safely
        avg_score_text = (
            f"{self.stats['average_score']:.2f}"
            if self.stats and "average_score" in self.stats
            else "Unknown"
        )

        texts = [
            f"TRAINED Q-LEARNING AGENT",
            f"Game: {game_num}/{total_games}",
            f"Current Score: {current_score}",
            f"Episodes Trained: {self.stats['episode'] if self.stats else 'Unknown'}",
            f"Training Best: {self.stats['best_score'] if self.stats else 'Unknown'}",
            f"Training Avg: {avg_score_text}",
            f"Q-States: {len(self.q_table)}",
            f"Exploration: 0% (Pure Exploitation)",
        ]

        # Title in bigger font
        title_text = self.big_font.render(texts[0], True, (0, 255, 0))
        game.surface.blit(title_text, (540, y_offset))
        y_offset += 40

        # Other info in normal font
        for text in texts[1:]:
            text_surface = self.font.render(text, True, (255, 255, 255))
            game.surface.blit(text_surface, (540, y_offset))
            y_offset += 25

        # Add a visual indicator for Q-Learning
        indicator_text = self.font.render(
            "🧠 Using Learned Knowledge", True, (255, 255, 0)
        )
        game.surface.blit(indicator_text, (540, y_offset + 10))

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

    def play_for_screenshots(self, num_games=5):
        """Play games with screenshot-friendly display"""
        print("\n🎬 Starting Screenshot-Friendly Trained Agent Gameplay")
        print(f"🎯 Playing {num_games} games for screenshots")
        print("📸 Game will pause periodically for screenshots")
        print("=" * 60)

        scores = []

        for game_num in range(1, num_games + 1):
            print(f"\n🎮 Starting Game {game_num}")
            print("📸 Take screenshots during gameplay!")

            game = Game()
            step_count = 0
            max_steps = 2000  # Prevent infinite loops

            try:
                while step_count < max_steps:
                    # Handle events (for ESC key)
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                print("🛑 Game interrupted by user")
                                return scores
                            elif event.key == pygame.K_SPACE:
                                print(
                                    "⏸️  Game paused for screenshot. Press SPACE again to continue."
                                )
                                input("Press ENTER when screenshot is taken...")
                        elif event.type == pygame.QUIT:
                            print("🛑 Window closed by user")
                            return scores

                    # Get current state and choose action
                    current_state = self.get_state(game)
                    action = self.choose_action(current_state)

                    # Execute action and play one step
                    self.execute_action(game, action)
                    game.play()

                    # Display performance info
                    current_score = game.snake.length - 1
                    self.display_performance_info(
                        game, current_score, game_num, num_games
                    )
                    pygame.display.flip()

                    step_count += 1

                    # Slower gameplay for better screenshots
                    time.sleep(0.15)

                # If we reach max steps, it's probably an infinite loop
                print(f"⚠️  Game {game_num} reached max steps ({max_steps})")
                final_score = game.snake.length - 1

            except Exception as e:
                # Game over
                final_score = game.snake.length - 1
                print(f"🎯 Game {game_num}: Score = {final_score} | Reason: {str(e)}")

            scores.append(final_score)

            # Pause between games for screenshots
            if game_num < num_games:
                print(f"📸 Game {game_num} completed with score {final_score}")
                input(f"⏸️  Press ENTER to start Game {game_num + 1}...")

            pygame.quit()
            time.sleep(1)
            pygame.init()

        return scores


def main():
    # Create the screenshot player
    player = ScreenshotPlayer()

    print("🎬 Screenshot-Friendly Trained Snake Agent!")
    print("This version is optimized for taking screenshots.")
    print("\nControls during gameplay:")
    print("  SPACE = Pause for screenshot")
    print("  ESC = Quit")
    print("\nChoose an option:")
    print("1. Play 3 games for screenshots (slow pace)")
    print("2. Play 1 game for detailed screenshots")
    print("3. Demo run (very slow for perfect screenshots)")

    choice = input("Enter choice (1-3): ").strip()

    if choice == "1":
        scores = player.play_for_screenshots(num_games=3)
    elif choice == "2":
        scores = player.play_for_screenshots(num_games=1)
    elif choice == "3":
        scores = player.play_for_screenshots(num_games=1)
    else:
        print("❌ Invalid choice, playing 1 game by default")
        scores = player.play_for_screenshots(num_games=1)

    # Final statistics
    if scores:
        print("\n📊 Screenshot Session Results")
        print("=" * 40)
        print(f"🎮 Games Played: {len(scores)}")
        print(f"🏆 Best Score: {max(scores)}")
        print(f"📈 Average Score: {sum(scores) / len(scores):.2f}")
        print(f"📊 All Scores: {scores}")


if __name__ == "__main__":
    main()
