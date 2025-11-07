# prismWriter

Python library and GUI for programmatically creating and manipulating GraphPad Prism (`.pzfx`) files. Convert pandas DataFrames into Prism's XML-based table format with complex grouping structures.

## Features

- Convert pandas DataFrames to GraphPad Prism format
- Flexible grouping: main groups, sub-columns, row labels
- Multiple interfaces: Python API, Qt GUI, and Web interface
- Load and modify existing `.pzfx` files
- Validate table structure with preview functionality

## Installation

```bash
pip install -e .
```

## Quick Start

### Python API

```python
from prismWriter.prism_writer import PrismFile
import pandas as pd

# Create a PrismFile
pf = PrismFile()**

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

Or use the provided launch scripts:
- **Windows (CMD)**: `run_web.bat`

Features:
- Upload CSV/Excel files
- Live data preview
- Interactive configuration
- Preview table structure
- Direct download

### Qt GUI

```bash
python prismWriter/gui.py
```

Or after installation:
```bash
prismwriter-gui
```

## Usage

### Grouping Parameters

- **`groupby`**: Main column grouping - creates separate Y-columns for each category
- **`subgroupby`/`subgroupcols`**: Sub-columns within each Y-column (replicates)
- **`rowgroupby`/`rowgroupcols`**: Row labels on the vertical axis
- **`cols`**: Data columns to include

**Note**: Use either column name (`subgroupby='condition'`) OR list of data columns (`subgroupcols=['col1', 'col2']`) - not both.

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
from prismWriter.prism_writer import load_prism_file

# Load existing Prism file
pf = load_prism_file("existing.pzfx")

# Get table names
tables = pf.get_table_names()
print(f"Found tables: {tables}")

# Convert to DataFrame
df = pf.to_dataframe("TableName")

# Add new table
pf.make_group_table(...)

# Save
pf.save("modified.pzfx")
```

## Dependencies

- **Core**: pandas, numpy, xml.etree.ElementTree
- **GUI**: PySide2 (Qt bindings)
- **Web**: streamlit
- **Files**: openpyxl for Excel support

## Project Structure

```
prismWriter/
├── prismWriter/
│   ├── prism_writer.py      # Core XML generation engine
│   ├── gui.py               # Qt GUI wrapper
│   ├── streamlit_app.py     # Streamlit web interface
│   ├── prism_template2.pzfx # XML structure template
│   └── schema/              # Prism XML schemas
├── tests/
│   ├── test_prism_writer.py
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
- Namespace: `{http://graphpad.com/prism/Prism.htm}`
- "Raveling" strategy: transforms DataFrames into flat structure, then rebuilds into nested XML
- Automatic backup files created when loading existing files

## Known Limitations

- No validation for duplicate table names
- Row mismatch warnings can occur with sparse data
- Template system hardcoded to specific Prism XML schema version
- No undo functionality - backup files are the safety net

## License

MIT License

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.
