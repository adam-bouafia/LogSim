"""
logpress - Semantic-Driven Log Schema Extraction and Compression

A production-ready system for extracting implicit schemas from unstructured
system logs and compressing them with semantic awareness.

Quick Start (High-level API):
    >>> from logpress import LogPress
    >>> lp = LogPress()
    >>> stats = lp.compress_file("app.log", "app.lsc")
    >>> errors = lp.query("app.lsc", severity="ERROR")

Advanced Usage (Low-level components):
    >>> from logpress import Compressor, QueryEngine, TemplateGenerator
    >>> compressor = Compressor(min_support=3)
    >>> compressed, stats = compressor.compress(log_lines)

MCP Architecture:
- Models: Pure data structures (Token, LogTemplate, CompressedLog)
- Protocols: Interface contracts (TokenizerProtocol, EncoderProtocol)
- Context: Domain implementations (Tokenization, Extraction, Encoding)
- Services: Application orchestration (Compressor, QueryEngine)
- CLI: User interface (compress, query commands)
"""

__version__ = "1.0.7"
__author__ = "Adam Bouafia"
__license__ = "MIT"

# High-level API (recommended for most users)
from logpress.api import LogPress, compress, query

# Core MCP layers (advanced usage)
from logpress import models, protocols
from logpress.context import LogTokenizer, Tokenizer, TemplateGenerator, SemanticTypeRecognizer, SemanticFieldClassifier
from logpress.services import SemanticCompressor, Compressor, QueryEngine, SchemaEvaluator, Evaluator, SchemaVersioner

# Legacy compatibility aliases
LogTokenizer = LogTokenizer
SemanticTypeRecognizer = SemanticTypeRecognizer
SchemaEvaluator = SchemaEvaluator

__all__ = [
    # High-level API (⭐ Start here!)
    'LogPress',           # Main user-facing class
    'compress',           # Quick compression function
    'query',              # Quick query function
    
    # Low-level components (advanced usage)
    'Compressor',         # Direct compression control
    'QueryEngine',        # Custom query logic
    'TemplateGenerator',  # Schema extraction only
    'SemanticTypeRecognizer',  # Extend semantic types
    'SemanticFieldClassifier',
    'SchemaVersioner',
    'SchemaEvaluator',
    'Evaluator',
    
    # MCP Architecture
    'models',
    'protocols',
    'LogTokenizer',
    'Tokenizer',
    'SemanticCompressor',
]
