#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify that all imports work correctly after restructuring.
Run this script to ensure the package structure is correct.
"""

def test_core_puzzle_imports():
    """Test that core puzzle imports work."""
    print("Testing core puzzle imports...")
    try:
        from puzzles.hanoi_tower import HanoiState, AutomatedValidator, InteractiveSolver
        print("✓ Successfully imported from puzzles.hanoi_tower")

        # Test instantiation
        state = HanoiState(3)
        print("✓ Successfully created HanoiState instance")

        validator = AutomatedValidator(3)
        print("✓ Successfully created AutomatedValidator instance")

        solver = InteractiveSolver(3)
        print("✓ Successfully created InteractiveSolver instance")

        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_logging_imports():
    """Test that logging module imports work."""
    print("\nTesting output_logging module imports...")
    try:
        from output_logging.output_logger import OutputLogger
        from output_logging.output_parser import parse_hanoi_output
        from output_logging.results_analyzer import ResultsAnalyzer
        print("✓ Successfully imported output_logging modules")

        # Test instantiation
        logger = OutputLogger("test_run", "test_model")
        print("✓ Successfully created OutputLogger instance")

        return True
    except ImportError as e:
        print(f"✗ Logging import failed: {e}")
        return False


def test_direct_module_imports():
    """Test that direct module imports work."""
    print("\nTesting direct module imports...")
    try:
        from puzzles.hanoi_tower.hanoi_state import HanoiState
        from puzzles.hanoi_tower.automated_validator import AutomatedValidator
        from puzzles.hanoi_tower.interactive_solver import InteractiveSolver
        print("✓ Successfully imported puzzle modules directly")
        return True
    except ImportError as e:
        print(f"✗ Direct import failed: {e}")
        return False


def test_simple_validation():
    """Test a simple validation to ensure everything works."""
    print("\nTesting simple validation...")
    try:
        from puzzles.hanoi_tower import AutomatedValidator

        validator = AutomatedValidator(3)

        # Optimal solution for 3 disks
        moves = [
            [1, 0, 2], [2, 0, 1], [1, 2, 1],
            [3, 0, 2], [1, 1, 0], [2, 1, 2],
            [1, 0, 2]
        ]

        result = validator.validate_solution(moves, verbose=False)

        if result['is_valid'] and result['is_solved']:
            print(f"✓ Validation successful! Solved in {result['total_moves']} moves")
            return True
        else:
            print(f"✗ Validation failed: {result.get('error_message', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"✗ Validation test failed: {e}")
        return False


def test_folder_structure():
    """Test that the folder structure is correct."""
    print("\nTesting folder structure...")
    import os
    required_folders = [
        'puzzles/hanoi_tower',
        'output_logging',
        'examples/hanoi_tower',
        'tests',
        'eval',
        'models'
    ]

    all_exist = True
    for folder in required_folders:
        if os.path.exists(folder):
            print(f"✓ {folder}/ exists")
        else:
            print(f"✗ {folder}/ missing")
            all_exist = False

    return all_exist


if __name__ == "__main__":
    print("="*70)
    print("PACKAGE STRUCTURE TEST")
    print("="*70)

    results = []
    results.append(test_folder_structure())
    results.append(test_core_puzzle_imports())
    results.append(test_logging_imports())
    results.append(test_direct_module_imports())
    results.append(test_simple_validation())

    print("\n" + "="*70)
    if all(results):
        print("✓ ALL TESTS PASSED!")
        print("The package structure is correct and all imports work.")
    else:
        print("✗ SOME TESTS FAILED")
        print("Please check the package structure.")
    print("="*70)
