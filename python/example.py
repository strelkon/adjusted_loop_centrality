"""
Example script demonstrating how to use the CLD Analysis tool.

This script shows how to:
1. Load an adjacency matrix from an Excel file
2. Detect all feedback loops
3. Calculate centrality scores
4. Export results to CSV files
"""

from cld_analysis import LoopSetLoader


def main():
    # Create the loader
    loader = LoopSetLoader()

    # Load the network from an adjacency matrix Excel file
    # Replace this path with your actual file path
    # For example: "data/OAIMicrosoft_v6_17.11.25.xlsx"
    input_file = "your_adjacency_matrix.xlsx"

    try:
        print("Starting Causal Loop Diagram Analysis")
        print("=" * 60)

        # Load the network and find loops
        loader.load_from_adjacency_matrix(
            filepath=input_file,
            sheet_name=0,  # First sheet (can also use sheet name as string)
            verbose=True
        )

        # Calculate centrality scores
        print("\nCalculating centrality scores...")
        loader.get_scores(verbose=True)

        # Print summary
        loader.summary()

        # Export results to files
        print("\nExporting results...")
        loader.write_concept_node_file("output_concept_nodes.csv")
        loader.write_concept_link_file("output_concept_links.csv")
        loader.write_loop_node_file("output_loop_nodes.csv")
        loader.report_scores("output_scores.txt")

        print("\nAnalysis complete!")

    except FileNotFoundError:
        print(f"\nError: Could not find file '{input_file}'")
        print("\nPlease update the 'input_file' variable with the path to your Excel file.")
        print("\nThe expected format is an adjacency matrix where:")
        print("  - First row contains target concept names (starting from column B)")
        print("  - First column contains source concept names (starting from row 2)")
        print("  - Cell values are +1 (positive influence) or -1 (negative influence)")
        print("  - Empty or 0 cells indicate no connection")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
