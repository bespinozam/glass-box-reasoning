#!/usr/bin/env python3
"""
Tower of Hanoi Puzzle Simulator

A comprehensive Tower of Hanoi simulator for evaluating reasoning models.
Supports both interactive solving and automated validation of move sequences.

Author: Tower of Hanoi Simulator
Purpose: Evaluate reasoning capabilities of AI models
"""

import sys
import argparse
from hanoi_state import HanoiState
from interactive_solver import InteractiveSolver
from automated_validator import AutomatedValidator
import json


def print_banner():
    """Print the application banner."""
    print("\n" + "="*70)
    print(" "*20 + "TOWER OF HANOI SIMULATOR")
    print("="*70)
    print("\n A tool for evaluating reasoning models through puzzle solving\n")


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
            print("❌ Please enter a number between 1 and 10.")
            return
    except ValueError:
        print("❌ Invalid input. Please enter a number.")
        return
    except KeyboardInterrupt:
        print("\n\nExiting.")
        return

    solver = InteractiveSolver(n_disks)
    solver.run()


def automated_mode():
    """Run the automated validator mode."""
    print_banner()
    print("MODE: Automated Validator")
    print("="*70)
    print("\nValidate a complete sequence of moves.\n")

    try:
        n_disks = int(input("Enter number of disks: ").strip())
        if n_disks < 1:
            print("❌ Number of disks must be at least 1.")
            return
    except ValueError:
        print("❌ Invalid input. Please enter a number.")
        return
    except KeyboardInterrupt:
        print("\n\nExiting.")
        return

    print("\nChoose input method:")
    print("  1. Enter moves manually")
    print("  2. Load from JSON file")

    try:
        choice = input("\nEnter choice (1 or 2): ").strip()
    except KeyboardInterrupt:
        print("\n\nExiting.")
        return

    validator = AutomatedValidator(n_disks)

    if choice == "1":
        # Manual input
        print("\nEnter moves one per line in format: disk from_peg to_peg")
        print("Example: 1 0 2")
        print("Enter 'done' when finished, or 'cancel' to abort.\n")

        moves = []
        while True:
            try:
                line = input(f"Move {len(moves)+1}: ").strip().lower()

                if line == 'done':
                    break
                if line == 'cancel':
                    print("Cancelled.")
                    return

                # Parse move
                parts = line.replace('[', '').replace(']', '').replace(',', ' ').split()
                if len(parts) != 3:
                    print("❌ Invalid format. Use: disk from_peg to_peg")
                    continue

                move = [int(parts[0]), int(parts[1]), int(parts[2])]
                moves.append(move)
                print(f"✓ Added: {move}")

            except ValueError:
                print("❌ Invalid input. Please enter three numbers.")
            except KeyboardInterrupt:
                print("\n\nCancelled.")
                return

        if not moves:
            print("No moves entered.")
            return

        # Validate
        result = validator.validate_solution(moves, verbose=True)
        validator.print_summary(result)

    elif choice == "2":
        # File input
        try:
            filepath = input("\nEnter path to JSON file: ").strip()
            result = validator.validate_from_file(filepath, verbose=True)
            validator.print_summary(result)
        except KeyboardInterrupt:
            print("\n\nCancelled.")
            return
    else:
        print("❌ Invalid choice.")


def demo_mode():
    """Run a demonstration of the simulator."""
    print_banner()
    print("MODE: Demo")
    print("="*70)

    # Demo 1: Show state representation
    print("\n1. STATE REPRESENTATION DEMO")
    print("-"*70)
    state = HanoiState(3)
    state.display()

    # Demo 2: Valid moves
    print("\n2. VALID MOVES DEMO")
    print("-"*70)
    moves = [
        [1, 0, 2],
        [2, 0, 1],
        [1, 2, 1],
    ]

    for i, (disk, from_peg, to_peg) in enumerate(moves, 1):
        print(f"\nMove {i}: Disk {disk} from Peg {from_peg} to Peg {to_peg}")
        success, msg = state.apply_move(disk, from_peg, to_peg)
        print(f"Result: {'✓ Success' if success else '❌ Failed'} - {msg}")
        state.display()

    # Demo 3: Invalid move
    print("\n3. INVALID MOVE DEMO")
    print("-"*70)
    print("\nAttempting invalid move: Disk 3 from Peg 0 to Peg 1")
    print("(Should fail: Disk 3 is not on top)")
    success, msg = state.apply_move(3, 0, 1)
    print(f"Result: {'✓ Success' if success else '❌ Failed'} - {msg}")

    # Demo 4: Automated validation
    print("\n4. AUTOMATED VALIDATION DEMO")
    print("-"*70)

    # Optimal solution for 3 disks
    optimal_solution = [
        [1, 0, 2], [2, 0, 1], [1, 2, 1],
        [3, 0, 2], [1, 1, 0], [2, 1, 2],
        [1, 0, 2]
    ]

    validator = AutomatedValidator(3)
    result = validator.validate_solution(optimal_solution, verbose=False)
    validator.print_summary(result)


def create_sample_file():
    """Create a sample JSON file with moves."""
    filename = "sample_solution_3disk.json"

    sample_data = {
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

    try:
        with open(filename, 'w') as f:
            json.dump(sample_data, f, indent=2)
        print(f"✓ Created sample file: {filename}")
        return True
    except Exception as e:
        print(f"❌ Error creating sample file: {e}")
        return False


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description="Tower of Hanoi Puzzle Simulator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --interactive          # Solve puzzle interactively
  %(prog)s --validate             # Validate a sequence of moves
  %(prog)s --demo                 # Run demonstration
  %(prog)s --rules                # Show puzzle rules
  %(prog)s --sample               # Create sample solution file
        """
    )

    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Run in interactive mode'
    )

    parser.add_argument(
        '--validate', '-v',
        action='store_true',
        help='Run in automated validation mode'
    )

    parser.add_argument(
        '--demo', '-d',
        action='store_true',
        help='Run demonstration'
    )

    parser.add_argument(
        '--rules', '-r',
        action='store_true',
        help='Show puzzle rules'
    )

    parser.add_argument(
        '--sample', '-s',
        action='store_true',
        help='Create a sample JSON solution file'
    )

    args = parser.parse_args()

    # Handle specific modes
    if args.rules:
        print_rules()
        return

    if args.sample:
        print_banner()
        create_sample_file()
        return

    if args.demo:
        demo_mode()
        return

    if args.interactive:
        interactive_mode()
        return

    if args.validate:
        automated_mode()
        return

    # No arguments provided - show menu
    print_banner()

    while True:
        print("\nSelect mode:")
        print("  1. Interactive Solver - Solve puzzle step by step")
        print("  2. Automated Validator - Validate a complete solution")
        print("  3. Demo - See how the simulator works")
        print("  4. Rules - Show puzzle rules and format")
        print("  5. Create Sample File - Generate example solution JSON")
        print("  6. Exit")

        try:
            choice = input("\nEnter choice (1-6): ").strip()

            if choice == '1':
                interactive_mode()
            elif choice == '2':
                automated_mode()
            elif choice == '3':
                demo_mode()
            elif choice == '4':
                print_rules()
            elif choice == '5':
                create_sample_file()
            elif choice == '6':
                print("\nGoodbye!\n")
                break
            else:
                print("❌ Invalid choice. Please enter 1-6.")

        except KeyboardInterrupt:
            print("\n\nGoodbye!\n")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
