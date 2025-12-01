# LogPress API Reference

Complete reference for the LogPress Python library.

## Installation

```bash
pip install LogPress
```

## Quick Start

```python
from logpress import LogPress

lp = LogPress()
stats = lp.compress_file("app.log", "app.lsc")
errors = lp.query("app.lsc", severity="ERROR")
```

---

## High-Level API

### LogPress Class

The main interface for most users. Provides simple methods for common operations.

```python
from logpress import LogPress

lp = LogPress(min_support=3)
```

#### Constructor

```python
LogPress(min_support: int = 3)
```

**Parameters:**
- `min_support` (int, optional): Minimum number of logs required to create a template. Default: 3. Lower values detect more templates but may overfit.

---

#### compress_file()

Compress a log file to disk.

```python
stats = lp.compress_file(
    input_path: Union[str, Path],
    output_path: Union[str, Path],
    show_progress: bool = False
) -> Dict[str, Union[int, float]]
```

**Parameters:**
- `input_path`: Path to input log file
- `output_path`: Path to output compressed file (.lsc extension recommended)
- `show_progress`: Show progress bar (requires tqdm)

**Returns:** Dictionary with statistics:
- `compression_ratio` (float): Achieved compression ratio (e.g., 12.5)
- `original_size` (int): Original file size in bytes
- `compressed_size` (int): Compressed file size in bytes
- `space_saved_mb` (float): Space saved in megabytes
- `template_count` (int): Number of templates extracted

**Example:**
```python
stats = lp.compress_file("app.log", "app.lsc")
print(f"Compression: {stats['compression_ratio']:.1f}×")
print(f"Saved: {stats['space_saved_mb']:.1f} MB")
```

---

#### compress_lines()

Compress a list of log strings to memory.

```python
compressed, stats = lp.compress_lines(
    logs: List[str]
) -> Tuple[CompressedLog, Dict]
```

**Parameters:**
- `logs`: List of log strings

**Returns:** Tuple of:
1. `CompressedLog` object (can be saved with `.save()`)
2. Statistics dictionary (same format as `compress_file`)

**Example:**
```python
logs = ["[INFO] App started", "[ERROR] Database failed", ...]
compressed, stats = lp.compress_lines(logs)

# Save to file
compressed.save("output.lsc")
```

---

#### compress_to_bytes()

Compress logs directly to bytes (for network/database storage).

```python
data = lp.compress_to_bytes(
    logs: List[str]
) -> bytes
```

**Parameters:**
- `logs`: List of log strings

**Returns:** Compressed data as bytes

**Example:**
```python
logs = ["[INFO] Message 1", "[WARN] Message 2"]
data = lp.compress_to_bytes(logs)

# Store in database, send over network, etc.
db.store("log_archive", data)
```

---

#### query()

Query compressed logs with filters.

```python
results = lp.query(
    compressed_path: Union[str, Path],
    severity: Optional[Union[str, List[str]]] = None,
    timestamp_after: Optional[str] = None,
    timestamp_before: Optional[str] = None,
    limit: int = 1000,
    **filters
) -> List[Dict[str, Any]]
```

**Parameters:**
- `compressed_path`: Path to compressed .lsc file
- `severity`: Filter by severity level(s). String or list of strings (e.g., "ERROR" or ["ERROR", "WARN"])
- `timestamp_after`: Filter logs after this timestamp (string format: "YYYY-MM-DD HH:MM:SS")
- `timestamp_before`: Filter logs before this timestamp
- `limit`: Maximum number of results to return (default: 1000)
- `**filters`: Additional field filters (experimental)

**Returns:** List of dictionaries, each containing:
- `timestamp` (str): Log timestamp
- `severity` (str): Severity level
- `message` (str): Log message
- `raw` (str): Original log line
- Additional fields based on log structure

**Example:**
```python
# Get all errors
errors = lp.query("app.lsc", severity="ERROR")

# Get errors or warnings
critical = lp.query("app.lsc", severity=["ERROR", "WARN"])

# Get logs from specific time range
recent = lp.query("app.lsc", 
                  timestamp_after="2024-12-01 10:00:00",
                  timestamp_before="2024-12-01 11:00:00",
                  limit=500)

# Limit results
top_errors = lp.query("app.lsc", severity="ERROR", limit=10)
```

