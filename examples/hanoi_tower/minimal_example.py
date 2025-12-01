#!/usr/bin/env python3
"""
Minimal example: How to use Tower of Hanoi validator in your script.

Copy this into your own script and modify as needed.
"""

from puzzles.hanoi_tower.automated_validator import AutomatedValidator

if __name__ == "__main__":
    # Initialize for N=3 disks
    validator = AutomatedValidator(n_disks=3)

    # Your moves (example: optimal solution for N=3)
    moves = [
        [1, 0, 2],  # Move disk 1 from peg 0 to peg 2
        [2, 0, 1],  # Move disk 2 from peg 0 to peg 1
        [1, 2, 1],  # Move disk 1 from peg 2 to peg 1
        [3, 0, 2],  # Move disk 3 from peg 0 to peg 2
        [1, 1, 0],  # Move disk 1 from peg 1 to peg 0
        [2, 1, 2],  # Move disk 2 from peg 1 to peg 2
        [1, 0, 2],  # Move disk 1 from peg 0 to peg 2
    ]

    # Validate (verbose=False for programmatic use)
    result = validator.validate_solution(moves, verbose=False)

    # Check if valid and solved
    if result['is_valid'] and result['is_solved']:
        print(f"✓ Valid solution!")
        print(f"  Moves: {result['total_moves']}")
        print(f"  Efficiency: {result['efficiency']:.1%}")
    else:
        print(f"✗ Invalid solution")
        if not result['is_valid']:
            print(f"  Error at step {result['failed_at'] + 1}: {result['error_message']}")
        elif not result['is_solved']:
            print(f"  Puzzle not solved (only {result['total_moves']} moves applied)")

    print(result)