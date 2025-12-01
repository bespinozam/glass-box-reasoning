#!/usr/bin/env python3
"""
Analysis Utilities for JSONL Output Files

This module provides utilities for analyzing and summarizing model evaluation results.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import defaultdict


class ResultsAnalyzer:
    """Analyzer for reading and summarizing JSONL output files."""

    def __init__(self, base_dir: str = "outputs"):
        """
        Initialize the analyzer.

        Args:
            base_dir: Base directory containing output files
        """
        self.base_dir = Path(base_dir)

    def list_runs(self) -> List[str]:
        """
        List all run IDs in the base directory.

        Returns:
            List of run IDs
        """
        if not self.base_dir.exists():
            return []

        return [d.name for d in self.base_dir.iterdir() if d.is_dir()]

    def list_models(self, run_id: str) -> List[str]:
        """
        List all models for a specific run.

        Args:
            run_id: Run identifier

        Returns:
            List of model names
        """
        run_dir = self.base_dir / run_id
        if not run_dir.exists():
            return []

        return [d.name for d in run_dir.iterdir() if d.is_dir()]

    def load_results(self, run_id: str, model_name: str, n_disks: int) -> List[Dict[str, Any]]:
        """
        Load all results for a specific run, model, and puzzle size.

        Args:
            run_id: Run identifier
            model_name: Model name
            n_disks: Number of disks

        Returns:
            List of result entries
        """
        filepath = self.base_dir / run_id / model_name / f"output_hanoi_n{n_disks}.jsonl"

        if not filepath.exists():
            return []

        results = []
        with open(filepath, 'r') as f:
            for line in f:
                if line.strip():
                    results.append(json.loads(line))

        return results

    def analyze_run(self, run_id: str, model_name: str) -> Dict[str, Any]:
        """
        Analyze all results for a specific run and model.

        Args:
            run_id: Run identifier
            model_name: Model name

        Returns:
            Dictionary with analysis results
        """
        model_dir = self.base_dir / run_id / model_name

        if not model_dir.exists():
            return {}

        # Find all output files
        output_files = list(model_dir.glob("output_hanoi_n*.jsonl"))

        analysis = {
            "run_id": run_id,
            "model_name": model_name,
            "puzzle_sizes": []
        }

        for filepath in sorted(output_files):
            # Extract n_disks from filename
            filename = filepath.stem  # output_hanoi_n3
            n_disks = int(filename.split('_n')[-1])

            # Load results
            results = []
            with open(filepath, 'r') as f:
                for line in f:
                    if line.strip():
                        results.append(json.loads(line))

            if not results:
                continue

            # Analyze this puzzle size
            total = len(results)
            successful = sum(1 for r in results if r.get('is_correct'))
            failed = total - successful

            # Token statistics
            tokens = [r.get('tokens_used') for r in results if r.get('tokens_used') is not None]
            avg_tokens = sum(tokens) / len(tokens) if tokens else None
            min_tokens = min(tokens) if tokens else None
            max_tokens = max(tokens) if tokens else None

            # Efficiency statistics (for successful attempts only)
            efficiencies = []
            for r in results:
                if r.get('is_correct'):
                    eff = r.get('metadata', {}).get('validation', {}).get('efficiency')
                    if eff is not None:
                        efficiencies.append(eff)

            avg_efficiency = sum(efficiencies) / len(efficiencies) if efficiencies else None

            # Failure reasons
            failure_reasons = defaultdict(int)
            for r in results:
                if not r.get('is_correct') and r.get('failure_reason'):
                    reason = r['failure_reason']
                    # Categorize the failure
                    if 'Parse error' in reason:
                        failure_reasons['parse_error'] += 1
                    elif 'Invalid move' in reason:
                        failure_reasons['invalid_move'] += 1
                    elif 'not solved' in reason:
                        failure_reasons['incomplete'] += 1
                    else:
                        failure_reasons['other'] += 1

            puzzle_analysis = {
                "n_disks": n_disks,
                "total_iterations": total,
                "successful": successful,
                "failed": failed,
                "success_rate": successful / total if total > 0 else 0.0,
                "avg_tokens": avg_tokens,
                "min_tokens": min_tokens,
                "max_tokens": max_tokens,
                "avg_efficiency": avg_efficiency,
                "failure_reasons": dict(failure_reasons)
            }

            analysis["puzzle_sizes"].append(puzzle_analysis)

        return analysis

    def compare_models(self, run_id: str) -> Dict[str, Any]:
        """
        Compare all models in a specific run.

        Args:
            run_id: Run identifier

        Returns:
            Dictionary with comparison data
        """
        models = self.list_models(run_id)

        comparison = {
            "run_id": run_id,
            "models": {}
        }

        for model_name in models:
            analysis = self.analyze_run(run_id, model_name)
            comparison["models"][model_name] = analysis

        return comparison

    def print_analysis(self, run_id: str, model_name: str) -> None:
        """
        Print a formatted analysis report.

        Args:
            run_id: Run identifier
            model_name: Model name
        """
        analysis = self.analyze_run(run_id, model_name)

        if not analysis or not analysis.get('puzzle_sizes'):
            print(f"No results found for {run_id}/{model_name}")
            return

        print("\n" + "="*70)
        print(f"ANALYSIS REPORT")
        print("="*70)
        print(f"Run ID: {analysis['run_id']}")
        print(f"Model: {analysis['model_name']}")
        print("-"*70)

        for puzzle in analysis['puzzle_sizes']:
            print(f"\nPuzzle Size: {puzzle['n_disks']} disks")
            print(f"  Iterations: {puzzle['total_iterations']}")
            print(f"  Success: {puzzle['successful']} ({puzzle['success_rate']:.1%})")
            print(f"  Failed: {puzzle['failed']}")

            if puzzle['avg_tokens']:
                print(f"  Tokens: avg={puzzle['avg_tokens']:.1f}, "
                      f"min={puzzle['min_tokens']}, max={puzzle['max_tokens']}")

            if puzzle['avg_efficiency']:
                print(f"  Efficiency: {puzzle['avg_efficiency']:.1%}")

            if puzzle['failure_reasons']:
                print(f"  Failures:")
                for reason, count in puzzle['failure_reasons'].items():
                    print(f"    - {reason}: {count}")

        print("\n" + "="*70)

    def print_comparison(self, run_id: str) -> None:
        """
        Print a formatted comparison of all models in a run.

        Args:
            run_id: Run identifier
        """
        comparison = self.compare_models(run_id)

        if not comparison.get('models'):
            print(f"No models found for run {run_id}")
            return

        print("\n" + "="*70)
        print(f"MODEL COMPARISON - Run: {run_id}")
        print("="*70)

        # Collect all puzzle sizes across all models
        all_sizes = set()
        for model_analysis in comparison['models'].values():
            for puzzle in model_analysis.get('puzzle_sizes', []):
                all_sizes.add(puzzle['n_disks'])

        for n_disks in sorted(all_sizes):
            print(f"\n{n_disks} Disks:")
            print("-"*70)
            print(f"{'Model':<20} {'Success Rate':<15} {'Avg Tokens':<15} {'Avg Efficiency':<15}")
            print("-"*70)

            for model_name, model_analysis in comparison['models'].items():
                # Find data for this puzzle size
                puzzle_data = None
                for puzzle in model_analysis.get('puzzle_sizes', []):
                    if puzzle['n_disks'] == n_disks:
                        puzzle_data = puzzle
                        break

                if puzzle_data:
                    success_rate = f"{puzzle_data['success_rate']:.1%}"
                    avg_tokens = f"{puzzle_data['avg_tokens']:.1f}" if puzzle_data['avg_tokens'] else "N/A"
                    avg_eff = f"{puzzle_data['avg_efficiency']:.1%}" if puzzle_data['avg_efficiency'] else "N/A"

                    print(f"{model_name:<20} {success_rate:<15} {avg_tokens:<15} {avg_eff:<15}")
                else:
                    print(f"{model_name:<20} {'No data':<15} {'No data':<15} {'No data':<15}")

        print("\n" + "="*70)


def main():
    """Demonstration of the analysis utilities."""
    print("\n" + "="*70)
    print("RESULTS ANALYZER - DEMONSTRATION")
    print("="*70)

    analyzer = ResultsAnalyzer()

    # List all runs
    print("\nAvailable runs:")
    runs = analyzer.list_runs()
    for run in runs:
        print(f"  - {run}")

    if not runs:
        print("  No runs found")
        return

    # Analyze the most recent run
    latest_run = sorted(runs)[-1]
    print(f"\nAnalyzing latest run: {latest_run}")

    models = analyzer.list_models(latest_run)
    print(f"Models in this run: {models}")

    # Print analysis for each model
    for model_name in models:
        analyzer.print_analysis(latest_run, model_name)

    # Print comparison if multiple models
    if len(models) > 1:
        analyzer.print_comparison(latest_run)


if __name__ == "__main__":
    main()
