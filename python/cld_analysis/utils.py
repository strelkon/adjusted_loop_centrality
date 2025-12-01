"""
Utility functions for CLD analysis.
"""

import numpy as np
from typing import List


def levenshtein_distance(a: List[int], b: List[int]) -> int:
    """
    Calculate the Levenshtein distance between two sequences.

    Args:
        a: First sequence of integers
        b: Second sequence of integers

    Returns:
        The Levenshtein distance
    """
    m = len(a)
    n = len(b)

    # Create distance matrix
    matrix = np.zeros((m + 1, n + 1), dtype=int)

    # Initialize first column and first row
    for i in range(m + 1):
        matrix[i][0] = i
    for j in range(n + 1):
        matrix[0][j] = j

    # Fill in the matrix
    for j in range(1, n + 1):
        for i in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                cost = 0
            else:
                cost = 1

            matrix[i][j] = min(
                matrix[i - 1][j] + 1,      # deletion
                matrix[i][j - 1] + 1,      # insertion
                matrix[i - 1][j - 1] + cost  # substitution
            )

    return int(matrix[m][n])


def levenshtein_distance_with_rotation(a: List[int], b: List[int]) -> int:
    """
    Calculate the minimum Levenshtein distance between two sequences,
    considering all possible rotations (for cyclic sequences/loops).

    Args:
        a: First sequence of integers
        b: Second sequence of integers

    Returns:
        The minimum Levenshtein distance across all rotations
    """
    m = len(a)
    n = len(b)

    if m == 0 or n == 0:
        return m + n

    # Create doubled arrays to allow rotation by sliding the start index
    a_double = a + a
    b_double = b + b

    # Determine the theoretical minimum (bail-out condition)
    min_possible = max(0, abs(m - n))

    # Start with the maximum possible distance
    lowest = m + n

    # Create the distance matrix (reused for each rotation)
    matrix = np.zeros((m + 1, n + 1), dtype=int)

    # Try all rotations
    for a_start in range(m):
        for b_start in range(n):
            # Initialize first column and row
            for i in range(m + 1):
                matrix[i][0] = i
            for j in range(n + 1):
                matrix[0][j] = j

            # Calculate Levenshtein distance for this rotation
            early_exit = False
            for j in range(1, n + 1):
                letter_b = b_double[b_start + j - 1]
                lowest_in_row = j

                for i in range(1, m + 1):
                    letter_a = a_double[a_start + i - 1]

                    if letter_a == letter_b:
                        cost = 0
                    else:
                        cost = 1

                    matrix[i][j] = min(
                        matrix[i - 1][j] + 1,      # deletion
                        matrix[i][j - 1] + 1,      # insertion
                        matrix[i - 1][j - 1] + cost  # substitution
                    )

                    lowest_in_row = min(lowest_in_row, matrix[i][j])

                # Early exit if this rotation can't improve the result
                if lowest_in_row >= lowest:
                    early_exit = True
                    break

            if not early_exit:
                lowest = min(matrix[m][n], lowest)

                # If we've found the theoretical minimum, we can stop
                if lowest == min_possible:
                    return lowest

    return lowest


def rotate_array(arr: List[int]) -> List[int]:
    """
    Rotate an array by moving the first element to the end.

    Args:
        arr: Array to rotate

    Returns:
        Rotated array
    """
    if len(arr) <= 1:
        return arr.copy()
    return arr[1:] + [arr[0]]
