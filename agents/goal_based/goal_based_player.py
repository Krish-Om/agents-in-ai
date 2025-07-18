#!/usr/bin/env python3
"""
Goal-Based Agent Player for Snake Game
Runs the goal-based agent that uses explicit goals and planning
"""

import pygame
import sys
import os
import time

# Add parent directories to path to import the game and agent
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from core_game.source import Game, SIZE

# Import the goal-based agent function
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goal_based_agent import goal_based_agent


class GoalBasedPlayer:
    def __init__(self):
        self.games_played = 0
        self.total_score = 0
        self.best_score = 0
        self.scores = []

    def play_game(self, game):
        """Play one game using the goal-based agent"""
        try:
            while True:
                # Agent makes decision based on goals
                goal_based_agent(game)

                # Execute one game step
                game.play()

                # Small delay for visibility
                time.sleep(0.1)

        except Exception as e:
            # Game over
            final_score = game.snake.length - 1
            self.games_played += 1
            self.total_score += final_score
            self.scores.append(final_score)
            self.best_score = max(self.best_score, final_score)

            print(
                f"🎯 Game {self.games_played}: Score = {final_score}, Reason: {str(e)}"
            )
            return final_score

    def play_multiple_games(self, num_games=5, show_display=True):
        """Play multiple games and show statistics"""
        print("🤖 Goal-Based Agent Player")
        print(f"🎯 Playing {num_games} games")
        print("📋 Strategy: Uses explicit goals and planning with A* pathfinding")
        print("🎯 Goals: REACH_APPLE, AVOID_DEATH, MAXIMIZE_SCORE, MAINTAIN_SAFETY")
        print("=" * 70)

        for game_num in range(num_games):
            print(f"\n🎮 Starting Game {game_num + 1}")

            # Create new game instance
            game = Game()
            game.game_speed = (
                0.15 if show_display else 0.01
            )  # Faster for multiple games

            # Play the game
            self.play_game(game)

            # Close the game window
            pygame.quit()
            pygame.init()

        # Show final statistics
        self.show_statistics()

    def show_statistics(self):
        """Display performance statistics"""
        if self.games_played == 0:
            print("❌ No games completed for analysis")
            return

        avg_score = self.total_score / self.games_played

        print("\n" + "=" * 70)
        print("📊 GOAL-BASED AGENT PERFORMANCE STATISTICS")
        print("=" * 70)
        print(f"🎮 Games Played: {self.games_played}")
        print(f"🏆 Best Score: {self.best_score}")
        print(f"📈 Average Score: {avg_score:.2f}")
        print(f"📊 Total Score: {self.total_score}")

        if len(self.scores) >= 5:
            recent_avg = sum(self.scores[-5:]) / 5
            print(f"🔥 Last 5 Games Average: {recent_avg:.2f}")

        print(f"📋 All Scores: {self.scores}")
        print("📝 Strategy Notes:")
        print("   • Uses A* pathfinding to reach apple")
        print("   • Dynamically switches between goals based on game state")
        print("   • Prioritizes safety when path to apple is dangerous")
        print("   • Plans ahead to avoid getting trapped")
        print("=" * 70)

    def play_single_game(self):
        """Play a single game with full display"""
        print("🤖 Goal-Based Agent Player")
        print("📋 Strategy: Uses explicit goals and A* pathfinding")
        print("🎯 Goals: REACH_APPLE, AVOID_DEATH, MAXIMIZE_SCORE, MAINTAIN_SAFETY")
        print("⌨️  Press ESC to quit")
        print("=" * 70)

        game = Game()
        game.game_speed = 0.2  # Moderate speed for watching

        running = True
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                elif event.type == pygame.QUIT:
                    running = False

            if running:
                try:
                    # Agent makes decision based on goals
                    goal_based_agent(game)

                    # Execute one game step
                    game.play()

                except Exception as e:
                    # Game over
                    final_score = game.snake.length - 1
                    print(f"🎯 Final Score: {final_score}, Reason: {str(e)}")

                    # Show game over screen
                    game.show_game_over(str(e))

                    # Wait for user input
                    waiting = True
                    while waiting and running:
                        for event in pygame.event.get():
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_RETURN:
                                    # Restart game
                                    game.reset()
                                    waiting = False
                                elif event.key == pygame.K_ESCAPE:
                                    running = False
                                    waiting = False
                            elif event.type == pygame.QUIT:
                                running = False
                                waiting = False

        pygame.quit()


def main():
    """Main function with user menu"""
    player = GoalBasedPlayer()

    print("🐍 Goal-Based Agent for Snake Game")
    print("\nChoose an option:")
    print("1. Play 1 game with display")
    print("2. Play 5 games with statistics")
    print("3. Play 10 games with statistics")
    print("4. Quick test 20 games (fast)")

    try:
        choice = input("\nEnter choice (1-4): ").strip()

        if choice == "1":
            player.play_single_game()
        elif choice == "2":
            player.play_multiple_games(5, show_display=True)
        elif choice == "3":
            player.play_multiple_games(10, show_display=True)
        elif choice == "4":
            player.play_multiple_games(20, show_display=False)
        else:
            print("❌ Invalid choice. Please run the script again.")

    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
