# Snake Game AI Agents

A collection of intelligent agents that play the classic Snake game using different AI approaches. This project demonstrates various AI techniques from simple reflex agents to reinforcement learning.

## 🎮 Game Overview

The Snake game implementation includes multiple AI agents:

- **Simple Reflex Agent**: Direct reactions to immediate perceptions
- **Goal-Based Agent**: Uses A* pathfinding algorithm
- **Model-Based Agent**: Maintains internal world model with prediction
- **Utility-Based Agent**: Maximizes expected utility across multiple criteria
- **Q-Learning Agent**: Reinforcement learning with Q-table

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd SnakeAgents
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  
   On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   
   Or install pygame directly:
   ```bash
   pip install pygame
   ```

### Running the Game

Execute the main runner script:
```bash
python run_agents.py
```

This will display a menu where you can choose which AI agent to run.

### Running Individual Agents

You can also run agents directly:

```bash
# Simple Reflex Agent
python agents/simple_reflex/simple_reflex_player.py

# Goal-Based Agent
python agents/goal_based/goal_based_player.py

# Model-Based Agent
python agents/model_based/model_based_player.py

# Utility-Based Agent
python agents/utility_based/utility_based_player.py

# Q-Learning Agent
python agents/q_learning/trained_player.py
```

## 📁 Project Structure

```
├── agents/                    # AI agent implementations
│   ├── simple_reflex/        # Simple reflex agent
│   ├── goal_based/           # Goal-based agent with A*
│   ├── model_based/          # Model-based agent
│   ├── utility_based/        # Utility-based agent
│   └── q_learning/           # Q-learning agent
├── core_game/                # Core game engine
├── resources/                # Game assets (images, sounds)
├── reports/                  # Performance reports
├── ss/                       # Screenshots
└── run_agents.py            # Main runner script
```

## 🤖 Agent Details

### Simple Reflex Agent
- **Strategy**: Direct reactions to current state
- **Complexity**: Low
- **Best for**: Understanding basic AI concepts

### Goal-Based Agent
- **Strategy**: A* pathfinding to reach food
- **Complexity**: Medium
- **Best for**: Learning search algorithms

### Model-Based Agent
- **Strategy**: Maintains world model and predicts outcomes
- **Complexity**: High
- **Best for**: Understanding predictive AI

### Utility-Based Agent
- **Strategy**: Evaluates multiple criteria and maximizes utility
- **Complexity**: High
- **Best for**: Multi-objective optimization

### Q-Learning Agent
- **Strategy**: Reinforcement learning with experience replay
- **Complexity**: Very High
- **Best for**: Machine learning applications

## 🎯 Training Q-Learning Agent

To train the Q-learning agent:
```bash
python agents/q_learning/auto_trainer.py
```

Training data is saved to `trained_q_table.json` and can be used by the trained player.

## 🎮 Controls

- **ESC**: Quit game
- **Space**: Pause/Resume (in some modes)

## 📊 Performance

Check the `reports/` directory for detailed performance analysis of each agent.

## 🛠️ Development

### Adding New Agents

1. Create a new directory in `agents/`
2. Implement your agent following the existing pattern
3. Add the agent to `run_agents.py`

### Dependencies

- `pygame`: Game engine and graphics
- `json`: For saving/loading training data (Q-learning)
- Standard Python libraries: `os`, `sys`, `math`, `random`, `time`
 

## Agent Types

### 1. Simple Reflex Agent
- Location: `agents/simple_reflex/`
- Basic reactive behavior based on immediate perceptions
- No internal state or planning

### 2. Goal-Based Agent  
- Location: `agents/goal_based/`
- Uses goal information to guide decision making
- Plans actions to achieve specific objectives

### 3. Model-Based Agent
- Location: `agents/model_based/`
- Maintains internal model of the world
- Uses model for planning and decision making

### 4. Utility-Based Agent
- Location: `agents/utility_based/`
- Uses utility functions to evaluate outcomes
- Makes decisions based on expected utility

### 5. Q-Learning Agent
- Location: `agents/q_learning/`
- Reinforcement learning using Q-learning algorithm
- Learns optimal policy through trial and error
- Includes both training and playing scripts

## Usage

### Running Q-Learning Training
```bash
cd agents/q_learning
python auto_trainer.py
```

### Playing with Trained Agent
```bash
cd agents/q_learning  
python trained_player.py
```

### Screenshot Capture for Documentation
```bash
cd agents/q_learning
python screenshot_trainer.py  # Training with overlay
python screenshot_player.py   # Playing with stats
```

## Core Game Engine
The main Snake game implementation is in `core_game/source.py` and provides:
- Game mechanics (movement, collision detection, scoring)
- Rendering and display
- External agent interface
- Audio and visual effects

## Performance
The Q-learning agent shows clear improvement:
- Training performance: ~0.30 average score
- Trained performance: Consistently achieves scores of 7+
- Learning uses epsilon-greedy strategy with decay (0.9 → 0.01)

## Documentation
Full technical report and analysis available in `reports/snake_agents_report.tex`
