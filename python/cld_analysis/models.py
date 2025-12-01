"""
Core data models for CLD analysis.
"""

from enum import Enum
from typing import Optional


class Influence(Enum):
    """Represents the type of influence in a causal relationship."""
    INCREASES = "INCREASES"
    DECREASES = "DECREASES"

    @classmethod
    def from_polarity(cls, polarity: int) -> 'Influence':
        """
        Convert polarity value to Influence.

        Args:
            polarity: +1 for positive (INCREASES), -1 for negative (DECREASES)

        Returns:
            Influence enum value
        """
        if polarity > 0:
            return cls.INCREASES
        elif polarity < 0:
            return cls.DECREASES
        else:
            raise ValueError(f"Invalid polarity value: {polarity}. Must be +1 or -1.")


class Polarity(Enum):
    """Represents the polarity of a feedback loop."""
    POSITIVE = "POSITIVE"  # Reinforcing loop
    NEGATIVE = "NEGATIVE"  # Balancing loop


class Concept:
    """
    Represents a concept/entity in the causal loop diagram.

    Attributes:
        name: The name/representation of the concept
        id: Unique identifier for this concept
    """

    _next_id = 0
    _instances = {}

    def __init__(self, name: str):
        self.name = name
        self.id = Concept._next_id
        Concept._next_id += 1

    def get_representation(self) -> str:
        """Get the string representation of this concept."""
        return self.name

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"Concept({self.name!r}, id={self.id})"

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Concept):
            return False
        return self.id == other.id

    @classmethod
    def reset(cls):
        """Reset the concept factory (for testing purposes)."""
        cls._next_id = 0
        cls._instances.clear()

    @classmethod
    def get_concept(cls, name: str) -> 'Concept':
        """
        Get or create a concept with the given name.

        This implements the factory pattern to ensure only one instance
        exists for each unique concept name.

        Args:
            name: The name of the concept

        Returns:
            The Concept instance for this name
        """
        if name not in cls._instances:
            cls._instances[name] = cls(name)
        return cls._instances[name]

    @classmethod
    def get_all(cls):
        """Get all concept instances."""
        return list(cls._instances.values())


class Link:
    """
    Represents a directed link between two concepts with an influence type.

    Attributes:
        source: The source concept
        target: The target concept
        influence: The type of influence (INCREASES or DECREASES)
    """

    def __init__(self, source: Concept, influence: Influence, target: Concept):
        self.source = source
        self.influence = influence
        self.target = target

    def __str__(self) -> str:
        return f"{self.source.name} -{self.influence.value}-> {self.target.name}"

    def __repr__(self) -> str:
        return f"Link({self.source.name!r}, {self.influence}, {self.target.name!r})"

    def __hash__(self) -> int:
        return hash((self.source.id, self.influence, self.target.id))

    def __eq__(self, other) -> bool:
        if not isinstance(other, Link):
            return False
        return (self.source.id == other.source.id and
                self.influence == other.influence and
                self.target.id == other.target.id)
