# prismWriter

Python library and GUI for programmatically creating and manipulating GraphPad Prism (`.pzfx`) files. Convert pandas DataFrames into Prism's XML-based table format with complex grouping structures.

**Version:** 1.0.0

## Features

- Convert pandas DataFrames to GraphPad Prism format
- Flexible grouping: main groups, sub-columns, row labels
- Multiple interfaces: Python API, Qt GUI, and Streamlit Web interface
- Load and modify existing `.pzfx` files
- Validate table structure with preview functionality
- Automatic backup creation when loading existing files

## Installation

```bash
pip install -e .
```

### Requirements

- Python >= 3.7
- numpy
- pandas
- openpyxl (for Excel file support)
- PySide2 (for Qt GUI) [optional]
- streamlit >= 1.28.0 (for web interface) [optional]


### See Also:

- https://github.com/Yue-Jiang/pypzfx - Another python package with similar functionality
- https://github.com/Biomiha/prism2R - R package for reading .prism (newer) files
- https://github.com/yue-jiang/pzfx - R package for reading .pzfx files

## Quick Start

### Python API

```python
from prismWriter.prism_writer import PrismFile
import pandas as pd

# Create a new PrismFile
pf = PrismFile()

# Load your data
df = pd.read_csv('data.csv')

# Create a grouped table
pf.make_group_table(
    group_name="MyTable",
    group_values=df,
    groupby="condition",  # Main grouping column
    cols=["value1", "value2"],  # Data columns
    subgroupby="replicate"  # Sub-grouping
)

# Save to Prism file
pf.save("output.pzfx")
```

### Web Interface (Streamlit)

The easiest way to use prismWriter:

```bash
streamlit run prismWriter/streamlit_app.py
```

Or use the provided launch script:
- **Windows**: `run_web.bat`

Or after installation:
```bash
prismwriter-web
```

Features:
- Upload CSV/Excel files (with multi-sheet Excel support)
- Live data preview with automatic column type detection
- Interactive grouping configuration
- Preview table structure before generating
- Direct download of generated `.pzfx` files
- Load and view existing Prism files

### Qt GUI

```bash
python prismWriter/gui.py
```

Or after installation:
```bash
prismwriter-gui
```

## API Reference

### PrismFile Class

```python
pf = PrismFile(file=None)  # Create new or load existing file
```

**Methods:**
- `load(file_path, backup=True)` - Load an existing Prism file
- `smake_group_table(group_name, group_values, groupby=None, cols=None, subgroupby=None, rowgroupby=None, append=True)` - Create a grouped table
- `get_table_names()` - Get list of all table names
- `to_dataframe(table_name)` - Convert a table to pandas DataFrame
- `save(file_path)` - Save to file
- `write(file_path, xml_declaration=True, encoding='utf-8', pretty_print=True)` - Write with options
- `remove_table(table_name)` - Remove a table from the file

### Grouping Parameters

- **`groupby`**: Main column grouping - creates separate Y-columns for each category
- **`subgroupby`**: Sub-columns within each Y-column (string for column name, or list for data columns)
- **`rowgroupby`**: Row labels on the vertical axis (string for column name, or list for data columns)
- **`cols`**: Data columns to include

**Note**: Use either column name (`subgroupby='condition'`) OR list of data columns (`subgroupby=['col1', 'col2']`) - not both.

### Example Data Structure

```python
import pandas as pd
from prismWriter.prism_writer import PrismFile

# Sample data
data = {
    'treatment': ['Control', 'Control', 'Drug A', 'Drug A'],
    'time': [0, 24, 0, 24],
    'replicate': [1, 1, 1, 1],
    'value': [10.5, 15.2, 12.1, 25.8]
}
df = pd.DataFrame(data)

# Create Prism file
pf = PrismFile()
pf.make_group_table(
    group_name="Treatment_Data",
    group_values=df,
    groupby="treatment",    # Separate columns for Control vs Drug A
    rowgroupby="time",      # Rows labeled by timepoint
    cols=["value"]          # Data column
)
pf.save("treatment_data.pzfx")
```

## Loading Existing Files

```python
from prismWriter.prism_writer import PrismFile

# Load existing Prism file (creates automatic backup)
pf = PrismFile()
pf.load("existing.pzfx")

# Or load directly in constructor
pf = PrismFile(file="existing.pzfx")

# Get table names
tables = pf.get_table_names()
print(f"Found tables: {tables}")

# Convert table to DataFrame
df = pf.to_dataframe("TableName")

# Add new table
pf.make_group_table(
    group_name="NewTable",
    group_values=df,
    groupby="category",
    cols=["value"]
)

# Save (use write() for more options)
pf.save("modified.pzfx")
```

## Dependencies

- **Core**: pandas, numpy
- **GUI**: PySide2 (Qt bindings)
- **Web**: streamlit >= 1.28.0
- **Files**: openpyxl for Excel support

## Project Structure

```
prismWriter/
├── prismWriter/
│   ├── __init__.py          # Package exports
│   ├── prism_writer.py      # Core XML generation engine
│   ├── gui.py               # PySide2 Qt GUI wrapper
│   ├── streamlit_app.py     # Streamlit web interface
│   ├── prism_template2.pzfx # XML structure template
│   └── schema/              # Prism XML schemas
├── tests/
│   ├── test_prism_writer.py
│   ├── test_gui.py
│   └── test_data.csv
├── pyproject.toml
└── README.md
```

## Development

### Running Tests

```bash
pytest tests/
```

### Key Implementation Details

- Uses `prism_template2.pzfx` as XML structure blueprint
- XML Namespace: `{http://graphpad.com/prism/Prism.htm}`
- "Raveling" strategy: transforms DataFrames into flat structure via `melt()`, then rebuilds into nested XML hierarchy
- Automatic backup files created as `{filename}.backup{timestamp}` when loading existing files
- Logging enabled at INFO level for debugging table creation

## Known Limitations

- No validation for duplicate table names
- Row mismatch warnings can occur with sparse data
- Template system hardcoded to specific Prism XML schema version
- No undo functionality - backup files are the safety net

## License

MIT License

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.
