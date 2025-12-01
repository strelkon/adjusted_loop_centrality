"""
Sequence class for representing paths and loops in causal diagrams.
"""

from typing import List, Set, Optional
from enum import Enum
from .models import Link, Concept, Influence, Polarity
from .utils import levenshtein_distance_with_rotation


class SequenceType(Enum):
    """Types of sequences."""
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    REINFORCING_LOOP = "REINFORCING_LOOP"
    BALANCING_LOOP = "BALANCING_LOOP"


class Sequence:
    """
    Represents a sequence of links forming a path or loop.

    A sequence is 'closed' if the last link's target equals any earlier concept.
    A sequence is a 'loop' if the last link's target equals the first link's source.
    """

    _id_counter = 0

    def __init__(self, links: Optional[List[Link]] = None, copy_from: Optional['Sequence'] = None):
        """
        Create a new sequence.

        Args:
            links: Optional list of links to initialize the sequence
            copy_from: Optional sequence to copy from (deep copy)
        """
        self.links: List[Link] = []
        self.id = Sequence._id_counter
        Sequence._id_counter += 1

        self.is_loop = False
        self.is_closed = False
        self.count_negative_influences = 0

        # Cached values
        self._sequence_as_ints: Optional[List[int]] = None
        self._representation: Optional[str] = None

        if copy_from is not None:
            # Deep copy constructor
            for link in copy_from.links:
                self.links.append(Link(link.source, link.influence, link.target))
            self._init()
        elif links is not None:
            self.links = links.copy()
            self._init()

    def add_link(self, link: Link) -> bool:
        """
        Add a link to the end of this sequence.

        Args:
            link: The link to add

        Returns:
            True if added successfully, False if sequence is already closed
        """
        if self.is_closed:
            return False

        self.links.append(link)
        self._init()
        return True

    def _init(self):
        """Initialize or re-initialize computed properties."""
        self._set_count_negative_influences()
        self._detect_closed_loop()
        self._sequence_as_ints = None  # Reset cache
        self._representation = None  # Reset cache

    def _set_count_negative_influences(self):
        """Count the number of negative influence (DECREASES) links."""
        self.count_negative_influences = sum(
            1 for link in self.links if link.influence == Influence.DECREASES
        )

    def _detect_closed_loop(self):
        """Detect if this sequence is closed or a loop."""
        if len(self.links) == 0:
            self.is_closed = False
            self.is_loop = False
            return

        last_target = self.links[-1].target
        idx = self._index_of_source_with_concept(last_target)

        self.is_closed = (idx != -1)
        self.is_loop = (idx == 0)

    def _index_of_source_with_concept(self, concept: Concept) -> int:
        """
        Find the index of the link with the given concept as source.

        Args:
            concept: The concept to search for

        Returns:
            Index of the link, or -1 if not found
        """
        for i, link in enumerate(self.links):
            if link.source.id == concept.id:
                return i
        return -1

    def has_source(self, concept: Concept) -> bool:
        """Check if any link in this sequence has the given concept as source."""
        return self._index_of_source_with_concept(concept) != -1

    def rotate(self):
        """Rotate the loop by moving the first link to the end."""
        if not self.is_loop or len(self.links) == 0:
            return

        self.links.append(self.links.pop(0))

    def rotate_to_concept(self, concept: Concept):
        """
        Rotate until the specified concept is at the first position.

        Args:
            concept: The concept to rotate to
        """
        if not self.is_loop:
            return

        if self._index_of_source_with_concept(concept) == -1:
            return

        if len(self.links) == 0:
            return

        while self.links[0].source.id != concept.id:
            self.rotate()

    def rotate_to_standard(self):
        """Rotate the loop so the lowest-ID concept is first."""
        if not self.is_loop or len(self.links) == 0:
            return

        lowest_concept = min(self.links, key=lambda link: link.source.id).source
        self.rotate_to_concept(lowest_concept)

    def get_size(self) -> int:
        """Get the number of links in this sequence."""
        return len(self.links)

    def get_sequence_as_ints(self) -> List[int]:
        """
        Get the sequence as a list of concept IDs (sources only).

        Returns:
            List of concept IDs
        """
        if self._sequence_as_ints is None:
            self._sequence_as_ints = [link.source.id for link in self.links]
        return self._sequence_as_ints.copy()

    def distance(self, other: 'Sequence') -> float:
        """
        Calculate the normalized Levenshtein distance to another sequence.

        Args:
            other: The other sequence

        Returns:
            Normalized distance (0.0 to 1.0)
        """
        if not self.is_loop or not other.is_loop:
            return float('inf')

        if len(self.links) == 0 or len(other.links) == 0:
            return float('inf')

        # Get sequences as integer arrays
        a = self.get_sequence_as_ints()
        b = other.get_sequence_as_ints()

        # Calculate Levenshtein distance with rotation
        lev_dist = levenshtein_distance_with_rotation(a, b)

        # Normalize by the sum of lengths
        denominator = len(a) + len(b)
        return lev_dist / denominator if denominator > 0 else 0.0

    def get_type(self) -> SequenceType:
        """Get the type of this sequence."""
        if not self.is_closed:
            return SequenceType.OPEN
        elif not self.is_loop:
            return SequenceType.CLOSED
        elif self.count_negative_influences % 2 == 1:
            return SequenceType.BALANCING_LOOP
        else:
            return SequenceType.REINFORCING_LOOP

    def get_polarity(self) -> Polarity:
        """Get the polarity of this loop."""
        if self.count_negative_influences % 2 == 1:
            return Polarity.NEGATIVE  # Balancing
        else:
            return Polarity.POSITIVE  # Reinforcing

    def head(self) -> Optional[Concept]:
        """Get the first concept in this sequence."""
        return self.links[0].source if len(self.links) > 0 else None

    def tail(self) -> Optional[Concept]:
        """Get the target of the last link."""
        return self.links[-1].target if len(self.links) > 0 else None

    def get_all_concepts(self) -> Set[Concept]:
        """Get all unique concepts in this sequence."""
        concepts = set()
        for link in self.links:
            concepts.add(link.source)
        if len(self.links) > 0:
            concepts.add(self.links[-1].target)
        return concepts

    def contains_link(self, source: Concept, target: Concept) -> bool:
        """
        Check if this sequence contains a link from source to target.

        Args:
            source: Source concept
            target: Target concept

        Returns:
            True if the link exists in this sequence
        """
        for link in self.links:
            if link.source.id == source.id and link.target.id == target.id:
                return True
        return False

    def get_id(self) -> str:
        """Get the string ID of this sequence."""
        return f"SEQ_{self.id}"

    def __str__(self) -> str:
        """Get string representation."""
        if self._representation is None:
            self._representation = self._create_short_representation()
        return self._representation

    def _create_short_representation(self) -> str:
        """Create a short string representation using concept IDs."""
        if self.is_loop:
            prefix = "LOOP: "
        elif self.is_closed:
            prefix = "CLOSED: "
        else:
            prefix = "SEQUENCE: "

        if len(self.links) == 0:
            return prefix + "<EMPTY>"

        result = prefix + str(self.links[0].source.id)

        for i, link in enumerate(self.links):
            symbol = "+" if link.influence == Influence.INCREASES else "-"

            if self.is_closed and i == len(self.links) - 1:
                target_str = f"{{{link.target.id}}}"
            else:
                target_str = str(link.target.id)

            result += symbol + target_str

        return result

    def __repr__(self) -> str:
        return f"Sequence(id={self.id}, size={self.get_size()}, type={self.get_type()})"

    def __eq__(self, other) -> bool:
        """Check equality based on string representation."""
        if not isinstance(other, Sequence):
            return False
        if self.get_size() != other.get_size():
            return False
        return str(self) == str(other)

    def __hash__(self) -> int:
        return hash(str(self))

    def __lt__(self, other: 'Sequence') -> bool:
        """Compare sequences for sorting."""
        return str(self) < str(other)

    @classmethod
    def reset_counter(cls):
        """Reset the ID counter (for testing)."""
        cls._id_counter = 0
