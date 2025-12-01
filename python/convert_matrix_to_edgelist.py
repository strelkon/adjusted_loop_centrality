"""
Convert adjacency matrix to edge list CSV format for Java implementation.

This script converts an Excel adjacency matrix to the CSV format expected
by the Java CLD analysis tool (Source,Target,Polarity format).
"""

import pandas as pd
import sys


def convert_matrix_to_edgelist(input_file: str, output_file: str, sheet_name=0):
    """
    Convert adjacency matrix to edge list format.

    Args:
        input_file: Path to Excel adjacency matrix
        output_file: Path to output CSV file
        sheet_name: Sheet name or index (default: 0)
    """
    # Read the adjacency matrix
    df = pd.read_excel(input_file, sheet_name=sheet_name, header=0, index_col=0)

    # Clean up column and index names
    df.columns = [str(col).strip() if pd.notna(col) else f"Unnamed_{i}"
                  for i, col in enumerate(df.columns)]
    df.index = [str(idx).strip() if pd.notna(idx) else f"Unnamed_{i}"
                for i, idx in enumerate(df.index)]

    # Create edge list
    edges = []

    for source_name in df.index:
        for target_name in df.columns:
            value = df.loc[source_name, target_name]

            # Skip empty/zero values
            if pd.isna(value):
                continue

            # Parse the value
            try:
                # Handle string values with spaces
                if isinstance(value, str):
                    cleaned = value.replace(" ", "").strip()
                    if not cleaned or cleaned == "0":
                        continue
                    # Remove plus sign if present
                    cleaned = cleaned.replace("+", "")
                    polarity_int = int(cleaned)
                else:
                    polarity_int = int(value)

                # Skip zero
                if polarity_int == 0:
                    continue

                # Validate
                if polarity_int not in [1, -1]:
                    print(f"Warning: Skipping invalid polarity {polarity_int} "
                          f"for {source_name} -> {target_name}")
                    continue

                # Convert to Java format: "Positive" or "Negative"
                polarity_str = "Positive" if polarity_int == 1 else "Negative"

                edges.append({
                    'Source': source_name,
                    'Target': target_name,
                    'Polarity': polarity_str
                })

            except (ValueError, TypeError) as e:
                print(f"Warning: Could not parse value '{value}' for "
                      f"{source_name} -> {target_name}: {e}")
                continue

    # Create DataFrame and save
    if edges:
        edge_df = pd.DataFrame(edges)
        edge_df.to_csv(output_file, index=False)
        print(f"\nSuccessfully converted {len(edges)} edges")
        print(f"Output file: {output_file}")

        # Print summary
        print(f"\nSummary:")
        print(f"  Total edges: {len(edges)}")
        print(f"  Positive edges: {sum(1 for e in edges if e['Polarity'] == 'Positive')}")
        print(f"  Negative edges: {sum(1 for e in edges if e['Polarity'] == 'Negative')}")
        print(f"  Unique concepts: {len(set([e['Source'] for e in edges] + [e['Target'] for e in edges]))}")

        return edge_df
    else:
        print("Error: No valid edges found in matrix")
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python convert_matrix_to_edgelist.py <input_file.xlsx> [output_file.csv]")
        print("\nExample:")
        print("  python convert_matrix_to_edgelist.py data/OAIMicrosoft_v6_17.11.25.xlsx java_input.csv")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "edgelist_for_java.csv"

    print("="*60)
    print("ADJACENCY MATRIX TO EDGE LIST CONVERTER")
    print("="*60)
    print(f"\nInput file: {input_file}")
    print(f"Output file: {output_file}")
    print()

    convert_matrix_to_edgelist(input_file, output_file)

    print("\n" + "="*60)
    print("Conversion complete!")
    print("="*60)
    print("\nYou can now use this file with the Java implementation:")
    print(f"  Java: network.loadLoopSet(path, \"{output_file}\");")


if __name__ == "__main__":
    main()
