# Tower of Hanoi Simulator

A comprehensive Tower of Hanoi puzzle simulator designed for evaluating reasoning capabilities of AI models. This tool provides both interactive solving and automated validation of move sequences.

## Overview

The Tower of Hanoi is a classic mathematical puzzle consisting of three pegs and N disks of varying sizes. The puzzle starts with all disks stacked on the leftmost peg in descending order (largest at bottom). The goal is to move all disks to the rightmost peg while following specific rules.

### Rules

1. **Single Disk Movement**: Only one disk may be moved at a time
2. **Top Disk Access**: Only the topmost disk from any peg can be selected
3. **Size Ordering Constraint**: A larger disk may never be placed on top of a smaller disk

### State Representation

States are represented as lists of three pegs, with disks shown in bottom-to-top order:
- Initial state (N=3): `[[3, 2, 1], [], []]`
- Goal state (N=3): `[[], [], [3, 2, 1]]`

### Move Format

Moves are specified as `[disk, source_peg, destination_peg]`:
- Example: `[1, 0, 2]` means "move disk 1 from peg 0 to peg 2"
- Pegs are numbered 0, 1, 2 (left to right)
- Disks are numbered 1 (smallest) to N (largest)

## Features

### 1. State Representation (`hanoi_state.py`)
- Tracks current peg configuration
- Maintains move history
- Counts total moves
- Tracks solution status (is_solved flag)
- Validates all moves according to puzzle rules

### 2. Interactive Mode (`interactive_solver.py`)
- Step-by-step solving with immediate feedback
- Visual state display after each move
- Move history tracking
- Reset functionality
- Victory detection with efficiency metrics

### 3. Automated Validation (`automated_validator.py`)
- Batch validation of move sequences
- Detailed error reporting (identifies first invalid move)
- Efficiency analysis (compares to optimal solution)
- Support for JSON file input
- Comprehensive validation results

### 4. Main Program (`hanoi_simulator.py`)
- Unified interface for all features
- Command-line arguments support
- Interactive menu system
- Demo mode with examples

## Installation

No external dependencies required! Uses only Python standard library.

**Requirements:**
- Python 3.9 or higher

## Usage

### Quick Start

Run the main program:
```bash
python3 hanoi_simulator.py
```

This will present an interactive menu with options:
1. Interactive Solver - Solve puzzle step by step
2. Automated Validator - Validate a complete solution
3. Demo - See how the simulator works
4. Rules - Show puzzle rules and format
5. Create Sample File - Generate example solution JSON
6. Exit

### Command-Line Options

```bash
# Interactive mode
python3 hanoi_simulator.py --interactive
python3 hanoi_simulator.py -i

# Automated validation mode
python3 hanoi_simulator.py --validate
python3 hanoi_simulator.py -v

# Demo mode
python3 hanoi_simulator.py --demo
python3 hanoi_simulator.py -d

# Show rules
python3 hanoi_simulator.py --rules
python3 hanoi_simulator.py -r

# Create sample JSON file
python3 hanoi_simulator.py --sample
python3 hanoi_simulator.py -s
```

### Interactive Mode

```bash
python3 hanoi_simulator.py --interactive
```

Example session:
```
Enter number of disks (1-10): 3

Tower of Hanoi - 3 disks
Pegs (bottom → top):
  Peg 0: [3, 2, 1]
  Peg 1: []
  Peg 2: []

Enter move (or command): 1 0 2
✓ Move applied: Disk 1 from Peg 0 to Peg 2

Pegs (bottom → top):
  Peg 0: [3, 2]
  Peg 1: []
  Peg 2: [1]
```

**Commands:**
- `quit` or `q` - Exit the game
- `reset` or `r` - Reset to initial state
- `history` or `h` - Show move history

### Automated Validation

```bash
python3 hanoi_simulator.py --validate
```

You can either:
1. Enter moves manually one by one
2. Load moves from a JSON file

#### JSON File Format

```json
{
  "n_disks": 3,
  "description": "Optimal solution for 3-disk Tower of Hanoi",
  "moves": [
    [1, 0, 2],
    [2, 0, 1],
    [1, 2, 1],
    [3, 0, 2],
    [1, 1, 0],
    [2, 1, 2],
    [1, 0, 2]
  ]
}
```

Or simplified format:
```json
[
  [1, 0, 2],
  [2, 0, 1],
  [1, 2, 1],
  [3, 0, 2],
  [1, 1, 0],
  [2, 1, 2],
  [1, 0, 2]
]
```

## Programmatic Usage

### Basic State Management

```python
from hanoi_state import HanoiState

# Create a 3-disk puzzle
state = HanoiState(3)

# Display current state
state.display()

# Apply a move
success, message = state.apply_move(disk=1, from_peg=0, to_peg=2)
if success:
    print(f"Move successful! Moves so far: {state.num_moves}")
else:
    print(f"Invalid move: {message}")

# Check if solved
if state.is_solved:
    print("Puzzle solved!")

# Reset to initial state
state.reset()
```

### Automated Validation

