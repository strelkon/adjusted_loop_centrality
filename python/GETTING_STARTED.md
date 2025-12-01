# Getting Started with CLD Analysis Tool

## Quick Start Guide

### 1. Installation

First, install the required dependencies:

```bash
cd python
pip install -r requirements.txt
```

### 2. Run a Test Example

Test the installation with the simple example:

```bash
python simple_example.py
```

This will:
- Create a small test network
- Detect all feedback loops
- Calculate centrality scores
- Export results to CSV files

### 3. Analyze Your Own Data

#### Option A: Using the Command Line Tool

The easiest way to analyze your adjacency matrix:

```bash
python analyze_matrix.py your_file.xlsx
```

This will create 4 output files:
- `output_concept_nodes.csv` - Concept scores
- `output_concept_links.csv` - Link information
- `output_loop_nodes.csv` - Loop information
- `output_scores.txt` - Ranked scores

**Additional options:**

```bash
# Specify output file prefix
python analyze_matrix.py data.xlsx --output my_results

# Use a specific sheet in Excel
python analyze_matrix.py data.xlsx --sheet "Diagram Sheet"

# Run in quiet mode (less output)
python analyze_matrix.py data.xlsx --quiet
```

#### Option B: Using Python Code

For more control, use the Python API:

```python
from cld_analysis import LoopSetLoader

# Create loader
loader = LoopSetLoader()

# Load your data
loader.load_from_adjacency_matrix("your_file.xlsx")

# Calculate scores
loader.get_scores()

# Show summary
loader.summary()

# Export results
loader.write_concept_node_file("concept_scores.csv")
```

### 4. Prepare Your Data

Your adjacency matrix should be in Excel (.xlsx) or CSV format:

#### Format Requirements:

```
|          | Concept1 | Concept2 | Concept3 |
|----------|----------|----------|----------|
| Concept1 |    0     |    1     |    0     |
| Concept2 |   -1     |    0     |    1     |
| Concept3 |    1     |   -1     |    0     |
```

- **Row headers**: Source concepts
- **Column headers**: Target concepts
- **Cell values**:
  - `1` or `+1` = Positive influence (source INCREASES target)
  - `-1` = Negative influence (source DECREASES target)
  - `0` or empty = No influence

#### Create a Sample File:

Run this to create a sample adjacency matrix:

```bash
python create_sample_matrix.py
```

This creates `sample_adjacency_matrix.xlsx` that you can use as a template.

## Understanding the Results

### Concept Scores

Higher scores indicate more central "leverage points" in the system:

- Concepts appearing in many loops get higher scores
- Concepts appearing in diverse (dissimilar) loops get higher scores
- These are the most influential intervention points

### Loop Types

- **Reinforcing Loop**: Amplifies changes (even number of negative links)
- **Balancing Loop**: Dampens changes (odd number of negative links)

### Output Files Explained

1. **concept_nodes.csv**
   - `id`: Concept name
   - `numberOfLoops`: How many loops contain this concept
   - `relevanceScore`: Centrality score (higher = more central)

2. **concept_links.csv**
   - `source`, `target`: The link endpoints
   - `linkInfluence`: INCREASES or DECREASES
   - `loopsTraversing`: Number of loops using this link

3. **loop_nodes.csv**
   - `id`: Loop identifier
   - `size`: Number of links in the loop

4. **scores.txt**
   - Simple ranked list of concepts with scores

## Examples

### Example 1: Basic Analysis

```bash
python analyze_matrix.py data.xlsx
```

### Example 2: Multiple Sheets

If your Excel file has multiple sheets:

```bash
python analyze_matrix.py data.xlsx --sheet "Main System"
```

### Example 3: Programmatic Analysis

```python
from cld_analysis import LoopSetLoader

loader = LoopSetLoader()
loader.load_from_adjacency_matrix("data.xlsx", verbose=True)
loader.get_scores(verbose=True)

# Get top 5 leverage points
top_concepts = loader.get_top_concepts(5)
for i, (concept, score) in enumerate(top_concepts, 1):
    print(f"{i}. {concept.name}: {score:.2f}")

# Export results
loader.write_concept_node_file("results.csv")
loader.summary()
```

### Example 4: CSV Input

Works the same as Excel:

```bash
python analyze_matrix.py data.csv --output csv_results
```

## Common Issues

### Problem: "Invalid polarity value"

**Solution**: Check that all non-zero cells contain exactly `1` or `-1`.

### Problem: "No loops found"

**Solution**:
- Verify your network has actual feedback loops (cycles)
- Check that influences form complete paths back to starting concepts

### Problem: Slow performance

**Solution**:
- Use `--quiet` flag to reduce output overhead
- Consider that large networks naturally take longer
- Networks with 1000+ loops may take several minutes

## Next Steps

1. Read the full [README.md](README.md) for detailed documentation
2. Explore the [example.py](example.py) for code examples
3. Look at [simple_example.py](simple_example.py) for a complete workflow
4. Check the original Java implementation in `../Java/` for comparison

## Getting Help

If you encounter issues:

1. Check that your input file format is correct
2. Try running `simple_example.py` to verify installation
3. Use `--help` with the CLI tool for options:
   ```bash
   python analyze_matrix.py --help
   ```

## Credits

This tool implements the methodology from:

> Rozhkov, A., Murphy, J. T., & Pijanowski, B. C. (2025).
> Identifying leverage points for sustainable transitions in urban-rural systems.

Python implementation by Claude Code, based on the original Java codebase.
