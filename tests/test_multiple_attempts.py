#!/usr/bin/env python3
"""
Test: Parsing Reasoning Model Output with Multiple Attempts

This demonstrates how the parser handles reasoning model outputs
where the model generates multiple attempts and we want the final answer.
"""

from output_logging.output_parser import parse_hanoi_output, parse_hanoi_output_lenient
from puzzles.hanoi_tower.automated_validator import AutomatedValidator


def test_reasoning_model_with_corrections():
    """Simulate a reasoning model that corrects itself."""
    print("\n" + "="*70)
    print("TEST: Reasoning Model with Self-Correction")
    print("="*70)

    # Realistic output where the model corrects itself
    reasoning_output = """
    Let me solve the 3-disk Tower of Hanoi puzzle.

    Initial state: Peg 0: [3,2,1], Peg 1: [], Peg 2: []
    Goal: Move all disks to Peg 2

    First attempt:
    moves=[[1,0,1],[2,0,2],[1,1,2],[3,0,1]]

    Wait, that won't work because I can't move disk 3 when disk 2 is still there.
    Let me reconsider...

    The correct approach is to:
    1. Move disk 1 to auxiliary peg (peg 2)
    2. Move disk 2 to auxiliary peg (peg 1)
    3. Move disk 1 onto disk 2
    4. Move disk 3 to destination (peg 2)
    5. Move disk 1 back to peg 0
    6. Move disk 2 to destination (peg 2)
    7. Move disk 1 to destination (peg 2)

    Final answer:
    moves=[[1,0,2],[2,0,1],[1,2,1],[3,0,2],[1,1,0],[2,1,2],[1,0,2]]
    """

    print("Reasoning Model Output:")
    print("-" * 70)
    print(reasoning_output)
    print("-" * 70)

    # Parse the output (should get the LAST moves= pattern)
    print("\nParsing output (expecting last match)...")
    moves, error = parse_hanoi_output(reasoning_output)

    if moves is None:
        print(f"✗ Parsing failed: {error}")
        return

    print(f"✓ Parsed {len(moves)} moves from LAST occurrence")
    print(f"  Moves: {moves}")

    # Validate
    print("\nValidating the solution...")
    validator = AutomatedValidator(n_disks=3)
    result = validator.validate_solution(moves, verbose=False)

    if result['is_valid'] and result['is_solved']:
        print(f"✓ Solution is VALID and COMPLETE")
        print(f"  Efficiency: {result['efficiency']:.1%}")
    else:
        print(f"✗ Solution is invalid or incomplete")
        print(f"  Error: {result['error_message']}")


def test_multiple_model_iterations():
    """Test output with multiple iterations."""
    print("\n" + "="*70)
    print("TEST: Multiple Iterations")
    print("="*70)

    output = """
    Iteration 1:
    moves=[[1,0,1]]

    Iteration 2:
    moves=[[1,0,2],[2,0,1]]

    Iteration 3 (complete):
    moves=[[1,0,2],[2,0,1],[1,2,1],[3,0,2],[1,1,0],[2,1,2],[1,0,2]]
    """

    print(f"Input has 3 'moves=' patterns")
    moves, error = parse_hanoi_output(output)

    if moves:
        print(f"✓ Correctly extracted last iteration: {len(moves)} moves")
        validator = AutomatedValidator(n_disks=3)
        result = validator.validate_solution(moves, verbose=False)
        print(f"  Valid: {result['is_valid']}, Solved: {result['is_solved']}")
    else:
        print(f"✗ Error: {error}")


def test_lenient_parser_multiple_patterns():
    """Test lenient parser with multiple patterns."""
    print("\n" + "="*70)
    print("TEST: Lenient Parser with Multiple Patterns")
    print("="*70)

    output = """
    Thinking process:

    First idea: [[1,0,1],[2,0,2]]
    - This won't work...

    Second idea: [[1,0,2],[2,0,1]]
    - Still incomplete...

    Final solution: [[1,0,2],[2,0,1],[1,2,1],[3,0,2],[1,1,0],[2,1,2],[1,0,2]]
    """

    print("Input has 3 list patterns (no 'moves=' label)")
    moves, error = parse_hanoi_output_lenient(output)

    if moves:
        print(f"✓ Correctly extracted last pattern: {len(moves)} moves")
        print(f"  Moves: {moves}")
        validator = AutomatedValidator(n_disks=3)
        result = validator.validate_solution(moves, verbose=False)
        print(f"  Valid: {result['is_valid']}, Solved: {result['is_solved']}")
    else:
        print(f"✗ Error: {error}")


def test_edge_case_nested_explanation():
    """Test with nested explanations."""
    print("\n" + "="*70)
    print("TEST: Edge Case - Nested Explanations")
    print("="*70)

    output = """
    Let me explain what DOESN'T work:

    If we tried moves=[[1,0,1],[3,0,2]], this would fail because
    disk 3 can't be moved while disk 2 is still on peg 0.

    The CORRECT solution is:
    moves=[[1,0,2],[2,0,1],[1,2,1],[3,0,2],[1,1,0],[2,1,2],[1,0,2]]

    This works because we follow the proper sequence.
    """

    print("Input has 2 'moves=' patterns (first is an example of what NOT to do)")
    moves, error = parse_hanoi_output(output)

    if moves:
        print(f"✓ Correctly extracted last (correct) solution: {len(moves)} moves")
        validator = AutomatedValidator(n_disks=3)
        result = validator.validate_solution(moves, verbose=False)
        print(f"  Valid: {result['is_valid']}, Solved: {result['is_solved']}")

        # Compare to what would happen if we took the first match
        print("\n  If we had taken the FIRST match instead:")
        validator2 = AutomatedValidator(n_disks=3)
        result2 = validator2.validate_solution([[1,0,1],[3,0,2]], verbose=False)
        print(f"  Valid: {result2['is_valid']}, Solved: {result2['is_solved']}")
        if not result2['is_valid']:
            print(f"  Error: {result2['error_message']}")
    else:
        print(f"✗ Error: {error}")


if __name__ == "__main__":
    test_reasoning_model_with_corrections()
    test_multiple_model_iterations()
    test_lenient_parser_multiple_patterns()
    test_edge_case_nested_explanation()

    print("\n" + "="*70)
    print("All tests completed!")
    print("="*70 + "\n")
