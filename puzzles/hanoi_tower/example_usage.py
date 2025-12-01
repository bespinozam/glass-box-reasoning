#!/usr/bin/env python3
"""
Example: Using Tower of Hanoi Simulator as a Library

This script demonstrates how to use the Tower of Hanoi simulator
programmatically from another Python script.
"""

from automated_validator import AutomatedValidator
from hanoi_state import HanoiState


def example_1_simple_validation():
    """Example 1: Simple validation of a move sequence."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Simple Validation")
    print("="*70)

    # Initialize validator for 3-disk puzzle
    validator = AutomatedValidator(n_disks=3)

    # Define your moves
    moves = [
        [1, 0, 2],  # Move disk 1 from peg 0 to peg 2
        [2, 0, 1],  # Move disk 2 from peg 0 to peg 1
        [1, 2, 1],  # Move disk 1 from peg 2 to peg 1
        [3, 0, 2],  # Move disk 3 from peg 0 to peg 2
        [1, 1, 0],  # Move disk 1 from peg 1 to peg 0
        [2, 1, 2],  # Move disk 2 from peg 1 to peg 2
        [1, 0, 2],  # Move disk 1 from peg 0 to peg 2
    ]

    # Validate the moves (verbose=False for programmatic use)
    result = validator.validate_solution(moves, verbose=False)

    # Check the result
    if result['is_valid'] and result['is_solved']:
        print(f"✓ Solution is VALID and COMPLETE")
        print(f"  Total moves: {result['total_moves']}")
        print(f"  Optimal moves: {result['optimal_moves']}")
        print(f"  Efficiency: {result['efficiency']:.1%}")
    else:
        print(f"❌ Solution is invalid")
        print(f"  Error: {result['error_message']}")


def example_2_checking_invalid_solution():
    """Example 2: Detect invalid moves."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Invalid Move Detection")
    print("="*70)

    validator = AutomatedValidator(n_disks=3)

    # This sequence has an invalid move
    moves = [
        [1, 0, 2],
        [3, 0, 1],  # INVALID: disk 3 is not on top
    ]

    result = validator.validate_solution(moves, verbose=False)

    if not result['is_valid']:
        print(f"❌ Invalid move detected!")
        print(f"  Failed at step: {result['failed_at'] + 1}")
        print(f"  Error: {result['error_message']}")
        print(f"  Valid moves before failure: {result['valid_moves']}")


def example_3_step_by_step_validation():
    """Example 3: Step-by-step validation using HanoiState directly."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Step-by-Step Validation")
    print("="*70)

    # Initialize state for 3-disk puzzle
    state = HanoiState(n_disks=3)

    print(f"Initial state: {state.pegs}")

    # Define moves to apply
    moves = [
        [1, 0, 2],
        [2, 0, 1],
        [1, 2, 1],
    ]

    # Apply moves one by one
    for i, (disk, from_peg, to_peg) in enumerate(moves, 1):
        success, message = state.apply_move(disk, from_peg, to_peg)

        if success:
            print(f"Step {i}: Move disk {disk}: peg {from_peg} → peg {to_peg}")
            print(f"  State: {state.pegs}")
        else:
            print(f"Step {i}: FAILED - {message}")
            break

    print(f"\nTotal moves: {state.num_moves}")
    print(f"Solved: {state.is_solved}")


def example_4_batch_check_multiple_solutions():
    """Example 4: Check multiple solutions (e.g., from different AI models)."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Batch Validation of Multiple Solutions")
    print("="*70)

    # Simulate solutions from different AI models
    solutions = {
        "Model_A": [
            [1, 0, 2], [2, 0, 1], [1, 2, 1],
            [3, 0, 2], [1, 1, 0], [2, 1, 2], [1, 0, 2]
        ],
        "Model_B": [
            [1, 0, 1], [2, 0, 2], [1, 1, 2],
            [3, 0, 1], [1, 2, 0], [2, 2, 1], [1, 0, 1]
        ],
        "Model_C": [
            [1, 0, 2], [2, 0, 1],  # Incomplete solution
        ],
    }

    results = {}

    for model_name, moves in solutions.items():
        validator = AutomatedValidator(n_disks=3)
        result = validator.validate_solution(moves, verbose=False)
        results[model_name] = result

    # Print comparison
    print(f"\n{'Model':<12} {'Valid':<8} {'Solved':<8} {'Moves':<8} {'Efficiency':<12}")
    print("-" * 60)

    for model_name, result in results.items():
        valid = "✓" if result['is_valid'] else "✗"
        solved = "✓" if result['is_solved'] else "✗"
        moves = result['total_moves']
        efficiency = f"{result['efficiency']:.1%}" if result['is_valid'] else "N/A"

        print(f"{model_name:<12} {valid:<8} {solved:<8} {moves:<8} {efficiency:<12}")