---

#### count()

Count total logs in compressed file (metadata-only, very fast).

```python
total = lp.count(
    compressed_path: Union[str, Path]
) -> int
```

**Parameters:**
- `compressed_path`: Path to compressed .lsc file

**Returns:** Total number of logs (integer)

**Example:**
```python
total = lp.count("app.lsc")
print(f"Total logs: {total:,}")
```

**Note:** This reads only metadata, not the actual log data, making it extremely fast even for large files.

---

#### extract_schemas()

Extract log templates without compression (schema discovery only).

```python
templates = lp.extract_schemas(
    logs: List[str]
) -> List[Dict[str, Any]]
```

**Parameters:**
- `logs`: List of log strings

**Returns:** List of template dictionaries:
- `template_id` (str): Unique template identifier
- `pattern` (List[str]): Template pattern with variable fields marked
- `count` (int): Number of logs matching this template
- `fields` (List[Dict]): Detected fields with types
- `confidence` (float): Extraction confidence score (0.0-1.0)

**Example:**
```python
logs = [
    "[INFO] User alice logged in",
    "[INFO] User bob logged in",
    "[ERROR] Database timeout"
]

templates = lp.extract_schemas(logs)

for template in templates:
    print(f"Pattern: {' '.join(template['pattern'])}")
    print(f"Matches: {template['count']} logs")
    print(f"Fields: {[f['name'] for f in template['fields']]}")
```

---

## Convenience Functions

Quick one-liner functions for simple scripts.

### compress()

```python
from logpress import compress

stats = compress(
    input_path: Union[str, Path],
    output_path: Union[str, Path],
    min_support: int = 3
) -> Dict
```

Equivalent to:
```python
lp = LogPress(min_support=min_support)
stats = lp.compress_file(input_path, output_path)
```

**Example:**
```python
from logpress import compress

stats = compress("app.log", "app.lsc")
print(f"{stats['compression_ratio']:.1f}× compression")
```

---

### query()

```python
from logpress import query

results = query(
    compressed_path: Union[str, Path],
    **filters
) -> List[Dict]
```

Equivalent to:
```python
lp = LogPress()
results = lp.query(compressed_path, **filters)
```

**Example:**
```python
from logpress import query

errors = query("app.lsc", severity="ERROR", limit=50)
for log in errors:
    print(log['message'])
```

---

## Low-Level Components

For advanced users who need fine-grained control.

### Compressor

Direct access to the compression pipeline.

```python
from logpress.services import Compressor

compressor = Compressor(
    min_support=3,
    enable_delta=True,
    enable_dictionary=True,
    enable_varint=True,
    enable_rle=True,
    enable_token_pool=True,
    enable_zstd=True
)

compressed = compressor.compress(logs)
stats = compressor.get_stats()
compressor.save("output.lsc")
```

---

### QueryEngine

Direct access to the query system.

```python
from logpress.services import QueryEngine

engine = QueryEngine("compressed.lsc")

# Filter logs
errors = engine.filter(severity="ERROR", limit=100)

# Count logs
total = engine.count()

# Get metadata
metadata = engine.get_metadata()
```

---

### TemplateGenerator

Direct access to template extraction.

```python
from logpress.context.extraction import TemplateGenerator

generator = TemplateGenerator(min_support=3)
templates = generator.extract_templates(logs)

for template in templates:
    print(template.pattern)
    print(f"  Matches: {template.log_count}")
```

---

## Data Models

### CompressedLog

Represents compressed log data.

```python
from logpress.models import CompressedLog

# Create from compression
compressed = CompressedLog(...)

# Save to file
compressed.save("output.lsc")

# Load from file
compressed = CompressedLog.load("output.lsc")
```

**Attributes:**
- `templates`: List of extracted templates
- `compressed_data`: Compressed log data
- `metadata`: File metadata (count, size, timestamps)

---

### LogTemplate

Represents an extracted log template.

```python
from logpress.models import LogTemplate

template = LogTemplate(
    template_id="template_001",
    pattern=["[", "TIMESTAMP", "]", "SEVERITY", "MESSAGE"],
    fields=[...],
    log_count=150,
    sample_logs=[...]
)
```

