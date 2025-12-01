# LogPress Examples

This directory contains practical examples for using LogPress as a library in your applications.

## 📚 Example Index

### Basic Usage
- **[01_basic_compression.py](01_basic_compression.py)** - Compress logs in 5 lines of code
- **[02_query_compressed_logs.py](02_query_compressed_logs.py)** - Filter and search compressed logs
- **[03_streaming_large_files.py](03_streaming_large_files.py)** - Process large log files efficiently

### Advanced Usage
- **[04_custom_semantic_types.py](04_custom_semantic_types.py)** - Extend semantic field recognition
- **[05_schema_extraction_only.py](05_schema_extraction_only.py)** - Extract schemas without compression
- **[06_batch_processing.py](06_batch_processing.py)** - Compress multiple log files

### Integration Examples (Require Optional Dependencies)

These examples demonstrate production-ready integrations but require additional packages:

- **[07_flask_api.py](07_flask_api.py)** - REST API with Flask
  - **Why**: Expose compression/query via HTTP endpoints for remote access
  - **Install**: `pip install LogPress[web]`
  - **Use case**: Integrate LogPress into existing web applications or microservices

- **[08_fastapi_service.py](08_fastapi_service.py)** - Async microservice with FastAPI
  - **Why**: Modern async API with automatic OpenAPI documentation
  - **Install**: `pip install LogPress[api]`
  - **Use case**: High-performance production deployments with auto-generated API docs

- **[09_log_rotation_handler.py](09_log_rotation_handler.py)** - Auto-compress on log rotation
  - **Why**: Monitor file system and compress logs when they rotate
  - **Install**: `pip install LogPress[monitoring]`
  - **Use case**: Production environments where logs rotate daily/hourly

**Install all optional features**: `pip install LogPress[all]`

## 🚀 Quick Start

```bash
# Install core library (examples 01-06 work immediately)
pip install LogPress

# Run basic example
python examples/01_basic_compression.py

# Run with your own logs
python examples/03_streaming_large_files.py /var/log/application.log output.lsc

# To run examples 07-09, install optional dependencies:
pip install LogPress[web]        # For example 07
pip install LogPress[api]        # For example 08
pip install LogPress[monitoring] # For example 09
```

## 📖 Documentation

For complete API documentation, see:
- [API Reference](../docs/api_reference.md)
- [Integration Guide](../docs/integration_guide.md)
- [Performance Tuning](../docs/performance_tuning.md)

## 💡 Need Help?

- Issues: https://github.com/adam-bouafia/LogPress/issues
- Discussions: https://github.com/adam-bouafia/LogPress/discussions