def example_5_get_detailed_info():
    """Example 5: Get detailed information from validation."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Detailed Validation Information")
    print("="*70)

    validator = AutomatedValidator(n_disks=3)

    moves = [
        [1, 0, 2], [2, 0, 1], [1, 2, 1],
        [3, 0, 2], [1, 1, 0], [2, 1, 2], [1, 0, 2]
    ]

    result = validator.validate_solution(moves, verbose=False)

    # Access all available information
    print(f"Validation Result Details:")
    print(f"  is_valid: {result['is_valid']}")
    print(f"  is_solved: {result['is_solved']}")
    print(f"  total_moves: {result['total_moves']}")
    print(f"  valid_moves: {result['valid_moves']}")
    print(f"  failed_at: {result['failed_at']}")
    print(f"  error_message: {result['error_message']}")
    print(f"  optimal_moves: {result['optimal_moves']}")
    print(f"  efficiency: {result['efficiency']:.2%}")
    print(f"  final_state: {result['final_state']}")
    print(f"  move_history: {result['move_history']}")


def example_6_validate_from_json():
    """Example 6: Validate solution from JSON file."""
    print("\n" + "="*70)
    print("EXAMPLE 6: Validate from JSON File")
    print("="*70)

    validator = AutomatedValidator(n_disks=3)

    # Validate from the sample JSON file
    result = validator.validate_from_file("sample_solution_3disk.json", verbose=False)

    if result.get('is_valid'):
        print(f"✓ JSON file validation successful")
        print(f"  File contains: {result['total_moves']} moves")
        print(f"  Solution is: {'COMPLETE' if result['is_solved'] else 'INCOMPLETE'}")
        print(f"  Efficiency: {result['efficiency']:.1%}")
    else:
        print(f"❌ Validation failed: {result.get('error_message')}")


def example_7_practical_use_case():
    """Example 7: Practical use case - Evaluate AI model output."""
    print("\n" + "="*70)
    print("EXAMPLE 7: Practical Use Case - Evaluate AI Model Output")
    print("="*70)

    def evaluate_ai_solution(n_disks, ai_generated_moves):
        """
        Evaluate a solution generated by an AI model.

        Args:
            n_disks: Number of disks in the puzzle
            ai_generated_moves: List of moves generated by AI

        Returns:
            Dictionary with evaluation metrics
        """
        validator = AutomatedValidator(n_disks=n_disks)
        result = validator.validate_solution(ai_generated_moves, verbose=False)

        # Return simplified evaluation
        return {
            'valid': result['is_valid'],
            'solved': result['is_solved'],
            'moves': result['total_moves'],
            'optimal': result['optimal_moves'],
            'efficiency': result['efficiency'],
            'error': result['error_message'] if not result['is_valid'] else None
        }

    # Simulate AI model output
    ai_moves = [
        [1, 0, 2], [2, 0, 1], [1, 2, 1],
        [3, 0, 2], [1, 1, 0], [2, 1, 2], [1, 0, 2]
    ]

    # Evaluate
    evaluation = evaluate_ai_solution(n_disks=3, ai_generated_moves=ai_moves)

    # Report
    print(f"AI Model Evaluation:")
    print(f"  Valid Solution: {evaluation['valid']}")
    print(f"  Puzzle Solved: {evaluation['solved']}")
    print(f"  Moves Used: {evaluation['moves']} (optimal: {evaluation['optimal']})")
    print(f"  Efficiency: {evaluation['efficiency']:.1%}")

    if evaluation['error']:
        print(f"  Error: {evaluation['error']}")

    # Grade the solution
    if not evaluation['valid']:
        grade = "F - Invalid solution"
    elif not evaluation['solved']:
        grade = "D - Valid moves but incomplete"
    elif evaluation['efficiency'] == 1.0:
        grade = "A+ - Optimal solution!"
    elif evaluation['efficiency'] >= 0.8:
        grade = "A - Excellent"
    elif evaluation['efficiency'] >= 0.6:
        grade = "B - Good"
    else:
        grade = "C - Needs improvement"

    print(f"  Grade: {grade}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print(" " * 15 + "TOWER OF HANOI - USAGE EXAMPLES")
    print("="*70)

    # Run all examples
    example_1_simple_validation()
    example_2_checking_invalid_solution()
    example_3_step_by_step_validation()
    example_4_batch_check_multiple_solutions()
    example_5_get_detailed_info()
    example_6_validate_from_json()
    example_7_practical_use_case()

    print("\n" + "="*70)
    print("All examples completed!")
    print("="*70 + "\n")