**Attributes:**
- `template_id` (str): Unique identifier
- `pattern` (List[str]): Template pattern
- `fields` (List[TemplateField]): Detected fields
- `log_count` (int): Number of matching logs
- `sample_logs` (List[str]): Example logs
- `confidence` (float): Extraction confidence

---

### TemplateField

Represents a field within a template.

```python
from logpress.models import TemplateField

field = TemplateField(
    name="timestamp",
    field_type="TIMESTAMP",
    position=0,
    is_variable=True,
    pattern=r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
)
```

---

## Error Handling

All LogPress functions raise standard Python exceptions:

```python
from logpress import LogPress

lp = LogPress()

try:
    stats = lp.compress_file("app.log", "app.lsc")
except FileNotFoundError:
    print("Input file not found")
except PermissionError:
    print("Permission denied")
except Exception as e:
    print(f"Compression failed: {e}")
```

---

## Performance Considerations

### Memory Usage

- **compress_file()**: Streams data, uses ~2-4 KB per log
- **compress_lines()**: Loads all logs into memory
- **query()**: Decompresses only matching logs (selective decompression)
- **count()**: Reads only metadata (~1-10 KB)

### Throughput

Typical performance on a modern laptop:
- Compression: ~0.5-1.0 MB/s
- Query: ~2-5 MB/s (6× faster than full decompression)
- Count: <10ms (metadata-only)

### Parallelization

Use `concurrent.futures` for batch processing:

```python
from concurrent.futures import ProcessPoolExecutor
from logpress import compress

files = ["app1.log", "app2.log", "app3.log"]

with ProcessPoolExecutor(max_workers=4) as executor:
    results = executor.map(
        lambda f: compress(f, f.replace('.log', '.lsc')),
        files
    )
```

---

## Configuration

### Environment Variables

LogPress respects these environment variables:

- `LOGPRESS_MIN_SUPPORT`: Default min_support value (default: 3)
- `LOGPRESS_CACHE_DIR`: Directory for temporary files (default: system temp)

**Example:**
```bash
export LOGPRESS_MIN_SUPPORT=5
python your_script.py
```

---

## Best Practices

### 1. Choosing min_support

- **Small logs (<1K lines)**: Use `min_support=2`
- **Medium logs (1K-100K lines)**: Use `min_support=3-5`
- **Large logs (>100K lines)**: Use `min_support=10-20`

### 2. File Organization

```python
# Good: Separate compressed files by date/source
compressed/2024-12-01/app.lsc
compressed/2024-12-01/db.lsc
compressed/2024-12-02/app.lsc
```

### 3. Query Performance

```python
# Fast: Use specific filters
errors = lp.query("app.lsc", severity="ERROR", limit=100)

# Slow: No filters with large result set
all_logs = lp.query("app.lsc", limit=1000000)
```

### 4. Error Handling

Always wrap compression/query operations:

```python
try:
    stats = lp.compress_file("app.log", "app.lsc")
except Exception as e:
    logger.error(f"Compression failed: {e}")
    # Handle error (retry, alert, etc.)
```

---

## Examples

See the [`examples/`](../examples/) directory for complete working examples:

1. [Basic Compression](../examples/01_basic_compression.py)
2. [Query Compressed Logs](../examples/02_query_compressed_logs.py)
3. [Stream Large Files](../examples/03_streaming_large_files.py)
4. [Custom Semantic Types](../examples/04_custom_semantic_types.py)
5. [Schema Extraction Only](../examples/05_schema_extraction_only.py)
6. [Batch Processing](../examples/06_batch_processing.py)
7. [Flask API](../examples/07_flask_api.py)
8. [FastAPI Service](../examples/08_fastapi_service.py)
9. [Log Rotation Handler](../examples/09_log_rotation_handler.py)

---

## Further Reading

- [Quick Start Guide](quickstart.md) - 5-minute tutorial
- [Integration Guide](integration_guide.md) - Production deployments
- [Main README](../README.md) - Project overview
- [GitHub Issues](https://github.com/adam-bouafia/LogPress/issues) - Bug reports and feature requests
