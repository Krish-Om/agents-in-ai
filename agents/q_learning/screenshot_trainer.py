#!/usr/bin/env python3
"""
Screenshot-friendly Q-Learning Trainer for Snake Game
Modified version with visible training progress for report screenshots
"""

import pygame
import json
import time
import random
import math
import sys
import os
from collections import defaultdict

# Add parent directories to path to import the game
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from core_game.source import Game, SIZE

# Q-Learning Parameters
LEARNING_RATE = 0.15
DISCOUNT_FACTOR = 0.95
INITIAL_EPSILON = 0.9
FINAL_EPSILON = 0.01
EPSILON_DECAY_EPISODES = 1000


class ScreenshotTrainer:
    def __init__(self):
        self.q_table = defaultdict(lambda: [0.0, 0.0, 0.0])  # [straight, right, left]
        self.epsilon = INITIAL_EPSILON
        self.episode = 0
        self.scores = []
        self.best_score = 0

        # For display
        pygame.init()
        self.font = pygame.font.SysFont("arial", 24)
        self.big_font = pygame.font.SysFont("arial", 32)

    def display_training_info(self, game, episode, score, avg_score):
        """Display training information on the game screen"""
        # Background for text
        info_surface = pygame.Surface((400, 200))
        info_surface.set_alpha(220)
        info_surface.fill((0, 0, 0))
        game.surface.blit(info_surface, (580, 10))

        # Training info
        y_offset = 20
        texts = [
            f"Q-LEARNING TRAINING",
            f"Episode: {episode}/1500",
            f"Current Score: {score}",
            f"Best Score: {self.best_score}",
            f"Avg Score (50): {avg_score:.2f}",
            f"Epsilon: {self.epsilon:.3f}",
            f"Q-States: {len(self.q_table)}",
            f"Learning Rate: {LEARNING_RATE}",
        ]

        # Title in bigger font
        title_text = self.big_font.render(texts[0], True, (255, 255, 0))
        game.surface.blit(title_text, (590, y_offset))
        y_offset += 40

        # Other info in normal font
        for text in texts[1:]:
            text_surface = self.font.render(text, True, (255, 255, 255))
            game.surface.blit(text_surface, (590, y_offset))
            y_offset += 25

    def get_state(self, game):
        """Get the current state representation from the game"""
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
        """Choose action using epsilon-greedy policy"""
        if random.random() < self.epsilon:
            return random.randint(0, 2)  # Random action
        else:
            return self.q_table[state].index(max(self.q_table[state]))  # Best action

    def update_q_table(self, state, action, reward, next_state):
        """Update Q-table using Q-learning formula"""
        current_q = self.q_table[state][action]
        max_next_q = max(self.q_table[next_state])
        new_q = current_q + LEARNING_RATE * (
            reward + DISCOUNT_FACTOR * max_next_q - current_q
        )
        self.q_table[state][action] = new_q

    def get_reward(self, game, action_taken, prev_score, collision_occurred=False):
        """Calculate reward based on game state"""
        current_score = game.snake.length - 1

        if collision_occurred:
            return -100  # Heavy penalty for collision

        if current_score > prev_score:
            return 50  # Reward for eating apple

        # Small reward for moving toward apple
        head_x, head_y = game.snake.x[0], game.snake.y[0]
        apple_x, apple_y = game.apple.x, game.apple.y
        distance_to_apple = math.sqrt((head_x - apple_x) ** 2 + (head_y - apple_y) ** 2)

        if distance_to_apple < 100:  # Close to apple
            return 1

        return -1  # Small penalty for each step to encourage efficiency

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

    def save_progress(self):
        """Save Q-table and training stats"""
        # Save Q-table
        q_table_dict = {str(k): v for k, v in self.q_table.items()}
        with open("trained_q_table.json", "w") as f:
            json.dump(q_table_dict, f, indent=2)

        # Save training stats
        stats = {
            "episode": self.episode,
            "best_score": self.best_score,
            "average_score": (
                sum(self.scores[-100:]) / min(100, len(self.scores))
                if self.scores
                else 0
            ),
            "total_states": len(self.q_table),
            "epsilon": self.epsilon,
            "scores_history": self.scores[-100:],  # Keep last 100 scores
        }

        with open("training_stats.json", "w") as f:
            json.dump(stats, f, indent=2)

    def update_epsilon(self):
        """Decay epsilon over episodes"""
        if self.episode < EPSILON_DECAY_EPISODES:
            self.epsilon = INITIAL_EPSILON - (INITIAL_EPSILON - FINAL_EPSILON) * (
                self.episode / EPSILON_DECAY_EPISODES
            )
        else:
            self.epsilon = FINAL_EPSILON

    def train_for_screenshots(self, screenshot_episodes=[50, 200, 500, 1000]):
        """Training with strategic pauses for screenshots"""
        print("🎬 Starting Screenshot-Friendly Q-Learning Training")
        print(f"📸 Will pause for screenshots at episodes: {screenshot_episodes}")
        print("⏸️  Press ENTER when ready to continue after each screenshot")
        print("=" * 60)

        max_episodes = 1500
        screenshot_taken = set()

        for episode in range(max_episodes):
            self.episode = episode
            game = Game()

            # Initialize game state
            prev_state = None
            prev_action = None
            prev_score = 0
            step_count = 0
            max_steps = 1000  # Prevent infinite loops

            # Episode loop
            while step_count < max_steps:
                try:
                    # Get current state
                    current_state = self.get_state(game)

                    # Update Q-table for previous action if this isn't the first step
                    if prev_state is not None:
                        reward = self.get_reward(game, prev_action, prev_score)
                        self.update_q_table(
                            prev_state, prev_action, reward, current_state
                        )

                    # Choose and execute action
                    action = self.choose_action(current_state)
                    self.execute_action(game, action)

                    # Play one step of the game
                    current_score = game.snake.length - 1
                    game.play()

                    # Display training info for screenshots
                    if episode in screenshot_episodes:
                        avg_score = (
                            sum(self.scores[-50:]) / min(50, len(self.scores))
                            if self.scores
                            else 0
                        )
                        self.display_training_info(
                            game, episode, current_score, avg_score
                        )
                        pygame.display.flip()
                        time.sleep(0.1)  # Slower for screenshot

                    # Store current state for next iteration
                    prev_state = current_state
                    prev_action = action
                    prev_score = current_score
                    step_count += 1

                except Exception as e:
                    # Game over - update Q-table with collision penalty
                    if prev_state is not None:
                        collision_reward = self.get_reward(
                            game, prev_action, prev_score, collision_occurred=True
                        )
                        final_state = self.get_state(game)  # Get final state
                        self.update_q_table(
                            prev_state, prev_action, collision_reward, final_state
                        )
                    break

            # Episode finished
            final_score = game.snake.length - 1
            self.scores.append(final_score)
            self.best_score = max(self.best_score, final_score)

            # Update epsilon
            self.update_epsilon()

            # Print progress
            if episode % 50 == 0:
                avg_score = sum(self.scores[-50:]) / min(50, len(self.scores))
                print(
                    f"Episode {episode:4d} | Score: {final_score:2d} | "
                    f"Avg(50): {avg_score:5.2f} | Best: {self.best_score:2d} | "
                    f"Epsilon: {self.epsilon:.3f} | States: {len(self.q_table)}"
                )

            # Pause for screenshots at specific episodes
            if episode in screenshot_episodes and episode not in screenshot_taken:
                print(f"\n📸 SCREENSHOT TIME - Episode {episode}")
                print(
                    f"Current Stats: Score={final_score}, Best={self.best_score}, States={len(self.q_table)}"
                )
                print("🎬 Take your screenshot now!")
                input("⏸️  Press ENTER when screenshot is taken to continue training...")
                screenshot_taken.add(episode)

            # Save progress periodically
            if episode % 100 == 0 and episode > 0:
                self.save_progress()
                print(f"💾 Progress saved at episode {episode}")

            pygame.quit()  # Clean up pygame for this episode
            pygame.init()  # Reinitialize for next episode

        # Final save
        self.save_progress()

        print("\n🎉 Training Completed!")
        print(f"📊 Total Episodes: {self.episode + 1}")
        print(f"🏆 Best Score: {self.best_score}")
        print(
            f"📈 Final Average (last 100): {sum(self.scores[-100:]) / min(100, len(self.scores)):.2f}"
        )
        print(f"🧠 Total States Learned: {len(self.q_table)}")
        print(f"💾 Q-table saved as: trained_q_table.json")
        print(f"📋 Stats saved as: training_stats.json")


if __name__ == "__main__":
    trainer = ScreenshotTrainer()
    trainer.train_for_screenshots(screenshot_episodes=[50, 200, 500, 1000, 1400])
