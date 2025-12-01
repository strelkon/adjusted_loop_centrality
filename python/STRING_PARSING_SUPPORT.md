# String Polarity Value Parsing Support

## Overview

The adjacency matrix parser now supports parsing polarity values in various string formats, including values with spaces and different formatting styles commonly found in Excel spreadsheets.

## Supported Formats

The parser can now handle all of the following polarity value formats:

### Numeric Values
- `1` or `1.0` - Positive influence
- `-1` or `-1.0` - Negative influence
- `0` - No connection (skipped)

### NumPy Types
- `np.int64(1)` - NumPy integer types (from pandas/Excel)
- `np.float64(-1.0)` - NumPy floating point types

### String Values with Spaces
- `"+ 1"` - Plus sign with space
- `"- 1"` - Minus sign with space
- `" 1 "` - Number with surrounding spaces
- `" -1 "` - Negative with surrounding spaces

### String Values without Spaces
- `"+1"` - Plus sign without space
- `"-1"` - Minus sign without space
- `"1"` - Plain string number
- `" +1"` - Leading space with plus sign

## Example Excel Matrix

Your adjacency matrix can now contain values in any of these formats:

|          | ConceptA | ConceptB | ConceptC |
|----------|----------|----------|----------|
| ConceptA |    0     |  "+ 1"   |    1     |
| ConceptB |  "- 1"   |    0     |  " +1"   |
| ConceptC |   -1     |   " 1 "  |    0     |

All of these will be correctly parsed:
- `ConceptA -> ConceptB`: Positive influence (from "+ 1")
- `ConceptA -> ConceptC`: Positive influence (from 1)
- `ConceptB -> ConceptA`: Negative influence (from "- 1")
- `ConceptB -> ConceptC`: Positive influence (from " +1")
- `ConceptC -> ConceptA`: Negative influence (from -1)
- `ConceptC -> ConceptB`: Positive influence (from " 1 ")

## Implementation Details

### Parsing Logic

The `_parse_polarity()` function in `matrix_loader.py` handles the parsing:

1. **Check for NaN/None**: Skip empty cells
2. **Check numeric types**: Handle int, float, and NumPy integer/floating types
3. **Parse strings**: Remove all whitespace, handle plus signs, convert to int
4. **Validate**: Ensure the final value is exactly +1 or -1

### Error Handling

The parser handles errors gracefully:

- **Silent skip**: Zero values, NaN, empty cells (expected "no connection" cases)
- **Warning message**: Invalid values that can't be parsed (e.g., "abc", "2", "0.5")

## Testing

A comprehensive test suite is provided in `test_string_parsing.py`:

```bash
cd python
python test_string_parsing.py
```

This creates a test matrix with various string formats and verifies that all are parsed correctly.

## Benefits

This enhancement makes the tool more flexible and user-friendly:

1. **Excel Compatibility**: Works with Excel spreadsheets that have formatted cells
2. **Copy-Paste Friendly**: Handles data copied from various sources
3. **Human-Readable**: Allows using "+ 1" and "- 1" for better readability
4. **Robust**: Handles whitespace and formatting variations automatically

## Usage

No changes needed to your code! The enhanced parser is automatically used:

```python
from cld_analysis import LoopSetLoader

loader = LoopSetLoader()
loader.load_from_adjacency_matrix("your_file.xlsx")  # Works with any format!
```

## Backwards Compatibility

This enhancement is fully backwards compatible:

- ✅ Numeric values (1, -1) still work
- ✅ Existing Excel files work without modification
- ✅ All previous functionality preserved

## File Format Specification

The adjacency matrix should have:

- **First row (header)**: Target concept names (starting from column B)
- **First column (index)**: Source concept names (starting from row 2)
- **Cell values**: Any of the formats listed above

### What Gets Parsed

| Value | Interpretation |
|-------|----------------|
| 1, "1", "+1", "+ 1", " 1 " | Positive influence (+1) |
| -1, "-1", "- 1", " -1 " | Negative influence (-1) |
| 0, "0", "", NaN | No connection (skipped) |

### What Gets Rejected

| Value | Result |
|-------|--------|
| "2", "3", etc. | Warning + skipped (not ±1) |
| "abc", "yes", etc. | Warning + skipped (not a number) |
| "0.5", "1.5", etc. | Warning + skipped (not integer ±1) |

## Technical Notes

### Why NumPy Support?

When pandas reads Excel files, it often converts integer cells to NumPy types (`np.int64`). The parser now recognizes these types and handles them correctly.

### Whitespace Handling

All whitespace is removed before parsing:
- `" + 1 "` → `"+1"` → `1`
- `" - 1"` → `"-1"` → `-1`

### Plus Sign Handling

Leading plus signs are stripped:
- `"+1"` → `"1"` → `1`
- `"+ 1"` → `"+1"` → `"1"` → `1`

## Future Enhancements

Potential future additions:
- Support for "positive"/"negative" text values
- Support for "yes"/"no" with positive/negative mapping
- Support for other polarity indicators
- Custom parsing rules via configuration

## Questions?

See the main [README.md](README.md) for general usage information or [GETTING_STARTED.md](GETTING_STARTED.md) for quick start instructions.
