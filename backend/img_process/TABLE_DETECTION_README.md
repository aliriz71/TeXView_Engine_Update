# Enhanced Table Detection and Formatting

This enhanced version of the PDF processing system now includes sophisticated table detection and formatting capabilities.

## New Features

### 1. Table Structure Detection
- **Line Detection**: Uses morphological operations to detect horizontal and vertical lines that form table borders
- **Grid Analysis**: Identifies table cells by analyzing the intersection of detected lines
- **Region Classification**: Automatically distinguishes between regular text regions and table regions

### 2. Enhanced OCR Processing
- **Table-Optimized OCR**: Uses specialized Tesseract configurations for better table text extraction
- **Cell-by-Cell Processing**: Processes each table cell individually for improved accuracy
- **Text Cleanup**: Automatically cleans up extracted text by removing extra whitespace and newlines

### 3. Multiple Output Formats
- **Plain Text**: Traditional text extraction with table indicators
- **Markdown Tables**: Properly formatted markdown tables with headers and separators
- **Aligned Text Tables**: Human-readable text tables with consistent column alignment

### 4. Intelligent Content Detection
- **Heuristic Analysis**: Uses pattern recognition to identify potential tables that weren't structurally detected
- **Fallback Processing**: Provides graceful degradation when table structure detection fails

## File Changes

### markDownROI.py
- Added `detect_table_structure()`: Detects table grids using line detection
- Added `extract_table_cells()`: Extracts individual cells from detected tables
- Added `mark_region_with_tables()`: Enhanced region detection that includes tables

### pdfMaster.py
- Added `format_table_as_markdown()`: Converts table data to markdown format
- Added `format_table_as_text()`: Converts table data to aligned text format
- Added `process_table_ocr()`: Specialized OCR processing for table cells
- Added `is_likely_table()`: Heuristic detection of tabular content
- Enhanced `pdf_conversion()`: Now outputs both plain text and formatted markdown files

### test_table_detection.py (New)
- Standalone test script for validating table detection on individual images
- Useful for debugging and fine-tuning table detection parameters

## Usage

### Basic Usage (Same as before)
```bash
python pdfMaster.py path/to/your.pdf
```

### Output Files
The system now generates two output files:
1. `{filename}.txt` - Traditional plain text extraction
2. `{filename}_formatted.md` - Markdown formatted output with properly structured tables

### Testing Table Detection
```bash
python test_table_detection.py debug_images/pdfConverted_001.jpg
```

## Example Output

### Markdown Table Format
```markdown
### Table 1

| Title | 1.1 | 1.2 | 1.3 |
| --- | --- | --- | --- |
| 2.1 | 2.2 | 2.3 |
| 3.1 | 3.2 | 3.3 |
| 4.1 | 4.2 | 4.3 |
```

### Aligned Text Format
```
Title | 1.1 | 1.2 | 1.3
----- | --- | --- | ---
2.1   | 2.2 | 2.3 |    
3.1   | 3.2 | 3.3 |    
4.1   | 4.2 | 4.3 |    
```

## Configuration

### Table Detection Parameters
- `min_line_length`: Minimum line length for table border detection (default: 50)
- `min_area`: Minimum area for table region detection (default: 10,000)

### OCR Parameters
- Uses PSM 6 (uniform text block) for table cells
- Applies binary thresholding for cleaner text recognition
- Includes text cleanup for better formatting

## Visual Annotations

The system now uses different colors for different region types:
- **Purple/Magenta**: Regular text regions
- **Green**: Detected table regions

## Troubleshooting

### If tables aren't detected:
1. Check the `min_area` parameter - very small tables might be filtered out
2. Verify that table borders are clearly visible in the PDF
3. Use the test script to debug table detection on individual images

### If table formatting is incorrect:
1. The system includes fallback processing for malformed tables
2. Check the OCR confidence by examining the plain text output
3. Consider adjusting the binary threshold value for better text recognition

## Future Enhancements

Potential improvements could include:
- Machine learning-based table detection
- Support for borderless tables
- Advanced cell merging detection
- Custom table formatting templates
