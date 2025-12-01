"""
Script to create a sample adjacency matrix Excel file.

This shows the exact format expected for the OAIMicrosoft_v6_17.11.25.xlsx style input.
"""

import pandas as pd


def create_sample_adjacency_matrix():
    """
    Create a sample adjacency matrix that demonstrates the expected format.
    """
    # Example concepts for a simple urban-rural system
    concepts = [
        'Urban Population',
        'Economic Growth',
        'Infrastructure Investment',
        'Environmental Quality',
        'Rural Migration',
        'Agricultural Production'
    ]

    # Create adjacency matrix
    matrix = pd.DataFrame(0, index=concepts, columns=concepts)

    # Define causal relationships
    # Format: matrix.loc['Source', 'Target'] = polarity (1 or -1)

    # Urban population increases economic growth
    matrix.loc['Urban Population', 'Economic Growth'] = 1

    # Economic growth increases infrastructure investment
    matrix.loc['Economic Growth', 'Infrastructure Investment'] = 1

    # Infrastructure investment increases urban population (reinforcing loop)
    matrix.loc['Infrastructure Investment', 'Urban Population'] = 1

    # Urban population decreases environmental quality
    matrix.loc['Urban Population', 'Environmental Quality'] = -1

    # Environmental quality decreases rural migration
    matrix.loc['Environmental Quality', 'Rural Migration'] = -1

    # Rural migration increases urban population (balancing loop)
    matrix.loc['Rural Migration', 'Urban Population'] = 1

    # Economic growth increases environmental quality (through regulations)
    matrix.loc['Economic Growth', 'Environmental Quality'] = 1

    # Agricultural production increases rural migration
    matrix.loc['Agricultural Production', 'Rural Migration'] = -1

    # Infrastructure investment increases agricultural production
    matrix.loc['Infrastructure Investment', 'Agricultural Production'] = 1

    # Agricultural production increases environmental quality
    matrix.loc['Agricultural Production', 'Environmental Quality'] = 1

    # Save to Excel
    output_file = "sample_adjacency_matrix.xlsx"
    matrix.to_excel(output_file, sheet_name='System Diagram')

    print(f"Created sample adjacency matrix: {output_file}\n")
    print("Matrix structure:")
    print(matrix)
    print("\n" + "="*60)
    print("Format explanation:")
    print("="*60)
    print("- Rows (index): Source concepts")
    print("- Columns: Target concepts")
    print("- Cell values:")
    print("    +1 = Source INCREASES Target (positive influence)")
    print("    -1 = Source DECREASES Target (negative influence)")
    print("     0 = No direct influence")
    print("\nThis file can now be used with the CLD analysis tool:")
    print("  python analyze_matrix.py sample_adjacency_matrix.xlsx")

    return output_file, matrix


if __name__ == "__main__":
    create_sample_adjacency_matrix()