```python
from automated_validator import AutomatedValidator

# Create validator for 3-disk puzzle
validator = AutomatedValidator(n_disks=3)

# Validate a sequence of moves
moves = [
    [1, 0, 2],
    [2, 0, 1],
    [1, 2, 1],
    [3, 0, 2],
    [1, 1, 0],
    [2, 1, 2],
    [1, 0, 2]
]

result = validator.validate_solution(moves, verbose=True)

# Check results
print(f"Valid: {result['is_valid']}")
print(f"Solved: {result['is_solved']}")
print(f"Total moves: {result['total_moves']}")
print(f"Efficiency: {result['efficiency']:.2%}")

# Validate from file
result = validator.validate_from_file("solution.json", verbose=True)
```

## Testing

Run the test suite:
```bash
python3 test_hanoi.py
```

The test suite includes:
- State initialization tests
- Valid move validation
- Invalid move detection
- Complete solution validation
- Incomplete solution handling
- Move parsing tests
- Different puzzle sizes
- JSON file validation
- State reset functionality

## Files

- `hanoi_state.py` - Core state representation and move validation
- `interactive_solver.py` - Interactive solving interface
- `automated_validator.py` - Batch move sequence validation
- `hanoi_simulator.py` - Main program and unified interface
- `test_hanoi.py` - Comprehensive test suite
- `sample_solution_3disk.json` - Example solution file

## Use Cases

### 1. Evaluating AI Reasoning Models

Use the automated validator to test if a reasoning model can:
- Generate valid move sequences
- Solve the puzzle completely
- Find optimal or near-optimal solutions

Example workflow:
1. Prompt AI model with puzzle description
2. Model generates move sequence
3. Save moves to JSON file
4. Validate with automated validator
5. Analyze efficiency and correctness

### 2. Educational Tool

Use interactive mode to:
- Teach puzzle-solving strategies
- Demonstrate algorithmic thinking
- Practice recursive problem-solving

### 3. Algorithm Testing

Use the state module to:
- Test automated solving algorithms
- Compare different solution strategies
- Benchmark algorithm performance

## Validation Results

The automated validator provides detailed results:

```python
{
    'is_valid': True/False,           # All moves are valid
    'is_solved': True/False,          # Puzzle is completely solved
    'total_moves': int,               # Number of moves in sequence
    'valid_moves': int,               # Number of valid moves applied
    'failed_at': int or None,         # Index of first failed move
    'error_message': str,             # Error description if any
    'optimal_moves': int,             # Optimal solution length (2^N - 1)
    'efficiency': float,              # Ratio of optimal to actual moves
    'final_state': List[List[int]],   # Final peg configuration
    'move_history': List[Tuple]       # Complete move history
}
```

## Optimal Solutions

The minimum number of moves to solve an N-disk puzzle is `2^N - 1`:

| Disks | Optimal Moves |
|-------|---------------|
| 1     | 1             |
| 2     | 3             |
| 3     | 7             |
| 4     | 15            |
| 5     | 31            |
| 6     | 63            |
| 7     | 127           |
| 8     | 255           |

## Example: 3-Disk Optimal Solution

```python
moves = [
    [1, 0, 2],  # Move disk 1: Peg 0 → Peg 2
    [2, 0, 1],  # Move disk 2: Peg 0 → Peg 1
    [1, 2, 1],  # Move disk 1: Peg 2 → Peg 1
    [3, 0, 2],  # Move disk 3: Peg 0 → Peg 2
    [1, 1, 0],  # Move disk 1: Peg 1 → Peg 0
    [2, 1, 2],  # Move disk 2: Peg 1 → Peg 2
    [1, 0, 2],  # Move disk 1: Peg 0 → Peg 2
]
```

State progression:
```
Initial:  [[3, 2, 1], [], []]
Step 1:   [[3, 2], [], [1]]
Step 2:   [[3], [2], [1]]
Step 3:   [[3], [2, 1], []]
Step 4:   [[], [2, 1], [3]]
Step 5:   [[1], [2], [3]]
Step 6:   [[1], [], [3, 2]]
Step 7:   [[], [], [3, 2, 1]]  ✓ SOLVED
```

## Architecture

The simulator follows a modular design:

```
┌─────────────────────────────────────────┐
│         hanoi_simulator.py              │
│         (Main Program)                  │
└─────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
┌───────▼──────────┐   ┌────────▼─────────┐
│ interactive_     │   │  automated_      │
│ solver.py        │   │  validator.py    │
└───────┬──────────┘   └────────┬─────────┘
        │                       │
        └───────────┬───────────┘
                    │
          ┌─────────▼──────────┐
          │   hanoi_state.py   │
          │  (Core Logic)      │
          └────────────────────┘
```

## License

This project is provided as-is for educational and research purposes.

## Contributing

This is a tool for evaluating reasoning models. Contributions that enhance:
- Validation capabilities
- Output formats for analysis
- Integration with ML frameworks
- Additional test cases

are welcome!

## Troubleshooting

**Issue**: Type errors with `|` operator
- **Solution**: Requires Python 3.9+. The code uses `Optional[T]` for compatibility.

**Issue**: JSON file not found
- **Solution**: Use absolute paths or ensure file is in current directory

**Issue**: Invalid move not detected
- **Solution**: Check that disk numbers and peg numbers are correct (0-indexed pegs, 1-indexed disks)

## Contact

For issues, questions, or suggestions, please refer to the project repository.
