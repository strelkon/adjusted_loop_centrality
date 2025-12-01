# Python Implementation of CLD Analysis Tool

## Overview

This document describes the new Python implementation of the Causal Loop Diagram (CLD) analysis tool, which has been reimplemented from the original Java codebase.

## What Was Implemented

### Core Functionality

All core functionality from the Java implementation has been ported to Python:

1. **Loop Detection Algorithm**
   - Recursive depth-first search through the network
   - Automatic removal of source and sink nodes
   - Detection of all unique feedback loops
   - Classification as reinforcing or balancing loops

2. **Centrality Scoring**
   - Levenshtein distance calculation with rotation support
   - Greedy algorithm for grouping similar loops
   - Weighted scoring based on loop diversity
   - Identification of leverage points in the system

3. **Input/Output**
   - NEW: Direct support for Excel adjacency matrices
   - NEW: Support for CSV adjacency matrices
   - Export to multiple CSV formats
   - Compatible output format with original Java version

### New Features

The Python implementation adds several user-friendly features:

1. **Adjacency Matrix Support**
   - Direct loading from Excel (.xlsx) files
   - Support for CSV files
   - Automatic parsing of matrix format
   - Clear format: sources in rows, targets in columns, polarities (+1/-1) in cells

2. **Simplified API**
   - Clean, documented Python API
   - Command-line interface for easy use
   - Type hints for better IDE support
   - More intuitive method names

3. **Better Documentation**
   - Comprehensive README
   - Getting started guide
   - Example scripts
   - Inline code documentation

## Directory Structure

```
python/
├── cld_analysis/              # Main package
│   ├── __init__.py           # Package initialization
│   ├── models.py             # Core data models (Concept, Link, Influence)
│   ├── sequence.py           # Sequence/Loop representation
│   ├── network.py            # Network and loop detection
│   ├── loop_set.py           # Loop collection and scoring
│   ├── loader.py             # Main entry point (LoopSetLoader)
│   ├── matrix_loader.py      # Adjacency matrix parsers
│   └── utils.py              # Utility functions (Levenshtein distance)
│
├── analyze_matrix.py         # Command-line interface
├── example.py                # Basic usage example
├── simple_example.py         # Complete working example
├── create_sample_matrix.py   # Creates sample data
├── requirements.txt          # Python dependencies
├── README.md                 # Full documentation
└── GETTING_STARTED.md        # Quick start guide
```

## How to Use

### Quick Start

1. **Install dependencies:**
   ```bash
   cd python
   pip install -r requirements.txt
   ```

2. **Test the installation:**
   ```bash
   python simple_example.py
   ```

3. **Analyze your data:**
   ```bash
   python analyze_matrix.py your_adjacency_matrix.xlsx
   ```

### Input Format

The tool accepts adjacency matrices in this format:

|          | Target1 | Target2 | Target3 |
|----------|---------|---------|---------|
| Source1  |    1    |   -1    |    0    |
| Source2  |   -1    |    0    |    1    |
| Source3  |    0    |    1    |   -1    |

Where:
- `+1` = Positive influence (source INCREASES target)
- `-1` = Negative influence (source DECREASES target)
- `0` or empty = No connection

This is compatible with the format mentioned in the request (e.g., OAIMicrosoft_v6_17.11.25.xlsx).

### Output Files

The tool generates:

1. **concept_nodes.csv** - Concept scores and loop counts
2. **concept_links.csv** - Link information with loop traversal counts
3. **loop_nodes.csv** - Loop sizes
4. **scores.txt** - Ranked concept scores

## Implementation Details

### Key Classes

1. **Concept** (`models.py`)
   - Represents a concept/entity in the diagram
   - Factory pattern ensures unique instances
   - Comparable for sorting

2. **Link** (`models.py`)
   - Directed edge with influence type (INCREASES/DECREASES)
   - Hashable for set operations

3. **Sequence** (`sequence.py`)
   - Represents a path or loop
   - Detects closed loops automatically
   - Rotation support for canonical form
   - Distance calculation to other sequences

4. **DiagramNetwork** (`network.py`)
   - Graph representation with nodes and links
   - Loop detection via DFS
   - Source/sink removal optimization

5. **LoopSet** (`loop_set.py`)
   - Manages collection of unique loops
   - Calculates pairwise distances
   - Implements centrality scoring algorithm

6. **LoopSetLoader** (`loader.py`)
   - Main entry point API
   - Orchestrates the analysis pipeline
   - Handles file I/O

### Algorithm Equivalence

The Python implementation uses identical algorithms to the Java version:

- **Loop Detection**: Same recursive DFS with pruning
- **Levenshtein Distance**: Same optimized implementation with rotation
- **Centrality Scoring**: Same greedy algorithm with distance weighting
- **Loop Normalization**: Same rotation to lowest-ID-first

Results should be identical to the Java implementation (within floating-point precision).

## Dependencies

- **numpy**: For efficient matrix operations
- **pandas**: For reading/writing Excel and CSV files
- **openpyxl**: Excel file support

All are standard, well-maintained packages available via pip.

## Performance

The Python implementation has comparable performance to Java for most networks:

- Loop detection: O(n!) worst case, but heavily optimized with pruning
- Distance calculation: Cached to avoid recomputation
- Large networks (1000+ loops) may take several minutes

For very large networks, the Java version may be faster due to JIT compilation, but the difference is typically not significant for analysis purposes.

## Testing

The implementation has been tested with:

1. Small test networks (5 concepts, 8 links, 5 loops)
2. Manual verification of loop detection
3. Score calculation validation
4. Output format verification

To run tests:
```bash
cd python
python simple_example.py
```

## Comparison with Java Implementation

### What's the Same

- Core algorithms (identical)
- Loop detection logic (identical)
- Scoring methodology (identical)
- Output format (compatible)

### What's Different

- **Input**: Python adds adjacency matrix support (Java uses edge list CSV)
- **API**: Python has cleaner, more Pythonic interface
- **Documentation**: Python has more comprehensive docs
- **CLI**: Python has integrated command-line tool

### Migration Path

To migrate from Java to Python:

1. Convert your edge list CSV to an adjacency matrix (or use the matrix directly)
2. Use `python analyze_matrix.py your_matrix.xlsx`
3. Results will be in the same format as Java output

## Future Enhancements

Potential improvements for future versions:

- Visualization of loops and scores
- Interactive network exploration
- Parallel processing for large networks
- Additional distance metrics
- Export to graph formats (GraphML, etc.)

## Credits

**Original Java Implementation:**
- Based on research by Rozhkov, Murphy, and Pijanowski
- Part of the SUReNet urban-rural systems project

**Python Implementation:**
- Reimplemented from Java codebase
- Maintains algorithm fidelity
- Adds user-friendly features

## License

This implementation is based on the original Java codebase and maintains compatibility with the research methodology described in the associated publications.

## Contact

For questions about:
- **The methodology**: See the research paper by Rozhkov et al. (2025)
- **The Java version**: Check the `Java/` directory
- **The Python version**: See `python/README.md` and `python/GETTING_STARTED.md`
