"""
Network representation and loop detection for causal loop diagrams.
"""

from typing import Dict, Set
from .models import Concept, Link
from .sequence import Sequence
from .loop_set import LoopSet


class Node:
    """Represents a node in the diagram network."""

    def __init__(self, concept: Concept):
        self.concept = concept
        self.outward_links: Dict[Concept, Link] = {}
        self.inward_links: Dict[Concept, Link] = {}

    def add_inward_link(self, link: Link) -> bool:
        """Add an inward link (link pointing to this node)."""
        if link.source in self.inward_links:
            return False
        self.inward_links[link.source] = link
        return True

    def add_outward_link(self, link: Link) -> bool:
        """Add an outward link (link from this node to another)."""
        if link.target in self.outward_links:
            return False
        self.outward_links[link.target] = link
        return True

    def is_sink(self) -> bool:
        """Check if this node is a sink (no outward links)."""
        return len(self.outward_links) == 0

    def is_source(self) -> bool:
        """Check if this node is a source (no inward links)."""
        return len(self.inward_links) == 0

    def remove_links_to(self, concept: Concept) -> bool:
        """Remove all links to/from a specific concept."""
        removed = False
        if concept in self.outward_links:
            del self.outward_links[concept]
            removed = True
        if concept in self.inward_links:
            del self.inward_links[concept]
            removed = True
        return removed


class DiagramNetwork:
    """
    Represents a causal loop diagram as a directed graph.

    Handles network construction, preprocessing (removing sources/sinks),
    and loop detection via recursive depth-first search.
    """

    def __init__(self):
        self.nodes: Dict[Concept, Node] = {}

    def add_link(self, link: Link):
        """
        Add a link to the network.

        Args:
            link: The link to add
        """
        source = link.source
        target = link.target

        # Get or create source node
        if source not in self.nodes:
            self.nodes[source] = Node(source)
        self.nodes[source].add_outward_link(link)

        # Get or create target node
        if target not in self.nodes:
            self.nodes[target] = Node(target)
        self.nodes[target].add_inward_link(link)

    def remove_node(self, concept: Concept):
        """
        Remove a node and all links to/from it.

        Args:
            concept: The concept to remove
        """
        # Remove links from other nodes to this one
        for node in self.nodes.values():
            node.remove_links_to(concept)

        # Remove the node itself
        if concept in self.nodes:
            del self.nodes[concept]

    def remove_sources_and_sinks(self) -> int:
        """
        Remove all source and sink nodes (nodes not in any loop).

        Returns:
            Number of nodes removed
        """
        to_remove: Set[Concept] = set()

        for node in self.nodes.values():
            if node.is_source() or node.is_sink():
                to_remove.add(node.concept)

        for concept in to_remove:
            for node in self.nodes.values():
                node.remove_links_to(concept)
            if concept in self.nodes:
                del self.nodes[concept]

        return len(to_remove)

    def get_loops(self, verbose: bool = True) -> LoopSet:
        """
        Find all loops in the network.

        This method:
        1. Removes source and sink nodes (not part of any loop)
        2. For each remaining node, finds all loops passing through it
        3. Removes the node after processing (optimization)
        4. Returns a LoopSet containing all unique loops

        Args:
            verbose: If True, print progress messages

        Returns:
            LoopSet containing all loops found
        """
        # Remove all sources and sinks repeatedly until none remain
        while self.remove_sources_and_sinks() > 0:
            pass

        loop_set = LoopSet()

        # Process each node
        all_nodes = list(self.nodes.values())

        for node in all_nodes:
            # Only process if node is still in network and not a source/sink
            if node.concept in self.nodes:
                if not node.is_sink() and not node.is_source():
                    # Find all loops through this node
                    self._get_loops_recursive(node, Sequence(), loop_set, verbose)

                    # Remove this node (optimization: already found all loops through it)
                    self.remove_node(node.concept)

                    # Clean up any new sources/sinks created
                    while self.remove_sources_and_sinks() > 0:
                        pass

        loop_set.finalize()

        if verbose:
            print(f"\nTotal loops found: {loop_set.get_size()}")

        return loop_set

    def _get_loops_recursive(self, node: Node, sequence: Sequence,
                             loop_set: LoopSet, verbose: bool):
        """
        Recursively find loops starting from a node.

        Args:
            node: Current node
            sequence: Current sequence of links
            loop_set: Set to store found loops
            verbose: If True, print found loops
        """
        # Try each outward link from this node
        for target_concept, link in node.outward_links.items():
            # Create a copy of the current sequence
            next_sequence = Sequence(copy_from=sequence)

            # Add this link to the sequence
            next_sequence.add_link(link)

            if next_sequence.is_loop:
                # Found a complete loop!
                if verbose:
                    print(f"FOUND LOOP {loop_set.get_size() + 1}: {next_sequence}")

                added_seq = loop_set.add_loop(next_sequence)

                if verbose:
                    print(f"ADDED AS {added_seq}")

            elif next_sequence.is_closed:
                # Sequence closed but not a loop - dead end
                pass

            else:
                # Continue recursing
                if target_concept in self.nodes:
                    self._get_loops_recursive(
                        self.nodes[target_concept],
                        next_sequence,
                        loop_set,
                        verbose
                    )
