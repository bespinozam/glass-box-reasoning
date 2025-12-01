#!/usr/bin/env python3
"""
Tower of Hanoi Interactive Simulator

A simplified interactive simulator for the Tower of Hanoi puzzle.
Use this to solve the puzzle step-by-step or quickly validate solutions.

For more examples and advanced usage, see the examples/ folder.
"""

import sys
import argparse
from puzzles.hanoi_tower.hanoi_state import HanoiState
from puzzles.hanoi_tower.interactive_solver import InteractiveSolver
from puzzles.hanoi_tower.automated_validator import AutomatedValidator


def print_banner():
    """Print the application banner."""
    print("\n" + "="*70)
    print(" "*20 + "TOWER OF HANOI SIMULATOR")
    print("="*70)
    print("\n Interactive puzzle solver and validator\n")


def print_rules():
    """Print the rules of Tower of Hanoi."""
    print("\n" + "-"*70)
    print("TOWER OF HANOI RULES:")
    print("-"*70)
    print("""
The puzzle consists of three pegs (0, 1, 2) and N disks of varying sizes.

OBJECTIVE:
  Move all disks from peg 0 to peg 2, maintaining size order.

CONSTRAINTS:
  1. Single Disk Movement: Only one disk may be moved at a time
  2. Top Disk Access: Only the topmost disk from any peg can be moved
  3. Size Ordering: A larger disk may never be placed on a smaller disk

INITIAL STATE (N=3):
  Peg 0: [3, 2, 1]  (largest to smallest)
  Peg 1: []
  Peg 2: []

GOAL STATE (N=3):
  Peg 0: []
  Peg 1: []
  Peg 2: [3, 2, 1]  (largest to smallest)

MOVE FORMAT:
  [disk, source_peg, destination_peg]
  Example: [1, 0, 2] means "move disk 1 from peg 0 to peg 2"
""")
    print("-"*70 + "\n")


def interactive_mode():
    """Run the interactive solver mode."""
    print_banner()
    print("MODE: Interactive Solver")
    print("="*70)
    print("\nSolve the puzzle step by step with immediate feedback.\n")

    try:
        n_disks = int(input("Enter number of disks (1-10): ").strip())
        if n_disks < 1 or n_disks > 10:
            print("Please enter a number between 1 and 10.")
            return
    except ValueError:
        print("Invalid input. Please enter a number.")
        return
    except KeyboardInterrupt:
        print("\n\nExiting.")
        return

    solver = InteractiveSolver(n_disks)
    solver.run()


def quick_validate():
    """Quick validation of a solution from command line."""
    print_banner()
    print("MODE: Quick Validator")
    print("="*70)
    print("\nQuickly validate a solution.\n")
    print("For more advanced validation examples, see examples/hanoi_tower/\n")

    try:
        n_disks = int(input("Enter number of disks: ").strip())
        if n_disks < 1:
            print("Number of disks must be at least 1.")
            return
    except ValueError:
        print("Invalid input. Please enter a number.")
        return
    except KeyboardInterrupt:
        print("\n\nExiting.")
        return

    print("\nEnter moves one per line in format: disk from_peg to_peg")
    print("Example: 1 0 2")
    print("Enter 'done' when finished.\n")

    validator = AutomatedValidator(n_disks)
    moves = []

    while True:
        try:
            line = input(f"Move {len(moves)+1}: ").strip().lower()

            if line == 'done':
                break
            if line == 'quit' or line == 'exit':
                print("Cancelled.")
                return

            # Parse move
            parts = line.replace('[', '').replace(']', '').replace(',', ' ').split()
            if len(parts) != 3:
                print("Invalid format. Use: disk from_peg to_peg")
                continue

            move = [int(parts[0]), int(parts[1]), int(parts[2])]
            moves.append(move)
            print(f"Added: {move}")

        except ValueError:
            print("Invalid input. Please enter three numbers.")
        except KeyboardInterrupt:
            print("\n\nCancelled.")
            return

    if not moves:
        print("No moves entered.")
        return

    # Validate
    result = validator.validate_solution(moves, verbose=True)
    validator.print_summary(result)


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description="Tower of Hanoi Interactive Simulator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                 # Run interactive mode (default)
  %(prog)s --interactive   # Solve puzzle interactively
  %(prog)s --validate      # Validate a sequence of moves
  %(prog)s --rules         # Show puzzle rules

For more examples and advanced usage, see the examples/ folder.
        """
    )

    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Run in interactive solver mode'
    )

    parser.add_argument(
        '--validate', '-v',
        action='store_true',
        help='Run quick validator mode'
    )

    parser.add_argument(
        '--rules', '-r',
        action='store_true',
        help='Show puzzle rules'
    )

    args = parser.parse_args()

    # Handle specific modes
    if args.rules:
        print_rules()
        return

    if args.validate:
        quick_validate()
        return

    if args.interactive:
        interactive_mode()
        return

    # No arguments provided - show menu
    print_banner()

    while True:
        print("\nSelect mode:")
        print("  1. Interactive Solver - Solve puzzle step by step")
        print("  2. Quick Validator - Validate a solution")
        print("  3. Rules - Show puzzle rules")
        print("  4. Exit")

        try:
            choice = input("\nEnter choice (1-4): ").strip()

            if choice == '1':
                interactive_mode()
            elif choice == '2':
                quick_validate()
            elif choice == '3':
                print_rules()
            elif choice == '4':
                print("\nGoodbye!\n")
                break
            else:
                print("Invalid choice. Please enter 1-4.")

        except KeyboardInterrupt:
            print("\n\nGoodbye!\n")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
