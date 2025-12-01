"""
Adjacency matrix loader for Excel files.
"""

import pandas as pd
from typing import List, Set
from .models import Concept, Link, Influence


def load_adjacency_matrix_from_excel(filepath: str, sheet_name: int = 0) -> Set[Link]:
    """
    Load an adjacency matrix from an Excel file.

    The expected format is:
    - First row contains target concept names (starting from column B)
    - First column contains source concept names (starting from row 2)
    - Cell values are polarities: +1 for positive influence, -1 for negative influence
    - Empty or 0 cells indicate no connection

    Args:
        filepath: Path to the Excel file
        sheet_name: Sheet name or index (default: 0 for first sheet)

    Returns:
        Set of Link objects representing the network

    Example Excel format:
        |          | Target1 | Target2 | Target3 |
        |----------|---------|---------|---------|
        | Source1  |    1    |   -1    |    0    |
        | Source2  |   -1    |    0    |    1    |
        | Source3  |    0    |    1    |   -1    |
    """
    # Read the Excel file
    df = pd.read_excel(filepath, sheet_name=sheet_name, header=0, index_col=0)

    # Clean up column and index names (remove any whitespace)
    df.columns = [str(col).strip() if pd.notna(col) else f"Unnamed_{i}"
                  for i, col in enumerate(df.columns)]
    df.index = [str(idx).strip() if pd.notna(idx) else f"Unnamed_{i}"
                for i, idx in enumerate(df.index)]

    # Create links from the matrix
    links = set()

    for source_name in df.index:
        for target_name in df.columns:
            # Get the polarity value
            polarity = df.loc[source_name, target_name]

            # Skip if no connection (NaN, 0, or empty)
            if pd.isna(polarity) or polarity == 0:
                continue

            # Convert polarity to int
            try:
                polarity_int = int(polarity)
            except (ValueError, TypeError):
                print(f"Warning: Invalid polarity value '{polarity}' for "
                      f"{source_name} -> {target_name}. Skipping.")
                continue

            # Validate polarity is +1 or -1
            if polarity_int not in [1, -1]:
                print(f"Warning: Polarity value {polarity_int} for "
                      f"{source_name} -> {target_name} is not +1 or -1. Skipping.")
                continue

            # Create concepts and link
            source_concept = Concept.get_concept(source_name)
            target_concept = Concept.get_concept(target_name)
            influence = Influence.from_polarity(polarity_int)

            link = Link(source_concept, influence, target_concept)
            links.add(link)

    print(f"Loaded {len(links)} links from adjacency matrix")

    return links


def load_adjacency_matrix_from_csv(filepath: str) -> Set[Link]:
    """
    Load an adjacency matrix from a CSV file.

    Same format as Excel: first row is targets, first column is sources,
    cell values are polarities (+1 or -1).

    Args:
        filepath: Path to the CSV file

    Returns:
        Set of Link objects representing the network
    """
    # Read the CSV file
    df = pd.read_csv(filepath, header=0, index_col=0)

    # Clean up column and index names
    df.columns = [str(col).strip() if pd.notna(col) else f"Unnamed_{i}"
                  for i, col in enumerate(df.columns)]
    df.index = [str(idx).strip() if pd.notna(idx) else f"Unnamed_{i}"
                for i, idx in enumerate(df.index)]

    # Create links from the matrix
    links = set()

    for source_name in df.index:
        for target_name in df.columns:
            # Get the polarity value
            polarity = df.loc[source_name, target_name]

            # Skip if no connection (NaN, 0, or empty)
            if pd.isna(polarity) or polarity == 0:
                continue

            # Convert polarity to int
            try:
                polarity_int = int(polarity)
            except (ValueError, TypeError):
                print(f"Warning: Invalid polarity value '{polarity}' for "
                      f"{source_name} -> {target_name}. Skipping.")
                continue

            # Validate polarity is +1 or -1
            if polarity_int not in [1, -1]:
                print(f"Warning: Polarity value {polarity_int} for "
                      f"{source_name} -> {target_name} is not +1 or -1. Skipping.")
                continue

            # Create concepts and link
            source_concept = Concept.get_concept(source_name)
            target_concept = Concept.get_concept(target_name)
            influence = Influence.from_polarity(polarity_int)

            link = Link(source_concept, influence, target_concept)
            links.add(link)

    print(f"Loaded {len(links)} links from adjacency matrix")

    return links
