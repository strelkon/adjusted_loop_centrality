"""
Adjacency matrix loader for Excel files.
"""

import pandas as pd
import numpy as np
from typing import List, Set
from .models import Concept, Link, Influence


def _parse_polarity(value) -> int:
    """
    Parse a polarity value from various formats.

    Supports:
    - Numeric: 1, -1, 1.0, -1.0
    - NumPy types: np.int64, np.float64, etc.
    - String with spaces: "+ 1", "- 1", "+1", "-1"
    - String variations: "1", "-1", " 1 ", " -1 "

    Args:
        value: The value to parse

    Returns:
        1 for positive, -1 for negative

    Raises:
        ValueError: If the value cannot be parsed or is not +1/-1
    """
    # Handle NaN or None
    if pd.isna(value):
        raise ValueError("NaN or None value")

    # If it's already a number (including numpy types), try to convert directly
    if isinstance(value, (int, float, np.integer, np.floating)):
        polarity_int = int(value)
        if polarity_int == 0:
            raise ValueError("Zero value")
        if polarity_int not in [1, -1]:
            raise ValueError(f"Numeric value {polarity_int} is not +1 or -1")
        return polarity_int

    # If it's a string, clean it up and parse
    if isinstance(value, str):
        # Remove all whitespace
        cleaned = value.replace(" ", "").strip()

        # Handle empty string
        if not cleaned or cleaned == "0":
            raise ValueError("Empty or zero value")

        # Try to convert to int
        try:
            polarity_int = int(cleaned)
        except ValueError:
            # Try to handle "+ 1" style by removing the +
            cleaned = cleaned.replace("+", "")
            try:
                polarity_int = int(cleaned)
            except ValueError:
                raise ValueError(f"Cannot parse '{value}' as integer")

        if polarity_int == 0:
            raise ValueError("Zero value")
        if polarity_int not in [1, -1]:
            raise ValueError(f"Parsed value {polarity_int} is not +1 or -1")

        return polarity_int

    raise ValueError(f"Unsupported type {type(value)}")


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
        | Source2  |  "+ 1"  |  "- 1"  |    0    |
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

            # Try to parse the polarity
            try:
                polarity_int = _parse_polarity(polarity)
            except ValueError as e:
                # Skip silently if it's a known "no connection" case
                error_msg = str(e)
                if error_msg in ["NaN or None value", "Empty or zero value", "Zero value"]:
                    continue
                # Otherwise, warn about truly invalid values
                print(f"Warning: Invalid polarity value '{polarity}' for "
                      f"{source_name} -> {target_name}. {e}. Skipping.")
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

    Supports various formats:
    - Numeric: 1, -1
    - String with spaces: "+ 1", "- 1"

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

            # Try to parse the polarity
            try:
                polarity_int = _parse_polarity(polarity)
            except ValueError as e:
                # Skip silently if it's a known "no connection" case
                error_msg = str(e)
                if error_msg in ["NaN or None value", "Empty or zero value", "Zero value"]:
                    continue
                # Otherwise, warn about truly invalid values
                print(f"Warning: Invalid polarity value '{polarity}' for "
                      f"{source_name} -> {target_name}. {e}. Skipping.")
                continue

            # Create concepts and link
            source_concept = Concept.get_concept(source_name)
            target_concept = Concept.get_concept(target_name)
            influence = Influence.from_polarity(polarity_int)

            link = Link(source_concept, influence, target_concept)
            links.add(link)

    print(f"Loaded {len(links)} links from adjacency matrix")

    return links
