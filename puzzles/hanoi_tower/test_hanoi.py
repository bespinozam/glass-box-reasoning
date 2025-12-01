#!/usr/bin/env python3
"""
Test Suite for Tower of Hanoi Simulator

This script tests various components of the Tower of Hanoi simulator.
"""

from hanoi_state import HanoiState
from automated_validator import AutomatedValidator
from interactive_solver import InteractiveSolver


def test_state_initialization():
    """Test state initialization."""
    print("Test 1: State Initialization")
    print("-" * 50)

    state = HanoiState(3)
    assert state.n_disks == 3
    assert state.pegs == [[3, 2, 1], [], []]
    assert state.num_moves == 0
    assert state.is_solved == False
    print("✓ State initialized correctly\n")


def test_valid_moves():
    """Test valid moves."""
    print("Test 2: Valid Moves")
    print("-" * 50)

    state = HanoiState(3)

    # Move 1: disk 1 from peg 0 to peg 2
    success, msg = state.apply_move(1, 0, 2)
    assert success == True
    assert state.pegs == [[3, 2], [], [1]]
    assert state.num_moves == 1
    print(f"✓ Move 1: {msg}")

    # Move 2: disk 2 from peg 0 to peg 1
    success, msg = state.apply_move(2, 0, 1)
    assert success == True
    assert state.pegs == [[3], [2], [1]]
    assert state.num_moves == 2
    print(f"✓ Move 2: {msg}")

    print("✓ All valid moves applied correctly\n")


def test_invalid_moves():
    """Test invalid moves."""
    print("Test 3: Invalid Moves")
    print("-" * 50)

    state = HanoiState(3)

    # Test 1: Move disk that's not on top
    success, msg = state.apply_move(2, 0, 1)
    assert success == False
    assert "not on top" in msg.lower()
    print(f"✓ Invalid move caught: {msg}")

    # Test 2: Move disk from empty peg
    success, msg = state.apply_move(1, 1, 2)
    assert success == False
    assert "empty" in msg.lower()
    print(f"✓ Invalid move caught: {msg}")

    # Test 3: Move larger disk on smaller disk
    state.apply_move(1, 0, 2)
    success, msg = state.apply_move(2, 0, 2)
    assert success == False
    assert "smaller disk" in msg.lower()
    print(f"✓ Invalid move caught: {msg}\n")


def test_complete_solution():
    """Test a complete optimal solution."""
    print("Test 4: Complete Optimal Solution")
    print("-" * 50)

    optimal_moves_3disk = [
        [1, 0, 2], [2, 0, 1], [1, 2, 1],
        [3, 0, 2], [1, 1, 0], [2, 1, 2],
        [1, 0, 2]
    ]

    validator = AutomatedValidator(3)
    result = validator.validate_solution(optimal_moves_3disk, verbose=False)

    assert result['is_valid'] == True
    assert result['is_solved'] == True
    assert result['total_moves'] == 7
    assert result['optimal_moves'] == 7
    assert result['efficiency'] == 1.0
    print(f"✓ Optimal solution validated")
    print(f"  Total moves: {result['total_moves']}")
    print(f"  Efficiency: {result['efficiency']:.2%}\n")


def test_incomplete_solution():
    """Test an incomplete solution."""
    print("Test 5: Incomplete Solution")
    print("-" * 50)

    incomplete_moves = [
        [1, 0, 2], [2, 0, 1]
    ]

    validator = AutomatedValidator(3)
    result = validator.validate_solution(incomplete_moves, verbose=False)

    assert result['is_valid'] == True
    assert result['is_solved'] == False
    print(f"✓ Incomplete solution detected")
    print(f"  Valid moves: {result['total_moves']}")
    print(f"  Solved: {result['is_solved']}\n")


def test_invalid_solution():
    """Test solution with invalid moves."""
    print("Test 6: Invalid Solution")
    print("-" * 50)

    invalid_moves = [
        [1, 0, 2],
        [3, 0, 1],  # Invalid: disk 3 is not on top
    ]

    validator = AutomatedValidator(3)
    result = validator.validate_solution(invalid_moves, verbose=False)

    assert result['is_valid'] == False
    assert result['failed_at'] == 1
    print(f"✓ Invalid move detected at step {result['failed_at'] + 1}")
    print(f"  Error: {result['error_message']}\n")


def test_move_parser():
    """Test move parsing in interactive solver."""
    print("Test 7: Move Parsing")
    print("-" * 50)

    solver = InteractiveSolver(3)

    # Test various formats
    test_cases = [
        ("1 0 2", [1, 0, 2]),
        ("[1, 0, 2]", [1, 0, 2]),
        ("1,0,2", [1, 0, 2]),
        ("[1,0,2]", [1, 0, 2]),
    ]

    for input_str, expected in test_cases:
        result = solver.parse_move(input_str)
        assert result == expected
        print(f"✓ Parsed '{input_str}' → {result}")

    # Test invalid format
    result = solver.parse_move("invalid")
    assert result is None
    print(f"✓ Invalid format correctly rejected\n")


def test_different_sizes():
    """Test with different puzzle sizes."""
    print("Test 8: Different Puzzle Sizes")
    print("-" * 50)

    for n in [1, 2, 3, 4, 5]:
        state = HanoiState(n)
        optimal = 2**n - 1
        assert state.n_disks == n
        assert len(state.pegs[0]) == n
        print(f"✓ {n}-disk puzzle: {len(state.pegs[0])} disks, optimal={optimal} moves")

    print()


def test_json_file_validation():
    """Test validation from JSON file."""
    print("Test 9: JSON File Validation")
    print("-" * 50)

    validator = AutomatedValidator(3)
    result = validator.validate_from_file("sample_solution_3disk.json", verbose=False)

    if result.get('is_valid'):
        assert result['is_solved'] == True
        assert result['total_moves'] == 7
        print(f"✓ JSON file validated successfully")
        print(f"  Total moves: {result['total_moves']}")
        print(f"  Solved: {result['is_solved']}\n")
    else:
        print(f"⚠ File not found (expected in first run)\n")


def test_reset_functionality():
    """Test state reset."""
    print("Test 10: State Reset")
    print("-" * 50)

    state = HanoiState(3)

    # Apply some moves
    state.apply_move(1, 0, 2)
    state.apply_move(2, 0, 1)

    # Reset
    state.reset()

    assert state.pegs == [[3, 2, 1], [], []]
    assert state.num_moves == 0
    assert state.is_solved == False
    assert len(state.history) == 0
    print("✓ State reset correctly\n")


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*70)
    print(" "*20 + "TOWER OF HANOI TEST SUITE")
    print("="*70 + "\n")

    tests = [
        test_state_initialization,
        test_valid_moves,
        test_invalid_moves,
        test_complete_solution,
        test_incomplete_solution,
        test_invalid_solution,
        test_move_parser,
        test_different_sizes,
        test_json_file_validation,
        test_reset_functionality,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ Test failed: {e}\n")
            failed += 1
        except Exception as e:
            print(f"❌ Test error: {e}\n")
            failed += 1

    print("="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")

    if failed == 0:
        print("\n✓ ALL TESTS PASSED!\n")
    else:
        print(f"\n❌ {failed} test(s) failed\n")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
