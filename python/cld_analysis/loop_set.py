"""
LoopSet class for managing collections of loops and calculating centrality scores.
"""

from typing import Dict, List, Set
import numpy as np
from .sequence import Sequence
from .models import Concept


class LoopSet:
    """
    Maintains a collection of unique loops and calculates centrality scores.

    All loops are rotated to standard position (lowest ID first) and
    duplicates are automatically removed.
    """

    def __init__(self):
        self.loops: Set[Sequence] = set()
        self.loops_list: List[Sequence] = []  # For ordering
        self.distances: Dict[tuple, float] = {}  # Cache for pairwise distances

    def add_loop(self, to_add: Sequence) -> Sequence:
        """
        Add a loop to this set.

        Only actual loops are added (not open or closed sequences).
        Duplicates are detected and not re-added.
        The loop is copied and rotated to standard form before storage.

        Args:
            to_add: The sequence to add

        Returns:
            The stored sequence (either newly added or existing duplicate),
            or None if not a loop
        """
        if not to_add.is_loop:
            return None

        # Create a copy and rotate to standard position
        loop = Sequence(copy_from=to_add)
        loop.rotate_to_standard()

        # Check for duplicates
        rep = str(loop)
        for existing_loop in self.loops:
            if str(existing_loop) == rep:
                return existing_loop

        # Add the new loop
        self.loops.add(loop)
        return loop

    def finalize(self):
        """
        Finalize the loop set by assigning sequential IDs and sorting.

        This should be called after all loops have been added and before
        calculating scores.
        """
        # Convert to list and sort
        self.loops_list = sorted(list(self.loops))

        # Reassign IDs sequentially
        for idx, loop in enumerate(self.loops_list):
            loop.id = idx

        print("\nFinalized loop set:")
        for loop in self.loops_list:
            print(f"{loop.id}: {loop}")

    def get_size(self) -> int:
        """Get the number of loops in this set."""
        return len(self.loops)

    def loops_sorted_by_size(self) -> List[Sequence]:
        """
        Get all loops sorted by size (descending).

        Returns:
            List of loops sorted by size
        """
        return sorted(self.loops_list, key=lambda s: s.get_size(), reverse=True)

    def loops_containing_link(self, source: Concept, target: Concept) -> int:
        """
        Count loops containing a specific link.

        Args:
            source: Source concept
            target: Target concept

        Returns:
            Number of loops containing this link
        """
        count = 0
        for loop in self.loops:
            if loop.contains_link(source, target):
                count += 1
        return count

    def loops_containing_concept(self, concept: Concept) -> int:
        """
        Count loops containing a specific concept.

        Args:
            concept: The concept to search for

        Returns:
            Number of loops containing this concept
        """
        count = 0
        for loop in self.loops:
            if loop.has_source(concept):
                count += 1
        return count

    def get_distance(self, seq_a: Sequence, seq_b: Sequence) -> float:
        """
        Get the distance between two sequences, using cache if available.

        Args:
            seq_a: First sequence
            seq_b: Second sequence

        Returns:
            Normalized distance between sequences
        """
        # Create cache key (order doesn't matter for distance)
        key = (min(seq_a.id, seq_b.id), max(seq_a.id, seq_b.id))

        if key not in self.distances:
            # Calculate and cache
            dist = seq_a.distance(seq_b)
            self.distances[key] = dist

        return self.distances[key]

    def get_all_concepts(self) -> Set[Concept]:
        """Get all unique concepts across all loops."""
        concepts = set()
        for loop in self.loops:
            concepts.update(loop.get_all_concepts())
        return concepts

    def get_concepts_and_scores(self, verbose: bool = False) -> Dict[Concept, float]:
        """
        Calculate centrality scores for all concepts.

        This implements a greedy algorithm that:
        1. For each concept, finds all loops containing it
        2. Groups loops by similarity using Levenshtein distance
        3. Assigns scores inversely proportional to similarity
        4. Final score = sum of (loop_size × distance_to_closest_scored_loop)

        Args:
            verbose: If True, print progress information

        Returns:
            Dictionary mapping concepts to their centrality scores
        """
        scores: Dict[Concept, float] = {}

        # Get loops sorted by size
        loops_by_size = self.loops_sorted_by_size()
        concepts = self.get_all_concepts()

        if verbose:
            print("\nEntering scoring phase...")
            print(f"Total concepts: {len(concepts)}")
            print(f"Total loops: {len(self.loops)}")

        concept_count = 0
        for concept in concepts:
            concept_count += 1

            if verbose:
                print(f"\nScoring concept: {concept.name} ({concept_count}/{len(concepts)})")

            # Find all loops containing this concept
            source_loops = []
            for loop in loops_by_size:
                if loop.has_source(concept):
                    source_loops.append({'seq': loop, 'score': 1.0})

            num_loops = len(source_loops)

            if num_loops <= 1:
                if verbose:
                    print(f"  {concept.name} is in {num_loops} loop(s) - skipping")
                continue

            if verbose:
                print(f"  {concept.name} appears in {num_loops} loops")

            # Start with the last loop in the list
            scored_loops = []
            last_added = source_loops.pop()
            scored_loops.append(last_added)

            # Initial score is just the size of the first loop
            final_score = last_added['seq'].get_size()

            # Process remaining loops
            while source_loops:
                if verbose and len(source_loops) % 10 == 0:
                    print(f"  Processing... {len(source_loops)} loops remaining")

                # Update distances to the last added loop
                for source_loop in source_loops:
                    dist = self.get_distance(source_loop['seq'], last_added['seq'])
                    if dist < source_loop['score']:
                        source_loop['score'] = dist

                # Find the loop with minimum distance to any scored loop
                min_idx = 0
                min_score = float('inf')

                for idx, source_loop in enumerate(source_loops):
                    if source_loop['score'] < min_score:
                        min_score = source_loop['score']
                        min_idx = idx

                # Remove and score this loop
                last_added = source_loops.pop(min_idx)
                contribution = last_added['seq'].get_size() * last_added['score']
                final_score += contribution
                scored_loops.append(last_added)

            if verbose:
                print(f"  FINAL SCORE for {concept.name}: {final_score:.2f} "
                      f"(from {num_loops} loops)")

            scores[concept] = final_score

        return scores

    def report(self):
        """Print statistics about the loop set."""
        from collections import Counter
        from .sequence import SequenceType

        # Count by type
        type_counts = Counter()
        for loop in self.loops:
            type_counts[loop.get_type()] += 1

        print("\nLoop Statistics:")
        for seq_type in SequenceType:
            print(f"  {seq_type.value}: {type_counts[seq_type]}")

        # Count by size
        size_counts = Counter()
        max_size = 0
        for loop in self.loops:
            size = loop.get_size()
            size_counts[size] += 1
            max_size = max(max_size, size)

        print("\nLoops by size:")
        for size in range(1, max_size + 1):
            if size_counts[size] > 0:
                print(f"  Size {size}: {size_counts[size]} loops")
