#!/usr/bin/env python3
"""
Example: Parsing and Validating Reasoning Model Output

This script demonstrates how to parse reasoning model output and validate
the extracted moves using the Tower of Hanoi validator.
"""

from output_parser import parse_hanoi_output, parse_hanoi_output_lenient, validate_and_parse
from automated_validator import AutomatedValidator


def example_parse_and_validate():
    """Example: Parse model output and validate the solution."""
    print("\n" + "="*70)
    print("EXAMPLE: Parse and Validate Reasoning Model Output")
    print("="*70)

    # Simulate reasoning model output with line breaks
    model_output = """
    I'll solve the 3-disk Tower of Hanoi puzzle.

    After analyzing the problem, here is my solution:

    moves=[
        [1, 0, 2],
        [2, 0, 1],
        [1, 2, 1],
        [3, 0, 2],
        [1, 1, 0],
        [2, 1, 2],
        [1, 0, 2]
    ]

    This solution moves all disks from peg 0 to peg 2.
    """

    print("Reasoning Model Output:")
    print("-" * 70)
    print(model_output)
    print("-" * 70)

    # Step 1: Parse the output
    print("\nStep 1: Parsing the output...")
    moves, error = parse_hanoi_output(model_output)

    if moves is None:
        print(f"✗ Parsing failed: {error}")
        return

    print(f"✓ Successfully parsed {len(moves)} moves")
    print(f"  Moves: {moves}")

    # Step 2: Validate the moves
    print("\nStep 2: Validating the moves...")
    validator = AutomatedValidator(n_disks=3)
    result = validator.validate_solution(moves, verbose=False)

    # Step 3: Display results
    print("\nValidation Results:")
    print("-" * 70)
    if result['is_valid'] and result['is_solved']:
        print(f"✓ Solution is VALID and COMPLETE")
        print(f"  Total moves: {result['total_moves']}")
        print(f"  Optimal moves: {result['optimal_moves']}")
        print(f"  Efficiency: {result['efficiency']:.1%}")

        if result['efficiency'] == 1.0:
            print(f"  ⭐ OPTIMAL SOLUTION!")
    elif result['is_valid']:
        print(f"⚠ Moves are valid but puzzle is NOT solved")
        print(f"  Total moves: {result['total_moves']}")
    else:
        print(f"✗ Invalid solution")
        print(f"  Failed at move: {result['failed_at'] + 1}")
        print(f"  Error: {result['error_message']}")


def example_batch_processing():
    """Example: Batch process multiple model outputs."""
    print("\n" + "="*70)
    print("EXAMPLE: Batch Processing Multiple Model Outputs")
    print("="*70)

    # Simulate outputs from different models
    model_outputs = {
        "Model A": """
        Solution: moves=[[1,0,2],[2,0,1],[1,2,1],[3,0,2],[1,1,0],[2,1,2],[1,0,2]]
        """,

        "Model B": """
        Here's my answer:
        moves=[
            [1, 0, 1],
            [2, 0, 2],
            [1, 1, 2],
            [3, 0, 1],
            [1, 2, 0],
            [2, 2, 1],
            [1, 0, 1]
        ]
        """,

        "Model C": """
        The solution is: [[1,0,2],[2,0,1],[1,2,1]]
        """,  # Incomplete solution, no 'moves=' label
    }

    results = {}

    for model_name, output in model_outputs.items():
        print(f"\n{model_name}:")
        print("-" * 40)

        # Parse (using lenient parser to handle missing 'moves=' label)
        moves, error = parse_hanoi_output_lenient(output)

        if moves is None:
            print(f"  ✗ Parsing failed: {error}")
            results[model_name] = {'error': error}
            continue

        # Validate
        validator = AutomatedValidator(n_disks=3)
        result = validator.validate_solution(moves, verbose=False)

        results[model_name] = result

        # Display
        if result['is_valid'] and result['is_solved']:
            print(f"  ✓ Valid & Complete")
            print(f"  Moves: {result['total_moves']}, Efficiency: {result['efficiency']:.1%}")
        elif result['is_valid']:
            print(f"  ⚠ Valid but incomplete")
            print(f"  Moves: {result['total_moves']}")
        else:
            print(f"  ✗ Invalid")
            print(f"  Error: {result['error_message']}")

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"\n{'Model':<15} {'Status':<15} {'Moves':<10} {'Efficiency':<12}")
    print("-" * 70)

    for model_name, result in results.items():
        if 'error' in result:
            print(f"{model_name:<15} {'Parse Error':<15} {'-':<10} {'-':<12}")
        else:
            status = 'Valid+Solved' if result['is_solved'] else 'Invalid'
            moves = result['total_moves']
            efficiency = f"{result['efficiency']:.1%}" if result['is_valid'] else 'N/A'
            print(f"{model_name:<15} {status:<15} {moves:<10} {efficiency:<12}")


def example_with_validation_details():
    """Example: Parse and validate with detailed checking."""
    print("\n" + "="*70)
    print("EXAMPLE: Parse with Validation Details")
    print("="*70)

    model_output = """
    My solution:
    moves=[[1, 0, 2], [5, 0, 1], [1, 2, 1]]
    """

    print("Model Output:")
    print(model_output)
    print("\nParsing and validating...")

    # Use the validate_and_parse function for comprehensive checking
    result = validate_and_parse(model_output, n_disks=3)

    print("\nResults:")
    print(f"  Success: {result['success']}")
    print(f"  Moves: {result['moves']}")
    print(f"  Error: {result['error']}")

    if result['warnings']:
        print(f"\n  Warnings:")
        for warning in result['warnings']:
            print(f"    - {warning}")

    # Even if there are warnings, we can try to validate
    if result['success']:
        print("\nAttempting full validation...")
        validator = AutomatedValidator(n_disks=3)
        validation_result = validator.validate_solution(result['moves'], verbose=False)

        print(f"  Valid: {validation_result['is_valid']}")
        print(f"  Error: {validation_result['error_message']}")


if __name__ == "__main__":
    example_parse_and_validate()
    example_batch_processing()
    example_with_validation_details()

    print("\n" + "="*70)
    print("All examples completed!")
    print("="*70 + "\n")
