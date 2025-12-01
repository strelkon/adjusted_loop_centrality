"""
LoopSetLoader - Main entry point for loading and analyzing causal loop diagrams.
"""

import pandas as pd
from typing import Dict, Set
from pathlib import Path
from .models import Concept, Link
from .network import DiagramNetwork
from .loop_set import LoopSet
from .matrix_loader import load_adjacency_matrix_from_excel, load_adjacency_matrix_from_csv


class LoopSetLoader:
    """
    Main class for loading causal loop diagrams and calculating centrality scores.

    This class orchestrates the entire analysis pipeline:
    1. Load network from adjacency matrix (Excel or CSV)
    2. Detect all feedback loops
    3. Calculate centrality scores for concepts
    4. Export results
    """

    def __init__(self):
        self.network: DiagramNetwork = None
        self.all_links: Set[Link] = None
        self.loop_set: LoopSet = None
        self.scores: Dict[Concept, float] = None

    def load_from_adjacency_matrix(self, filepath: str, sheet_name=0, verbose: bool = True):
        """
        Load a causal loop diagram from an adjacency matrix file.

        Supports both Excel (.xlsx) and CSV files.
        The matrix format should have:
        - First row: target concept names (starting from column B)
        - First column: source concept names (starting from row 2)
        - Cell values: +1 for positive influence, -1 for negative influence

        Args:
            filepath: Path to the Excel or CSV file
            sheet_name: For Excel files, the sheet name or index (default: 0)
            verbose: If True, print progress messages

        Returns:
            The LoopSet containing all detected loops
        """
        if verbose:
            print(f"Loading network from: {filepath}")

        # Reset the concept factory for clean state
        Concept.reset()

        # Load links from file
        file_path = Path(filepath)
        if file_path.suffix.lower() in ['.xlsx', '.xls']:
            self.all_links = load_adjacency_matrix_from_excel(filepath, sheet_name)
        elif file_path.suffix.lower() == '.csv':
            self.all_links = load_adjacency_matrix_from_csv(filepath)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

        if verbose:
            print(f"Loaded {len(self.all_links)} links")

        # Build the network
        self.network = DiagramNetwork()
        for link in self.all_links:
            self.network.add_link(link)

        if verbose:
            print(f"{len(self.network.nodes)} nodes in network")

        # Find all loops
        if verbose:
            print("\nFinding loops...")

        self.loop_set = self.network.get_loops(verbose=verbose)

        if verbose:
            print(f"\nFound {self.loop_set.get_size()} unique loops")
            self.loop_set.report()

        return self.loop_set

    def get_scores(self, verbose: bool = True):
        """
        Calculate centrality scores for all concepts.

        Args:
            verbose: If True, print progress messages

        Returns:
            Dictionary mapping concepts to their centrality scores
        """
        if self.scores is None:
            if self.loop_set is None:
                raise ValueError("Must load network and find loops before calculating scores")

            self.scores = self.loop_set.get_concepts_and_scores(verbose=verbose)

        return self.scores

    def write_concept_node_file(self, output_path: str):
        """
        Write concept scores to a CSV file.

        Output format:
        id,numberOfLoops,relevanceScore

        Args:
            output_path: Path to the output CSV file
        """
        if self.scores is None:
            self.get_scores()

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("id,numberOfLoops,relevanceScore\n")

            for concept in Concept.get_all():
                score = self.scores.get(concept, 0.0)
                loops_count = self.loop_set.loops_containing_concept(concept)
                f.write(f"{concept.get_representation()},{loops_count},{score}\n")

        print(f"Wrote concept scores to: {output_path}")

    def write_concept_link_file(self, output_path: str):
        """
        Write link information to a CSV file.

        Output format:
        source,target,linkInfluence,loopsTraversing

        Args:
            output_path: Path to the output CSV file
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("source,target,linkInfluence,loopsTraversing\n")

            for link in self.all_links:
                loop_count = self.loop_set.loops_containing_link(link.source, link.target)
                if loop_count > 0:
                    f.write(f"{link.source.get_representation()},"
                           f"{link.target.get_representation()},"
                           f"{link.influence.value},"
                           f"{loop_count}\n")

        print(f"Wrote link information to: {output_path}")

    def write_loop_node_file(self, output_path: str):
        """
        Write loop information to a CSV file.

        Output format:
        id,size

        Args:
            output_path: Path to the output CSV file
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("id,size\n")

            for loop in self.loop_set.loops_sorted_by_size():
                f.write(f"{loop.get_id()},{loop.get_size()}\n")

        print(f"Wrote loop information to: {output_path}")

    def report_scores(self, output_path: str):
        """
        Write a simple score report.

        Output format:
        ConceptName = score

        Args:
            output_path: Path to the output file
        """
        if self.scores is None:
            self.get_scores()

        # Sort by score (descending)
        sorted_concepts = sorted(self.scores.items(), key=lambda x: x[1], reverse=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            for concept, score in sorted_concepts:
                f.write(f"{concept.get_representation()} = {score}\n")

        print(f"Wrote score report to: {output_path}")

    def get_top_concepts(self, n: int = 10) -> list:
        """
        Get the top N concepts by centrality score.

        Args:
            n: Number of top concepts to return

        Returns:
            List of tuples (concept, score) sorted by score descending
        """
        if self.scores is None:
            self.get_scores()

        sorted_concepts = sorted(self.scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_concepts[:n]

    def summary(self):
        """Print a summary of the analysis."""
        print("\n" + "="*60)
        print("CAUSAL LOOP DIAGRAM ANALYSIS SUMMARY")
        print("="*60)

        print(f"\nNetwork Statistics:")
        print(f"  Total concepts: {len(Concept.get_all())}")
        print(f"  Total links: {len(self.all_links)}")
        print(f"  Total loops: {self.loop_set.get_size()}")

        if self.scores:
            print(f"\nTop 10 Most Central Concepts:")
            for i, (concept, score) in enumerate(self.get_top_concepts(10), 1):
                loops = self.loop_set.loops_containing_concept(concept)
                print(f"  {i}. {concept.name}: {score:.2f} (in {loops} loops)")

        print("\n" + "="*60)
