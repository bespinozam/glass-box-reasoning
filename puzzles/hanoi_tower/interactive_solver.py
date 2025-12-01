"""
Interactive Solver Module

This module provides an interactive interface for solving the Tower of Hanoi
puzzle step by step, allowing users to input moves and see the state after
each move.
"""

from hanoi_state import HanoiState
from typing import List, Optional


class InteractiveSolver:
    """
    Interactive solver for Tower of Hanoi puzzle.
    Allows users to input moves step by step and see the state after each move.
    """

    def __init__(self, n_disks: int):
        """
        Initialize the interactive solver.

        Args:
            n_disks: Number of disks in the puzzle
        """
        self.state = HanoiState(n_disks)

    def parse_move(self, move_input: str) -> Optional[List[int]]:
        """
        Parse a move input string.

        Args:
            move_input: String in format "disk from_peg to_peg" or "[disk, from_peg, to_peg]"

        Returns:
            List of [disk, from_peg, to_peg] or None if parsing fails
        """
        try:
            # Remove brackets and whitespace
            move_input = move_input.strip().replace('[', '').replace(']', '')

            # Split by comma or space
            if ',' in move_input:
                parts = [int(x.strip()) for x in move_input.split(',')]
            else:
                parts = [int(x.strip()) for x in move_input.split()]

            if len(parts) != 3:
                return None

            return parts
        except (ValueError, AttributeError):
            return None

    def run(self):
        """
        Run the interactive solver.
        """
        print("\n" + "="*60)
        print("  TOWER OF HANOI - INTERACTIVE MODE")
        print("="*60)
        print(f"\nWelcome! Solve the {self.state.n_disks}-disk Tower of Hanoi puzzle.")
        print("\nGoal: Move all disks from Peg 0 to Peg 2")
        print("\nRules:")
        print("  1. Move only one disk at a time")
        print("  2. Only the top disk can be moved")
        print("  3. Larger disks cannot be placed on smaller disks")
        print("\nMove format: disk from_peg to_peg")
        print("  Example: '1 0 2' to move disk 1 from peg 0 to peg 2")
        print("  Or use: '[1, 0, 2]'")
        print("\nCommands:")
        print("  'quit' or 'q' - Exit the game")
        print("  'reset' or 'r' - Reset to initial state")
        print("  'history' or 'h' - Show move history")

        # Display initial state
        self.state.display()

        while not self.state.is_solved:
            try:
                # Get user input
                user_input = input("Enter move (or command): ").strip().lower()

                # Check for commands
                if user_input in ['quit', 'q']:
                    print("\nExiting. Puzzle not solved.")
                    return False

                if user_input in ['reset', 'r']:
                    self.state.reset()
                    print("\n[Puzzle reset to initial state]")
                    self.state.display()
                    continue

                if user_input in ['history', 'h']:
                    self.show_history()
                    continue

                # Parse move
                move = self.parse_move(user_input)
                if move is None:
                    print("❌ Invalid format. Use: 'disk from_peg to_peg' (e.g., '1 0 2')")
                    continue

                disk, from_peg, to_peg = move

                # Apply move
                success, message = self.state.apply_move(disk, from_peg, to_peg)

                if success:
                    print(f"✓ Move applied: Disk {disk} from Peg {from_peg} to Peg {to_peg}")
                    self.state.display()

                    if self.state.is_solved:
                        self.show_victory()
                        return True
                else:
                    print(f"❌ Invalid move: {message}")

            except KeyboardInterrupt:
                print("\n\nInterrupted. Exiting.")
                return False
            except Exception as e:
                print(f"❌ Error: {e}")

        return True

    def show_history(self):
        """Display the move history."""
        print("\n" + "-"*50)
        print("Move History:")
        print("-"*50)
        if not self.state.history:
            print("  No moves yet")
        else:
            for i, (disk, from_peg, to_peg) in enumerate(self.state.history, 1):
                print(f"  {i}. Disk {disk}: Peg {from_peg} → Peg {to_peg}")
        print("-"*50 + "\n")

    def show_victory(self):
        """Display victory message."""
        print("\n" + "🎉"*30)
        print("\n  CONGRATULATIONS! PUZZLE SOLVED!")
        print(f"\n  Total moves: {self.state.num_moves}")

        # Calculate optimal number of moves
        optimal_moves = 2**self.state.n_disks - 1
        print(f"  Optimal moves: {optimal_moves}")

        if self.state.num_moves == optimal_moves:
            print("\n  ⭐ PERFECT! You solved it optimally!")
        elif self.state.num_moves <= optimal_moves * 1.5:
            print("\n  👍 Great job! Very efficient solution!")
        else:
            print(f"\n  You can try to solve it in fewer moves!")

        print("\n" + "🎉"*30 + "\n")

        self.show_history()


def main():
    """Main function for interactive mode."""
    print("\nTower of Hanoi - Interactive Solver")
    print("="*60)

    try:
        n_disks = int(input("Enter number of disks (1-10): ").strip())
        if n_disks < 1 or n_disks > 10:
            print("Please enter a number between 1 and 10.")
            return
    except ValueError:
        print("Invalid input. Please enter a number.")
        return

    solver = InteractiveSolver(n_disks)
    solver.run()


if __name__ == "__main__":
    main()
