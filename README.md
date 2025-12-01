# LogPress

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](logpress/tests/)
[![Coverage](https://img.shields.io/badge/coverage-42%25-yellow.svg)](htmlcov/index.html)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![PyPI](https://img.shields.io/badge/pypi-1.0.7-blue.svg)](https://pypi.org/project/LogPress/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**Semantic log compression library with automatic schema extraction**

LogPress compresses system logs 10-20× while maintaining queryability through selective decompression. Automatically discovers log schemas using constraint-based pattern matching—no manual annotation required.

## 🚀 Quick Start

### Installation

```bash
# Core library
pip install LogPress

# Optional: Web API server (Flask REST endpoints)
pip install LogPress[web]

# Optional: Modern async API (FastAPI + OpenAPI docs)
pip install LogPress[api]

# Optional: Auto-compress on log rotation
pip install LogPress[monitoring]

# Install everything
pip install LogPress[all]
```

**Why optional dependencies?**
- **`web`**: Adds Flask for HTTP REST API (example 07) - useful for remote compression via web interface
- **`api`**: Adds FastAPI + async support (example 08) - better for production/high-traffic deployments
- **`monitoring`**: Adds Watchdog for file system monitoring (example 09) - auto-compress logs when they rotate in production
- **Core library works without any of these** - only needed if you want web servers or file monitoring features

### Basic Usage (Library)

```python
from logpress import LogPress

# Compress logs
lp = LogPress()
stats = lp.compress_file("application.log", "compressed.lsc")
print(f"Compressed {stats['compression_ratio']:.1f}×")

# Query compressed logs (6× faster than full decompression)
errors = lp.query("compressed.lsc", severity="ERROR", limit=100)
for log in errors:
    print(log['message'])
```

### One-Liner Functions

```python
from logpress import compress, query

# Compress
stats = compress("app.log", "app.lsc")

# Query
errors = query("app.lsc", severity="ERROR")
```

### Interactive Tutorial

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/adam-bouafia/LogPress/blob/main/notebooks/quickstart.ipynb)

Try LogPress in your browser with our [interactive Jupyter notebook](notebooks/quickstart.ipynb)! No installation required.

### More Examples

See [`examples/`](examples/) directory for complete examples:
- [01_basic_compression.py](examples/01_basic_compression.py) - Compress logs in 5 lines
- [02_query_compressed_logs.py](examples/02_query_compressed_logs.py) - Fast querying
- [03_streaming_large_files.py](examples/03_streaming_large_files.py) - Handle large files
- [04_custom_semantic_types.py](examples/04_custom_semantic_types.py) - Extend pattern recognition
- [05_schema_extraction_only.py](examples/05_schema_extraction_only.py) - Extract templates
- [06_batch_processing.py](examples/06_batch_processing.py) - Parallel compression
- [07_flask_api.py](examples/07_flask_api.py) - REST API service
- [08_fastapi_service.py](examples/08_fastapi_service.py) - Async microservice
- [09_log_rotation_handler.py](examples/09_log_rotation_handler.py) - Auto-compress on rotation

---

## 📖 Library Usage

### Compression

```python
from logpress import LogPress

lp = LogPress(min_support=3)  # Minimum logs per template

# From file
stats = lp.compress_file("input.log", "output.lsc")

# From list
logs = ["[INFO] Started", "[ERROR] Failed", ...]
compressed, stats = lp.compress_lines(logs)

# To bytes (for network/database)
data = lp.compress_to_bytes(logs)
```

### Querying

```python
# Filter by severity
errors = lp.query("app.lsc", severity="ERROR")
warnings = lp.query("app.lsc", severity=["WARN", "ERROR"])

# Time range
recent = lp.query("app.lsc", 
                  timestamp_after="2024-12-01 10:00:00",
                  limit=100)

# Count (metadata-only, very fast)
total = lp.count("app.lsc")
```

### Schema Extraction Only

```python
# Extract templates without compression
templates = lp.extract_schemas(logs)
for t in templates:
    print(f"{t['pattern']} - {t['count']} matches")
```

---

## 🔬 Research Background

**Master's Thesis Project** by Adam Bouafia (VU Amsterdam)

### Research Goals

- **Automatic Schema Discovery**: Extract implicit log schemas without manual annotation
- **Semantic-Aware Compression**: Achieve 10-30× compression while maintaining queryability
- **Real-World Validation**: Tested on 8 datasets with 1M+ log entries

### Key Results

- **12.2× average compression** (comparable to gzip's 12.4×)
- **6.5× query speedup** through selective decompression
- **93.7% accuracy** for automatic schema extraction
- **Outperforms gzip** on structured logs (Mac: 19.1× vs 11.7×, OpenStack: 20.8× vs 12.5×)

---

## 🖥️ Alternative Interfaces

### CLI Tools

For batch processing and automation:

```bash
# Compress logs via command line
python -m logpress compress -i app.log -o app.lsc -m

# Query compressed logs
python -m logpress query -c app.lsc --severity ERROR --limit 20

# Interactive mode (rich terminal UI)
python -m logpress.cli.interactive
```

**CLI Features**:
- 📊 Real-time compression progress
- 🎨 Rich terminal UI with tables
- 🔍 Interactive query mode
- ⚡ Batch processing support

See [CLI documentation](documentation/CLI.md) for complete reference.

### Docker

Run LogPress in a container:

```bash
# Pull from GHCR
docker pull ghcr.io/adam-bouafia/logpress:latest

# Compress a log file
docker run --rm -v "$(pwd):/data" \
  ghcr.io/adam-bouafia/logpress:latest \
  compress -i /data/app.log -o /data/app.lsc

# Query compressed logs
docker run --rm -v "$(pwd):/data" \
  ghcr.io/adam-bouafia/logpress:latest \
  query -c /data/app.lsc --severity ERROR
```

**Docker Compose** for development:

```bash
# Clone repository
git clone https://github.com/adam-bouafia/LogPress.git
cd LogPress

# Run interactive mode
docker-compose -f deployment/docker-compose.yml run --rm logpress-interactive
```

See [Docker guide](deployment/README.md) for production deployment.


### Available on Multiple Registries

LogPress Docker images are published to:
- **GitHub Container Registry**: `ghcr.io/adam-bouafia/logpress:latest`
- **Docker Hub**: `adambouafia/logpress:latest`

Both registries contain the same image with version tags (e.g., `v1.0.7`).

---

## 📁 For Developers

### Architecture

LogPress follows the **Model-Context-Protocol** design pattern:

```
logpress/
├── api.py               # High-level API (LogPress class)
├── models/              # Data structures (Token, LogTemplate, CompressedLog)
├── protocols/           # Abstract interfaces (EncoderProtocol, CompressorProtocol)
├── context/             # Core algorithms
│   ├── tokenization/    # FSM-based log parsing
│   ├── extraction/      # Template generation (log alignment)
│   ├── classification/  # Semantic type detection (pattern-based)
│   └── encoding/        # Compression codecs (delta, dictionary, varint)
└── services/            # High-level orchestration
    ├── compressor.py    # 6-stage compression pipeline
    ├── query_engine.py  # Queryable decompression with indexes
    └── evaluator.py     # Accuracy metrics vs ground truth
```

See [MCP Architecture](documentation/MCP_ARCHITECTURE.md) for design details.

### Testing

**Test Suite**: 25 tests, 100% passing, 42% coverage

```bash
# Run all tests
bash scripts/run-tests.sh

# Watch mode (re-run on changes)
pip install pytest-watch
ptw logpress/tests/ -- -v

# Coverage report
open htmlcov/index.html
```

See [Testing Guide](documentation/TESTING.md) for details.

### Research Datasets

The repository includes 8 real-world log sources (~1.07M entries) for evaluation:

| Dataset | Lines | Description |
|---------|-------|-------------|
| Apache | 52K | Web server logs |
| HealthApp | 212K | Android health tracking |
| HPC | 433K | High-performance computing cluster |
| Linux | 26K | Linux system logs |
| Mac | 117K | macOS system logs |
| OpenStack | 137K | Cloud infrastructure logs |
| Proxifier | 21K | Network proxy logs |
| Zookeeper | 74K | Distributed coordination logs |

Datasets are in `data/datasets/`, ground truth annotations in `data/ground_truth/`.

---

## 📖 How It Works

### Schema Extraction

LogPress automatically discovers log structure using a 6-stage pipeline:

1. **Tokenization**: Parse diverse log formats (Apache, Syslog, JSON, custom)
2. **Semantic Classification**: Detect field types (timestamp, IP, severity, metrics)
3. **Field Grouping**: Find related fields (host:port, user+action)
4. **Template Generation**: Extract patterns using log alignment algorithm
5. **Schema Versioning**: Track format changes over time
6. **Validation**: Verify against ground truth (93.7% accuracy)

**Example**:
```
Input:
  [Thu Jun 09 06:07:04 2005] [notice] LDAP: Built with OpenLDAP
  [Thu Jun 09 06:07:05 2005] [notice] LDAP: SSL unavailable
  
Detected Schema:
  [TIMESTAMP] [SEVERITY] LDAP: [MESSAGE]
```

### Compression Strategy

LogPress uses **semantic-aware encoding** tailored to each field:

| Field Type | Codec | Compression |
|------------|-------|-------------|
| Timestamps | Delta encoding | 8-10× |
| Severity/Status | Dictionary encoding | 5-7× |
| Metrics | Gorilla time-series | 3-5× |
| Messages | Token pool + refs | Variable |
| Stack traces | Reference tracking | High |

**Queryable indexes** enable filtering without full decompression (6.5× speedup).

## 🧪 Testing

### Run Complete Test Suite

```bash
# All tests with coverage
bash scripts/run-tests.sh

# View coverage report
firefox htmlcov/index.html
```

### Pre-Production Validation

```bash
# Validate before deployment
bash scripts/run-pre-production-tests.sh
```

**Test Status**: ✅ 25/25 tests passing (100%)
- Unit tests: 9 tests
- Integration tests: 8 tests
- E2E tests: 3 tests
- Performance benchmarks: 5 tests

### Performance Benchmarks

```bash
# Run benchmarks
python -m pytest logpress/tests/performance/ --benchmark-only

# Expected results:
# - Compression: >500 ops/sec
# - Template extraction: >900 ops/sec
# - Linear scalability: 100 → 10,000 logs
```

## 📚 Documentation

- [Documentation Index](documentation/README.md) - Complete documentation overview
- [Testing Guide](documentation/TESTING.md) - Test strategy and commands
- [MCP Architecture](documentation/MCP_ARCHITECTURE.md) - System design details
- [API Reference](documentation/API.md) - Python API usage
- [Docker Guide](deployment/README.md) - Container deployment

## 🎓 Research Context

**Master's Thesis**: Automatic Schema Extraction from Unstructured System Logs  
**Duration**: 26 weeks (4 phases)  
**Target Venues**: VLDB, SIGMOD, IEEE BigData  
**Novel Contribution**: Semantic-aware compression adapting to log content types

### Related Work
- **Log Parsing**: Drain, Spell, LogPai
- **Schema Inference**: Lakehouse formats (Parquet, ORC)
- **Compression**: Generic (gzip, zstd) vs specialized (LogShrink)

### Key Differentiators
- ✅ No ML models (constraint-based approach)
- ✅ Semantic awareness (field-type-specific compression)
- ✅ Query preservation (columnar indexes)
- ✅ Schema evolution tracking
- ✅ Lossless compression (exact reconstruction)

## 🛠️ Development

### Setup Development Environment

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-benchmark pytest-mock

# Run tests on file changes (watch mode)
pip install pytest-watch
ptw logpress/tests/ -- -v
```

### Contribution Workflow

1. Create feature branch: `git checkout -b feature/new-encoder`
2. Make changes and add tests
3. Run validation: `bash scripts/run-pre-production-tests.sh`
4. Submit PR (GitHub Actions runs full test suite)

### Adding New Semantic Type Patterns

```python
# logpress/context/classification/semantic_types.py

def recognize_custom_field(token: str) -> Tuple[str, float]:
    """
    Add pattern for new field type.
    
    Returns:
        (field_type, confidence_score)
    """
    if re.match(r'^[A-Z]{3}-\d{4}$', token):
        return ('ERROR_CODE', 0.95)  # High confidence
    return ('UNKNOWN', 0.0)
```

### Adding New Compression Codecs

```python
# logpress/context/encoding/custom_encoder.py

from logpress.protocols import EncoderProtocol

class CustomEncoder(EncoderProtocol):
    def encode(self, values: List[Any]) -> bytes:
        # Your encoding logpress
        pass
    
    def decode(self, data: bytes) -> List[Any]:
        # Your decoding logpress
        pass
```

## 📦 Dependencies

### Core Libraries
```
msgpack>=1.0.0          # Serialization
zstandard>=0.21.0       # Compression baseline
python-dateutil>=2.8.0  # Timestamp parsing
regex>=2023.0.0         # Advanced pattern matching
rich>=13.0.0            # Terminal UI
click>=8.1.0            # CLI framework
```

### Testing
```
pytest>=7.4.0           # Test framework
pytest-cov>=4.1.0       # Coverage reporting
pytest-benchmark>=4.0.0 # Performance testing
pytest-mock>=3.12.0     # Mocking utilities
```

### Optional Tools
```bash
# Baseline comparison
gzip --version

# Command-line benchmarking
cargo install hyperfine

# Memory profiling
pip install memory-profiler
```

## 🐳 Docker Deployment

### Build & Run

```bash
# Build all services
docker-compose -f deployment/docker-compose.yml build

# Run interactive CLI
docker-compose -f deployment/docker-compose.yml run --rm logpress-interactive

# Run compression
docker-compose -f deployment/docker-compose.yml run --rm logpress-cli \
  compress -i /app/data/datasets/Apache/Apache_full.log -o /app/evaluation/compressed/apache.lsc
```

### Environment Variables

```bash
# Set in docker-compose.yml
PYTHONUNBUFFERED=1      # Real-time output
TERM=xterm-256color     # Colored terminal
MIN_SUPPORT=3           # Template extraction threshold
ZSTD_LEVEL=15           # Compression level (1-22)
```

## 🤝 Contributing

We welcome contributions! Please see CONTRIBUTING.md for guidelines.

### Areas for Contribution
- [ ] Additional semantic type patterns
- [ ] New compression codecs
- [ ] Query optimization
- [ ] Schema visualization
- [ ] Performance improvements

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.


## 🔗 Links

- [Project Documentation](documentation/README.md)
- [Test Results](evaluation/results/)
- [Research Roadmap](PROJECT.md)
- [GitHub Repository](https://github.com/adam-bouafia/logpress)

## 📞 Contact

- **Author**: Adam Bouafia
- **Repository**: https://github.com/adam-bouafia/logpress
- **Linkedin**: https://www.linkedin.com/in/adam-bouafia 

---

**Status**: ✅ Production Ready | 🧪 All Tests Passing (25/25) | 📊 Coverage: 42%

Built with ❤️ for research in log analysis and semantic compression.
