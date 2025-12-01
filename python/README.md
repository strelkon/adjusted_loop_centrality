# Causal Loop Diagram (CLD) Analysis Tool

Python implementation of a tool for analyzing causal loop diagrams, identifying feedback loops, and calculating centrality scores.

This tool implements the methodology described in:
> Rozhkov, A., Murphy, J. T., & Pijanowski, B. C. (2025). Identifying leverage points for sustainable transitions in urban-rural systems.

## Features

- **Adjacency Matrix Input**: Load causal loop diagrams from Excel or CSV adjacency matrices
- **Loop Detection**: Automatically detect all feedback loops in the network using depth-first search
- **Loop Classification**: Distinguish between reinforcing and balancing loops
- **Centrality Scoring**: Calculate leverage point scores using similarity-weighted loop analysis
- **Export Results**: Generate CSV outputs for further analysis or visualization

## Installation

### Requirements

- Python 3.7 or higher
- numpy
- pandas
- openpyxl

### Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. The package is ready to use. No additional installation needed.

## Input Format

The tool accepts adjacency matrices in Excel (.xlsx) or CSV format:

- **First row**: Target concept names (starting from column B/column 2)
- **First column**: Source concept names (starting from row 2)
- **Cell values**:
  - `+1` or `1`: Positive influence (increases)
  - `-1`: Negative influence (decreases)
  - `0` or empty: No connection

### Example Matrix

|          | Target1 | Target2 | Target3 |
|----------|---------|---------|---------|
| Source1  |    1    |   -1    |    0    |
| Source2  |   -1    |    0    |    1    |
| Source3  |    0    |    1    |   -1    |

## Quick Start

### Simple Example

Run the simple example to see the tool in action:

```bash
python simple_example.py
```

This creates a small test network and analyzes it, showing all steps of the process.

### Using Your Own Data

```python
from cld_analysis import LoopSetLoader

# Create the loader
loader = LoopSetLoader()

# Load your adjacency matrix
loader.load_from_adjacency_matrix("your_file.xlsx", verbose=True)

# Calculate centrality scores
loader.get_scores(verbose=True)

# Display summary
loader.summary()

# Export results
loader.write_concept_node_file("concept_scores.csv")
loader.write_concept_link_file("link_info.csv")
loader.write_loop_node_file("loop_info.csv")
loader.report_scores("scores.txt")
```

## Output Files

The tool generates several output files:

### 1. Concept Nodes (`concept_scores.csv`)
- **id**: Concept name
- **numberOfLoops**: How many loops contain this concept
- **relevanceScore**: Centrality/leverage point score

### 2. Concept Links (`concept_links.csv`)
- **source**: Source concept
- **target**: Target concept
- **linkInfluence**: Type of influence (INCREASES/DECREASES)
- **loopsTraversing**: Number of loops containing this link

### 3. Loop Nodes (`loop_info.csv`)
- **id**: Loop identifier
- **size**: Number of links in the loop

### 4. Score Report (`scores.txt`)
- Ranked list of concepts with their scores

## How It Works

### 1. Loop Detection

The algorithm:
1. Removes source and sink nodes (not part of any loop)
2. Uses recursive depth-first search to find all loops
3. Normalizes loops by rotating to standard form (lowest ID first)
4. Removes duplicate loops

### 2. Loop Classification

Loops are classified based on the number of negative influences:
- **Reinforcing Loop**: Even number of negative influences (0, 2, 4, ...)
- **Balancing Loop**: Odd number of negative influences (1, 3, 5, ...)

### 3. Centrality Scoring

For each concept appearing in multiple loops:

1. Collect all loops containing the concept
2. Use a greedy algorithm to group similar loops
3. Calculate Levenshtein distance between loop sequences
4. Weight each loop's contribution inversely to its similarity with already-scored loops
5. Final score = Σ (loop_size × distance_to_closest_scored_loop)

Concepts in more diverse loops receive higher scores, indicating they are more central leverage points.

## API Reference

### LoopSetLoader

Main class for loading and analyzing causal loop diagrams.

#### Methods

- `load_from_adjacency_matrix(filepath, sheet_name=0, verbose=True)`
  - Load network from Excel or CSV file
  - Returns: LoopSet object

- `get_scores(verbose=True)`
  - Calculate centrality scores
  - Returns: Dictionary mapping concepts to scores

- `summary()`
  - Print analysis summary

- `get_top_concepts(n=10)`
  - Get top N concepts by score
  - Returns: List of (concept, score) tuples

- `write_concept_node_file(output_path)`
  - Export concept scores to CSV

- `write_concept_link_file(output_path)`
  - Export link information to CSV

- `write_loop_node_file(output_path)`
  - Export loop information to CSV

- `report_scores(output_path)`
  - Export ranked scores to text file

## Advanced Usage

### Accessing Loop Details

```python
from cld_analysis import LoopSetLoader

loader = LoopSetLoader()
loader.load_from_adjacency_matrix("data.xlsx")

# Access the loop set
loop_set = loader.loop_set

# Get all loops
for loop in loop_set.loops:
    print(f"Loop {loop.get_id()}: {loop}")
    print(f"  Type: {loop.get_type()}")
    print(f"  Size: {loop.get_size()}")
    print(f"  Polarity: {loop.get_polarity()}")

# Get loops containing a specific concept
from cld_analysis.models import Concept
concept = Concept.get_concept("YourConceptName")
count = loop_set.loops_containing_concept(concept)
print(f"{concept.name} appears in {count} loops")
```

### Working with CSV Files

```python
# Load from CSV instead of Excel
loader.load_from_adjacency_matrix("data.csv")
```

## Performance Considerations

For large networks:

- Loop detection is O(n!) in worst case but optimized with pruning
- Distance calculation is cached to avoid recomputation
- Levenshtein distance calculation uses optimized dynamic programming
- Consider the number of loops: networks with thousands of loops may take significant time to score

## Troubleshooting

### Common Issues

1. **"Invalid polarity value"**
   - Check that all non-zero cells contain exactly +1 or -1

2. **"No loops found"**
   - Verify your network actually contains feedback loops
   - Check that influences form complete cycles

3. **Slow performance**
   - Large networks with many loops can take time
   - Consider using verbose=False to reduce output overhead

## Examples

See the `example.py` and `simple_example.py` files for complete working examples.

## License

This implementation is based on the methodology described in the SUReNet urban-rural systems research project.

## Citation

If you use this tool in your research, please cite:

```
Rozhkov, A., Murphy, J. T., & Pijanowski, B. C. (2025).
Identifying leverage points for sustainable transitions in urban-rural systems.
```

## Comparison with Java Implementation

This Python implementation provides the same core functionality as the original Java version:

- ✅ Loop detection algorithm (identical)
- ✅ Levenshtein distance with rotation (identical)
- ✅ Centrality scoring algorithm (identical)
- ✅ Adjacency matrix input (new feature)
- ✅ CSV export functionality
- ✅ More user-friendly API

The Python version adds:
- Direct support for Excel/CSV adjacency matrices
- Simplified API
- Better documentation
- Type hints for better IDE support
