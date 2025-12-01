"""
Simple example with a manually created test network.

This demonstrates the CLD analysis without requiring an external file.
"""

import pandas as pd
from cld_analysis import LoopSetLoader


def create_test_adjacency_matrix():
    """
    Create a simple test adjacency matrix and save it as an Excel file.

    This creates a simple causal loop diagram with a few feedback loops.
    """
    # Create a simple test network
    # Concepts: A, B, C, D, E
    concepts = ['A', 'B', 'C', 'D', 'E']

    # Create adjacency matrix (all zeros initially)
    matrix = pd.DataFrame(0, index=concepts, columns=concepts)

    # Add some links to create feedback loops
    # Loop 1: A -> B -> C -> A (all positive, reinforcing loop)
    matrix.loc['A', 'B'] = 1   # A increases B
    matrix.loc['B', 'C'] = 1   # B increases C
    matrix.loc['C', 'A'] = 1   # C increases A

    # Loop 2: A -> B -> D -> A (one negative, balancing loop)
    matrix.loc['B', 'D'] = 1   # B increases D
    matrix.loc['D', 'A'] = -1  # D decreases A

    # Loop 3: C -> E -> D -> B -> C (two negatives, reinforcing loop)
    matrix.loc['C', 'E'] = 1   # C increases E
    matrix.loc['E', 'D'] = -1  # E decreases D
    matrix.loc['D', 'B'] = -1  # D decreases B

    # Save to Excel file
    output_file = "test_adjacency_matrix.xlsx"
    matrix.to_excel(output_file)
    print(f"Created test adjacency matrix: {output_file}")
    print("\nMatrix:")
    print(matrix)
    print("\nThis network contains multiple feedback loops:")
    print("  - Loop 1: A -> B -> C -> A (reinforcing)")
    print("  - Loop 2: A -> B -> D -> A (balancing)")
    print("  - Loop 3: C -> E -> D -> B -> C (reinforcing)")

    return output_file


def main():
    print("Simple CLD Analysis Example")
    print("=" * 60)

    # Create a test adjacency matrix
    print("\nStep 1: Creating test adjacency matrix...")
    test_file = create_test_adjacency_matrix()

    # Create the loader
    loader = LoopSetLoader()

    # Load and analyze
    print("\n\nStep 2: Loading network and finding loops...")
    print("=" * 60)
    loader.load_from_adjacency_matrix(
        filepath=test_file,
        verbose=True
    )

    # Calculate scores
    print("\n\nStep 3: Calculating centrality scores...")
    print("=" * 60)
    loader.get_scores(verbose=True)

    # Print summary
    print("\n\nStep 4: Results Summary")
    print("=" * 60)
    loader.summary()

    # Export results
    print("\n\nStep 5: Exporting results...")
    print("=" * 60)
    loader.write_concept_node_file("simple_example_nodes.csv")
    loader.write_concept_link_file("simple_example_links.csv")
    loader.write_loop_node_file("simple_example_loops.csv")
    loader.report_scores("simple_example_scores.txt")

    print("\n\nAnalysis complete! Check the output files:")
    print("  - simple_example_nodes.csv: Concept scores")
    print("  - simple_example_links.csv: Link information")
    print("  - simple_example_loops.csv: Loop information")
    print("  - simple_example_scores.txt: Ranked scores")


if __name__ == "__main__":
    main()
