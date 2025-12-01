# Quick Reference: Using Tower of Hanoi Simulator in Your Script

## Simplest Usage

```python
from automated_validator import AutomatedValidator

# 1. Initialize validator for N=3 disks
validator = AutomatedValidator(n_disks=3)

# 2. Define your moves
moves = [
    [1, 0, 2],  # [disk, source_peg, dest_peg]
    [2, 0, 1],
    [1, 2, 1],
    [3, 0, 2],
    [1, 1, 0],
    [2, 1, 2],
    [1, 0, 2]
]

# 3. Validate
result = validator.validate_solution(moves, verbose=False)

# 4. Check result
if result['is_valid'] and result['is_solved']:
    print(f"✓ Valid solution! Used {result['total_moves']} moves")
else:
    print(f"✗ Invalid: {result['error_message']}")
```

## Result Dictionary

The `validate_solution()` method returns a dictionary with:

```python
{
    'is_valid': bool,        # Are all moves valid?
    'is_solved': bool,       # Is puzzle completely solved?
    'total_moves': int,      # Number of moves in sequence
    'valid_moves': int,      # Number of valid moves applied
    'failed_at': int|None,   # Index of first failed move (or None)
    'error_message': str,    # Error description (if any)
    'optimal_moves': int,    # Optimal solution length (2^N - 1)
    'efficiency': float,     # Ratio: optimal / actual moves
    'final_state': list,     # Final peg configuration
    'move_history': list     # All moves applied
}
```

## Common Patterns

### Pattern 1: Quick Validation

```python
from automated_validator import AutomatedValidator

def is_valid_solution(n_disks, moves):
    validator = AutomatedValidator(n_disks)
    result = validator.validate_solution(moves, verbose=False)
    return result['is_valid'] and result['is_solved']

# Usage
moves = [[1, 0, 2], [2, 0, 1], ...]
if is_valid_solution(3, moves):
    print("Solution is correct!")
```

### Pattern 2: Step-by-Step Validation

```python
from hanoi_state import HanoiState

state = HanoiState(n_disks=3)

for disk, from_peg, to_peg in moves:
    success, msg = state.apply_move(disk, from_peg, to_peg)
    if not success:
        print(f"Error: {msg}")
        break

if state.is_solved:
    print(f"Solved in {state.num_moves} moves!")
```

### Pattern 3: Evaluate AI Output

```python
from automated_validator import AutomatedValidator

def evaluate_ai_model(n_disks, ai_moves):
    validator = AutomatedValidator(n_disks)
    result = validator.validate_solution(ai_moves, verbose=False)

    return {
        'correct': result['is_valid'] and result['is_solved'],
        'efficiency': result['efficiency'],
        'moves': result['total_moves'],
        'error': result['error_message'] if not result['is_valid'] else None
    }

# Usage
ai_solution = [[1, 0, 2], [2, 0, 1], ...]  # From your AI model
score = evaluate_ai_model(3, ai_solution)
print(f"Efficiency: {score['efficiency']:.1%}")
```

### Pattern 4: Batch Testing

```python
from automated_validator import AutomatedValidator

solutions = {
    "Model_A": [[1, 0, 2], ...],
    "Model_B": [[1, 0, 1], ...],
    "Model_C": [[1, 0, 2], ...],
}

for name, moves in solutions.items():
    validator = AutomatedValidator(n_disks=3)
    result = validator.validate_solution(moves, verbose=False)

    status = "✓" if (result['is_valid'] and result['is_solved']) else "✗"
    print(f"{name}: {status} ({result['total_moves']} moves, {result['efficiency']:.0%} efficient)")
```

## Key Points

1. **Move Format**: `[disk, source_peg, dest_peg]`
   - Pegs: 0, 1, 2 (left to right)
   - Disks: 1 (smallest) to N (largest)

2. **State Format**: `[[peg0], [peg1], [peg2]]`
   - Disks in bottom-to-top order
   - Example: `[[3, 2, 1], [], []]` = all disks on peg 0

3. **Optimal Moves**: `2^N - 1`
   - N=3: 7 moves
   - N=4: 15 moves
   - N=5: 31 moves

## Import Options

```python
# For batch validation (recommended for AI evaluation)
from automated_validator import AutomatedValidator

# For step-by-step control
from hanoi_state import HanoiState

# For interactive CLI use
from interactive_solver import InteractiveSolver
```

## See Also

- `example_usage.py` - Complete examples
- `test_hanoi.py` - Test suite with more examples
- `README.md` - Full documentation
