# prismWriter - AI Coding Agent Instructions

## Project Purpose
Python library and GUI for programmatically creating and manipulating GraphPad Prism (`.pzfx`) files. Converts pandas DataFrames into Prism's XML-based table format with complex grouping structures (main groups, sub-columns, row labels).

## Architecture Overview

### Core Components
- **`prism_writer.py`**: Core XML generation engine and PrismFile class
- **`prism_writer_gui.py`**: PySide6-based GUI wrapper with live preview
- **Template System**: Uses `prism_template2.pzfx` as XML structure blueprint

### Key Data Flow
1. User loads CSV/Excel into pandas DataFrame
2. GUI collects grouping parameters (main group, sub-groups, row groups, data columns)
3. `PrismFile.make_group_table()` "ravels" DataFrame into flat structure with metadata
4. Data is re-organized into nested XML structure: YColumn → Subcolumn → data points
5. XML written to `.pzfx` file (Prism's format)

## Critical Implementation Patterns

### XML Namespace Handling
All Prism XML uses namespace `{http://graphpad.com/prism/Prism.htm}`. **Always** include namespace in `ET.find/findall` calls:
```python
# Correct
tables = tree.findall('{http://graphpad.com/prism/Prism.htm}Table', ns)
# Wrong - will silently return empty
tables = tree.findall('Table')
```

### The "Raveling" Strategy
`make_group_table()` transforms DataFrames using a 2-phase approach:
1. **Ravel**: Explode DataFrame into one row per data point with grouping metadata
2. **Nest**: Rebuild into Prism's hierarchy (YColumn → Subcolumn → data point)

This pattern handles arbitrary grouping combinations. See lines 132-178 in `prism_writer.py`.

### Template String Interpolation
XML fragments in `group_str_template` dict use UPPERCASE placeholders:
```python
"ycolumn_title": "<Title>COLUMN_TITLE</Title>"
```
Replace with `.replace('COLUMN_TITLE', actual_value)` before `ET.fromstring()`.

### GUI State Management
- Main group: **Single** selection (QComboBox)
- Sub/row/data groups: **Multi** selection (custom `MultiSelectPopup` buttons)
- Column names displayed with `[NUM]`/`[CAT]` prefixes - strip before use:
  ```python
  clean_name = display_text.split(' ', 1)[-1]
  ```

## Dependencies
- **Core**: pandas, numpy, xml.etree.ElementTree
- **GUI**: PySide6 (Qt bindings)
- **Files**: openpyxl/xlrd for Excel support (pandas backends)

Run GUI: `python prism_writer_gui.py` (entry point at bottom of file)

## Common Operations

### Creating Tables
Three grouping parameters control layout:
- `groupby`: Main column grouping (creates separate Y-columns)
- `subgroupby`/`subgroupcols`: Sub-columns within each Y-column (replicates)
- `rowgroupby`/`rowgroupcols`: Row labels (vertical axis)

Either pass label column name (`subgroupby='condition'`) OR list of data column names (`subgroupcols=['col1', 'col2']`) - NOT both.

### Preview System
GUI generates preview by:
1. Sampling 50% of DataFrame (for performance)
2. Creating temporary table with `__` prefix
3. Round-tripping through `to_dataframe()` to validate
4. Deleting temporary table (line 654-666)

## File Structure Quirks
- Package structure: `prismWriter/prismWriter/` (nested folder)
- Template files (`.pzfx`) live alongside Python code
- No setup.py/requirements.txt present - dependencies implicit in imports
- Backup files created as `{filename}.backup{timestamp}` on every load

## Testing Strategy
Run GUI and check:
1. Load sample CSV with numeric + categorical columns
2. Select categorical for main group, numeric for data
3. Verify preview table dimensions match expectations
4. Save and open in Prism to validate XML structure

## Known Limitations
- No validation for duplicate table names
- Row mismatch warnings (line 412) can occur with sparse data
- Template system hardcoded to specific Prism XML schema version
- No undo functionality - backup files are only safety net
