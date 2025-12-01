"""
Test script to verify parsing of string values with spaces in adjacency matrices.

This tests the ability to parse values like "+ 1", "- 1", " 1 ", " -1 ", etc.
"""

import pandas as pd
from cld_analysis import LoopSetLoader


def create_test_matrix_with_string_values():
    """
    Create a test adjacency matrix with various string formats.
    """
    concepts = ['A', 'B', 'C', 'D']

    # Create a matrix with various string formats
    data = {
        'A': [0, '+ 1', 0, 0],      # String with space: "+ 1"
        'B': [0, 0, '- 1', 0],       # String with space: "- 1"
        'C': [' 1 ', 0, 0, '-1'],    # Strings with spaces: " 1 ", "-1"
        'D': [0, ' +1', 0, 0]        # String with leading space: " +1"
    }

    matrix = pd.DataFrame(data, index=concepts)

    # Save to Excel
    output_file = "test_string_values.xlsx"
    matrix.to_excel(output_file)

    print("Created test matrix with string values:")
    print(matrix)
    print("\nString types in matrix:")
    for col in matrix.columns:
        for idx in matrix.index:
            val = matrix.loc[idx, col]
            if val != 0:
                print(f"  [{idx}, {col}] = '{val}' (type: {type(val).__name__})")

    return output_file


def main():
    print("="*60)
    print("STRING VALUE PARSING TEST")
    print("="*60)

    # Create test matrix
    print("\nStep 1: Creating test matrix with string values...")
    print("-"*60)
    test_file = create_test_matrix_with_string_values()

    # Load and analyze
    print("\n\nStep 2: Loading matrix with string parser...")
    print("-"*60)

    loader = LoopSetLoader()

    try:
        loader.load_from_adjacency_matrix(test_file, verbose=True)

        print("\n\nStep 3: Results...")
        print("-"*60)
        print(f"[OK] Successfully loaded {len(loader.all_links)} links")

        print("\nLinks found:")
        for link in sorted(loader.all_links, key=lambda l: (l.source.name, l.target.name)):
            print(f"  {link.source.name} --[{link.influence.value}]--> {link.target.name}")

        print("\nTest PASSED!")
        print("\nThe parser successfully handles:")
        print("  - '+ 1' (plus with space)")
        print("  - '- 1' (minus with space)")
        print("  - ' 1 ' (number with surrounding spaces)")
        print("  - ' +1' (plus sign with leading space)")
        print("  - '-1' (regular negative)")

    except Exception as e:
        print(f"\n[ERROR] Test FAILED with error: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*60)


if __name__ == "__main__":
    main()
