#!/usr/bin/env python
"""
Command-line interface for analyzing causal loop diagrams from adjacency matrices.

Usage:
    python analyze_matrix.py <input_file> [options]

Examples:
    python analyze_matrix.py data.xlsx
    python analyze_matrix.py data.csv --output results
    python analyze_matrix.py data.xlsx --sheet "Sheet2" --quiet
"""

import argparse
import sys
from pathlib import Path
from cld_analysis import LoopSetLoader


def main():
    parser = argparse.ArgumentParser(
        description='Analyze causal loop diagrams from adjacency matrices',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Input Format:
  The adjacency matrix should have:
  - First row: target concept names (starting from column B)
  - First column: source concept names (starting from row 2)
  - Cell values: +1 (positive influence) or -1 (negative influence)
  - Empty or 0 cells indicate no connection

Output Files:
  - concept_nodes.csv: Concept scores and loop counts
  - concept_links.csv: Link information with loop counts
  - loop_nodes.csv: Loop information
  - scores.txt: Ranked concept scores

Examples:
  python analyze_matrix.py OAIMicrosoft_v6_17.11.25.xlsx
  python analyze_matrix.py data.csv --output results --quiet
  python analyze_matrix.py data.xlsx --sheet "Main Diagram"
        """
    )

    parser.add_argument(
        'input_file',
        help='Path to the adjacency matrix file (Excel or CSV)'
    )

    parser.add_argument(
        '--sheet',
        default=0,
        help='Sheet name or index for Excel files (default: 0)'
    )

    parser.add_argument(
        '--output',
        default='output',
        help='Prefix for output files (default: output)'
    )

    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress progress messages'
    )

    parser.add_argument(
        '--top',
        type=int,
        default=10,
        help='Number of top concepts to display (default: 10)'
    )

    args = parser.parse_args()

    # Check if input file exists
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: File not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)

    verbose = not args.quiet

    try:
        if verbose:
            print("="*60)
            print("CAUSAL LOOP DIAGRAM ANALYSIS")
            print("="*60)
            print(f"\nInput file: {args.input_file}")
            print(f"Output prefix: {args.output}")
            print()

        # Create loader
        loader = LoopSetLoader()

        # Convert sheet to int if possible
        try:
            sheet_name = int(args.sheet)
        except ValueError:
            sheet_name = args.sheet

        # Load and analyze
        if verbose:
            print("Loading network and detecting loops...")
            print("-"*60)

        loader.load_from_adjacency_matrix(
            filepath=args.input_file,
            sheet_name=sheet_name,
            verbose=verbose
        )

        # Calculate scores
        if verbose:
            print("\nCalculating centrality scores...")
            print("-"*60)

        loader.get_scores(verbose=verbose)

        # Display summary
        if verbose:
            loader.summary()

        # Export results
        output_files = {
            'nodes': f"{args.output}_concept_nodes.csv",
            'links': f"{args.output}_concept_links.csv",
            'loops': f"{args.output}_loop_nodes.csv",
            'scores': f"{args.output}_scores.txt"
        }

        if verbose:
            print("\nExporting results...")
            print("-"*60)

        loader.write_concept_node_file(output_files['nodes'])
        loader.write_concept_link_file(output_files['links'])
        loader.write_loop_node_file(output_files['loops'])
        loader.report_scores(output_files['scores'])

        if verbose:
            print("\n" + "="*60)
            print("ANALYSIS COMPLETE")
            print("="*60)
            print("\nOutput files created:")
            for name, path in output_files.items():
                print(f"  - {path}")
        else:
            # In quiet mode, just show file count
            print(f"Analysis complete. {len(output_files)} files created.")

        sys.exit(0)

    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
