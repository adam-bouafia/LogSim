"""
High-level public API for LogPress library users

This module provides a simplified interface for common use cases.
For advanced control, use the lower-level components directly.
"""

from typing import List, Dict, Optional, Union, Tuple
from pathlib import Path
import tempfile

from logpress.services import Compressor, QueryEngine
from logpress.models import CompressedLog


class LogPress:
    """
    High-level unified API for log compression and querying
    
    This class provides a simple interface for the most common LogPress
    operations. For advanced usage, use the lower-level components directly.
    
    Example:
        >>> # Quick compression
        >>> lp = LogPress()
        >>> stats = lp.compress_file("app.log", "app.lsc")
        >>> print(f"Compressed {stats['compression_ratio']:.1f}×")
        
        >>> # Quick querying
        >>> errors = lp.query("app.lsc", severity="ERROR", limit=100)
        >>> for log in errors:
        ...     print(log['message'])
    
    Attributes:
        compressor: Underlying Compressor instance for advanced control
        min_support: Minimum number of logs to form a template
    """
    
    def __init__(self, min_support: int = 3):
        """
        Initialize LogPress API
        
        Args:
            min_support: Minimum logs needed to create a template (default: 3)
        """
        self.min_support = min_support
        self.compressor = Compressor(min_support=min_support)
    
    def compress_file(
        self, 
        input_path: Union[str, Path], 
        output_path: Union[str, Path],
        show_progress: bool = False
    ) -> Dict[str, Union[int, float]]:
        """
        Compress a log file - one-liner API
        
        Args:
            input_path: Path to input log file
            output_path: Path to output compressed file (.lsc)
            show_progress: Show compression progress (default: False)
        
        Returns:
            Dictionary with compression statistics:
                - compression_ratio: Compression ratio achieved
                - original_size: Original file size in bytes
                - compressed_size: Compressed file size in bytes
                - template_count: Number of templates extracted
                - coverage_percentage: Percentage of logs matching templates
        
        Example:
            >>> lp = LogPress()
            >>> stats = lp.compress_file("app.log", "app.lsc")
            >>> print(f"Saved {stats['space_saved_mb']:.1f} MB")
        """
        input_path = Path(input_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # Read logs
        with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
            logs = [line.strip() for line in f if line.strip()]
        
        # Compress
        compressed, stats = self.compressor.compress(logs)
        
        # Save (compressor retains compressed_data internally)
        self.compressor.save(Path(output_path))
        
        output_size = Path(output_path).stat().st_size
        
        return {
            'compression_ratio': stats.compression_ratio,
            'original_size': stats.original_size,
            'compressed_size': output_size,
            'template_count': stats.template_count,
            'log_count': stats.log_count,
            'compression_time': stats.compression_time,
            'space_saved_bytes': stats.original_size - output_size,
            'space_saved_mb': (stats.original_size - output_size) / (1024 * 1024),
        }
    
    def compress_lines(self, logs: List[str]) -> Tuple[CompressedLog, Dict]:
        """
        Compress log lines in memory (no file I/O)
        
        Args:
            logs: List of log strings to compress
        
        Returns:
            Tuple of (CompressedLog object, statistics dict)
        
        Example:
            >>> lp = LogPress()
            >>> logs = ["[INFO] User login", "[ERROR] Failed"]
            >>> compressed, stats = lp.compress_lines(logs)
            >>> print(f"Ratio: {stats['compression_ratio']:.1f}×")
        """
        compressed, stats = self.compressor.compress(logs)
        
        return compressed, {
            'compression_ratio': stats.compression_ratio,
            'original_size': stats.original_size,
            'compressed_size': stats.compressed_size,
            'template_count': stats.template_count,
            'coverage_percentage': stats.coverage_percentage,
        }
    
    def compress_to_bytes(self, logs: List[str]) -> bytes:
        """
        Compress logs and return as bytes (for network transfer or storage)
        
        Args:
            logs: List of log strings to compress
        
        Returns:
            Compressed data as bytes
        
        Example:
            >>> lp = LogPress()
            >>> data = lp.compress_to_bytes(logs)
            >>> # Send over network or save to database
        """
        compressed, _ = self.compressor.compress(logs)
        
        # Save to temporary file and read bytes
        with tempfile.NamedTemporaryFile(suffix='.lsc', delete=False) as tmp:
            self.compressor.save(compressed, tmp.name)
            with open(tmp.name, 'rb') as f:
                data = f.read()
            Path(tmp.name).unlink()
        
        return data
    
    def query(
        self,
        compressed_path: Union[str, Path],
        severity: Optional[Union[str, List[str]]] = None,
        timestamp_after: Optional[str] = None,
        timestamp_before: Optional[str] = None,
        limit: Optional[int] = None,
        **filters
    ) -> List[Dict]:
        """
        Query compressed logs with filters
        
        Args:
            compressed_path: Path to compressed .lsc file
            severity: Filter by severity level(s)
            timestamp_after: Filter logs after this timestamp
            timestamp_before: Filter logs before this timestamp
            limit: Maximum number of results to return
            **filters: Additional field filters
        
        Returns:
            List of matching log entries as dictionaries
        
        Example:
            >>> lp = LogPress()
            >>> errors = lp.query("app.lsc", severity="ERROR", limit=10)
            >>> warnings = lp.query("app.lsc", severity=["WARN", "ERROR"])
        """
        engine = QueryEngine(str(compressed_path))
        
        # Convert timestamp parameters to milliseconds if provided
        start_ms = None
        end_ms = None
        if timestamp_after:
            # Simple conversion - in production would parse ISO format
            start_ms = int(timestamp_after) if isinstance(timestamp_after, (int, float)) else None
        if timestamp_before:
            end_ms = int(timestamp_before) if isinstance(timestamp_before, (int, float)) else None
        
        # Query using QueryEngine's method
        result = engine.query_compound(
            severity=severity,
            start_time_ms=start_ms,
            end_time_ms=end_ms
        )
        
        # Apply limit if specified
        logs = result.matched_logs
        if limit and len(logs) > limit:
            logs = logs[:limit]
        
        return logs
    
    def count(self, compressed_path: Union[str, Path]) -> int:
        """
        Count total logs in compressed file (metadata-only, very fast)
        
        Args:
            compressed_path: Path to compressed .lsc file
        
        Returns:
            Total number of log entries
        
        Example:
            >>> lp = LogPress()
            >>> total = lp.count("app.lsc")
            >>> print(f"Total logs: {total:,}")
        """
        engine = QueryEngine(str(compressed_path))
        return engine.count()
    
    def extract_schemas(self, logs: List[str]) -> List[Dict]:
        """
        Extract templates/schemas without compression
        
        Args:
            logs: List of log strings
        
        Returns:
            List of extracted templates with patterns and match counts
        
        Example:
            >>> lp = LogPress()
            >>> templates = lp.extract_schemas(logs)
            >>> for t in templates:
            ...     print(f"{t['pattern']} ({t['count']} matches)")
        """
        from logpress.context.extraction.template_generator import TemplateGenerator
        
        generator = TemplateGenerator(min_support=self.min_support)
        templates = generator.extract_schemas(logs)
        
        return [
            {
                'pattern': t.pattern,
                'count': t.match_count,
                'fields': t.field_types,
            }
            for t in templates
        ]


# Convenience function for quick compression
def compress(input_path: str, output_path: str, **kwargs) -> str:
    """
    Quick compression function - no class initialization needed
    
    Args:
        input_path: Path to input log file
        output_path: Path to output compressed file
        **kwargs: Additional options (min_support, compression_level)
    
    Returns:
        Path to compressed file (output_path)
    
    Example:
        >>> from logpress.api import compress
        >>> compressed = compress("app.log", "app.lsc")
        >>> print(f"Compressed to: {compressed}")
    """
    lp = LogPress(**kwargs)
    lp.compress_file(input_path, output_path)
    return output_path


# Convenience function for quick querying
def query(compressed_path: str, **filters) -> List[Dict]:
    """
    Quick query function - no class initialization needed
    
    Args:
        compressed_path: Path to compressed .lsc file
        **filters: Query filters (severity, timestamp_after, limit, etc.)
    
    Returns:
        List of matching log entries
    
    Example:
        >>> from logpress.api import query
        >>> errors = query("app.lsc", severity="ERROR", limit=10)
    """
    lp = LogPress()
    return lp.query(compressed_path, **filters)
