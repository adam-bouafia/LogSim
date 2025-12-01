# LogPress Quick Start Guide

Get started with LogPress in under 5 minutes.

## Installation

```bash
pip install LogPress
```

## Your First Compression

```python
from logpress import LogPress

# Create LogPress instance
lp = LogPress()

# Compress a log file
stats = lp.compress_file("application.log", "compressed.lsc")

# Check results
print(f"Original:   {stats['original_size'] / 1024:.1f} KB")
print(f"Compressed: {stats['compressed_size'] / 1024:.1f} KB")
print(f"Ratio:      {stats['compression_ratio']:.1f}×")
print(f"Saved:      {stats['space_saved_mb']:.1f} MB")
```

## Query Compressed Logs

```python
# Find all ERROR logs
errors = lp.query("compressed.lsc", severity="ERROR", limit=100)

for log in errors:
    print(f"[{log['timestamp']}] {log['message']}")
```

## Common Use Cases

### 1. Compress Multiple Files

```python
import glob
from logpress import LogPress

lp = LogPress()

for log_file in glob.glob("logs/*.log"):
    output = log_file.replace(".log", ".lsc")
    stats = lp.compress_file(log_file, output)
    print(f"{log_file}: {stats['compression_ratio']:.1f}×")
```

### 2. Time Range Queries

```python
# Get logs from specific time window
recent = lp.query(
    "compressed.lsc",
    timestamp_after="2024-12-01 10:00:00",
    timestamp_before="2024-12-01 11:00:00",
    limit=1000
)
```

### 3. Filter by Multiple Criteria

```python
# Find WARNING or ERROR logs
critical = lp.query(
    "compressed.lsc",
    severity=["WARNING", "ERROR"],
    limit=500
)
```

### 4. Count Logs (Fast!)

```python
# Count without decompressing (metadata-only)
total = lp.count("compressed.lsc")
print(f"Total logs: {total:,}")
```

## Working with Log Lines

```python
# Compress logs from a list
logs = [
    "[2024-12-01 10:00:00] INFO Application started",
    "[2024-12-01 10:00:01] ERROR Database connection failed",
    "[2024-12-01 10:00:02] INFO Request processed",
]

compressed, stats = lp.compress_lines(logs)
print(f"Compressed {len(logs)} logs to {stats['compressed_size']} bytes")
```

## Examples Gallery

LogPress includes 9 comprehensive examples covering different use cases:

### Basic Examples (Work Immediately)
```bash
# Example 01: Basic compression (5 lines of code)
python examples/01_basic_compression.py

# Example 02: Query compressed logs
python examples/02_query_compressed_logs.py

# Example 03: Stream large files (50K+ logs)
python examples/03_streaming_large_files.py /path/to/large.log output.lsc

# Example 04: Custom semantic type patterns
python examples/04_custom_semantic_types.py

# Example 05: Schema extraction without compression
python examples/05_schema_extraction_only.py

# Example 06: Batch process multiple files
python examples/06_batch_processing.py
```

### Integration Examples (Require Optional Deps)
```bash
# Example 07: Flask REST API (install: pip install LogPress[web])
python examples/07_flask_api.py
# Access at http://localhost:5000

# Example 08: FastAPI service (install: pip install LogPress[api])
python examples/08_fastapi_service.py
# API docs at http://localhost:8000/docs

# Example 09: Auto-compress on rotation (install: pip install LogPress[monitoring])
python examples/09_log_rotation_handler.py /var/log/myapp /compressed
```

**See [examples/README.md](../examples/README.md) for detailed descriptions**

## Extract Schemas Only

```python
# Get templates without compression
templates = lp.extract_schemas(logs)

for template in templates:
    print(f"Pattern: {template['pattern']}")
    print(f"Matches: {template['count']} logs")
    print(f"Fields:  {template['fields']}")
    print()
```

## Configuration Options

```python
# Customize compression behavior
lp = LogPress(
    min_support=5,        # Minimum logs needed for a template (default: 3)
    compression_level=19  # Zstandard level 1-22 (default: 15, higher = better ratio)
)
```

## One-Liner Functions

For quick scripts:

```python
from logpress import compress, query

# Compress
stats = compress("app.log", "app.lsc")

# Query
errors = query("app.lsc", severity="ERROR")
```

## Next Steps

- **More Examples**: See [`examples/`](../examples/) directory
- **Integration Guide**: [Integration with existing systems](integration_guide.md)
- **API Reference**: [Complete API documentation](api_reference.md)
- **Performance Tips**: [Optimize for your workload](performance_tuning.md)

## Common Questions

### How does it compare to gzip?

LogPress achieves similar compression ratios (12.2× vs gzip's 12.4×) but enables **6× faster queries** through selective decompression. Use LogPress when you need to query compressed logs frequently.

### What log formats are supported?

LogPress automatically detects and handles:
- Apache/NGINX logs
- Syslog formats
- JSON logs (one per line)
- Pipe-delimited logs
- Custom application logs

No configuration needed!

### Can I use this in production?

Yes! LogPress is production-ready:
- Tested on 1M+ real-world logs
- Memory-efficient (2-4 KB per log)
- Linear time complexity
- No external dependencies

### Where should I use this?

Best for:
- **Log archival** (compress once, query many times)
- **Cloud monitoring** (reduce storage costs)
- **Security analytics** (fast filtering)
- **Compliance logs** (long-term retention)

Not ideal for:
- Real-time streaming (throughput: 0.9 MB/s)
- Logs with random UUIDs in every field
- Very small log files (<1K lines)

## Support

- **Issues**: https://github.com/adam-bouafia/LogPress/issues
- **Discussions**: https://github.com/adam-bouafia/LogPress/discussions
- **Examples**: [`examples/`](../examples/) directory
