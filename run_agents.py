#!/usr/bin/env python3
"""
Master Agent Runner for Snake Game
Central script to run any of the implemented AI agents
"""

import os
import sys
import subprocess

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PROJECT_ROOT)

# Python executable path
PYTHON_PATH = os.path.join(PROJECT_ROOT, ".venv", "bin", "python")


def show_banner():
    """Display the main menu banner"""
    print("🐍" * 30)
    print("🤖 SNAKE GAME AI AGENTS RUNNER 🤖")
    print("🐍" * 30)
    print()


def show_agent_info():
    """Display information about each agent type"""
    print("📋 Available AI Agents:")
    print()
    print("1️⃣  Simple Reflex Agent")
    print("   🧠 Strategy: Direct reactions to immediate perceptions")
    print("   📈 Complexity: Low | Speed: Fast | Planning: None")
    print()
    print("2️⃣  Goal-Based Agent")
    print("   🧠 Strategy: Uses explicit goals with A* pathfinding")
    print("   📈 Complexity: Medium | Speed: Medium | Planning: Path-based")
    print()
    print("3️⃣  Model-Based Agent")
    print("   🧠 Strategy: Maintains internal world model with prediction")
    print("   📈 Complexity: High | Speed: Medium | Planning: Predictive")
    print()
    print("4️⃣  Utility-Based Agent")
    print("   🧠 Strategy: Maximizes expected utility across criteria")
    print("   📈 Complexity: High | Speed: Slow | Planning: Utility-optimized")
    print()
    print("5️⃣  Q-Learning Agent")
    print("   🧠 Strategy: Reinforcement learning with Q-table")
    print("   📈 Complexity: Very High | Speed: Fast | Planning: Learned")
    print()


def run_simple_reflex():
    """Run the simple reflex agent"""
    agent_path = os.path.join(
        PROJECT_ROOT, "agents", "simple_reflex", "simple_reflex_player.py"
    )
    subprocess.run([PYTHON_PATH, agent_path], cwd=os.path.dirname(agent_path))


def run_goal_based():
    """Run the goal-based agent"""
    agent_path = os.path.join(
        PROJECT_ROOT, "agents", "goal_based", "goal_based_player.py"
    )
    subprocess.run([PYTHON_PATH, agent_path], cwd=os.path.dirname(agent_path))


def run_model_based():
    """Run the model-based agent"""
    agent_path = os.path.join(
        PROJECT_ROOT, "agents", "model_based", "model_based_player.py"
    )
    subprocess.run([PYTHON_PATH, agent_path], cwd=os.path.dirname(agent_path))


def run_utility_based():
    """Run the utility-based agent"""
    agent_path = os.path.join(
        PROJECT_ROOT, "agents", "utility_based", "utility_based_player.py"
    )
    subprocess.run([PYTHON_PATH, agent_path], cwd=os.path.dirname(agent_path))


def run_q_learning():
    """Show Q-learning options"""
    print("\n🧠 Q-Learning Agent Options:")
    print("1. Train new agent (auto_trainer.py)")
    print("2. Play with trained agent (trained_player.py)")
    print("3. Screenshot training (screenshot_trainer.py)")
    print("4. Screenshot playing (screenshot_player.py)")

    choice = input("\nEnter choice (1-4): ").strip()

    q_learning_dir = os.path.join(PROJECT_ROOT, "agents", "q_learning")

    if choice == "1":
        script_path = os.path.join(q_learning_dir, "auto_trainer.py")
    elif choice == "2":
        script_path = os.path.join(q_learning_dir, "trained_player.py")
    elif choice == "3":
        script_path = os.path.join(q_learning_dir, "screenshot_trainer.py")
    elif choice == "4":
        script_path = os.path.join(q_learning_dir, "screenshot_player.py")
    else:
        print("❌ Invalid choice")
        return

    subprocess.run([PYTHON_PATH, script_path], cwd=q_learning_dir)


def main():
    """Main menu function"""
    while True:
        show_banner()
        show_agent_info()

        print("🎮 Choose an agent to run:")
        print("1. Simple Reflex Agent")
        print("2. Goal-Based Agent")
        print("3. Model-Based Agent")
        print("4. Utility-Based Agent")
        print("5. Q-Learning Agent")
        print("6. Exit")

        try:
            choice = input("\n👉 Enter your choice (1-6): ").strip()

            if choice == "1":
                print("\n🚀 Launching Simple Reflex Agent...")
                run_simple_reflex()
            elif choice == "2":
                print("\n🚀 Launching Goal-Based Agent...")
                run_goal_based()
            elif choice == "3":
                print("\n🚀 Launching Model-Based Agent...")
                run_model_based()
            elif choice == "4":
                print("\n🚀 Launching Utility-Based Agent...")
                run_utility_based()
            elif choice == "5":
                print("\n🚀 Launching Q-Learning Agent...")
                run_q_learning()
            elif choice == "6":
                print("\n👋 Goodbye! Thanks for using Snake AI Agents!")
                break
            else:
                print("\n❌ Invalid choice. Please enter 1-6.")
                input("\nPress Enter to continue...")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
