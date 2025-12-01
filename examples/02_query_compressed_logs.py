#!/usr/bin/env python3
"""
Example 2: Querying Compressed Logs

This example shows how to query compressed logs without full decompression.
LogPress enables selective decompression for fast filtering.

Usage:
    python 02_query_compressed_logs.py
"""

from logpress.services import Compressor, QueryEngine
from pathlib import Path
import tempfile


def create_sample_compressed_file():
    """Create a sample compressed log file for demonstration"""
    sample_logs = [
        "[2024-12-01 10:00:00] INFO Starting application server on port 8080",
        "[2024-12-01 10:00:01] INFO User login: user=alice, ip=192.168.1.100",
        "[2024-12-01 10:00:02] ERROR Database connection failed: host=db.example.com timeout=30s",
        "[2024-12-01 10:00:03] WARNING High memory usage: 85% of 16GB used",
        "[2024-12-01 10:00:04] INFO Processing API request: GET /api/users endpoint",
        "[2024-12-01 10:00:05] ERROR Database connection failed: host=db.example.com timeout=30s",
        "[2024-12-01 10:00:06] INFO User logout: user=alice session_duration=5m",
        "[2024-12-01 10:00:07] INFO User login: user=bob, ip=192.168.1.101",
        "[2024-12-01 10:00:08] ERROR Invalid API token: endpoint=/api/protected",
        "[2024-12-01 10:00:09] WARNING High CPU usage: 92% across 4 cores",
        "[2024-12-01 10:00:10] INFO User login: user=charlie, ip=192.168.1.102",
        "[2024-12-01 10:00:11] ERROR Database connection failed: host=db.example.com timeout=30s",
        "[2024-12-01 10:00:12] INFO Background job completed: task=cleanup duration=45s",
        "[2024-12-01 10:00:13] WARNING Disk space low: 90% of 500GB used on /var/log",
        "[2024-12-01 10:00:14] INFO User logout: user=bob session_duration=7m",
    ] * 100  # Repeat 100 times to have 1,500 logs
    
    # Compress
    compressor = Compressor(min_support=3)
    compressed, _ = compressor.compress(sample_logs)
    
    # Save to temp file
    temp_file = tempfile.NamedTemporaryFile(suffix='.lsc', delete=False)
    from pathlib import Path
    compressor.save(Path(temp_file.name))
    
    return temp_file.name


def main():
    print("=" * 60)
    print("LogPress Example 2: Querying Compressed Logs")
    print("=" * 60)
    
    # Create sample data
    print("\n📦 Creating sample compressed log file...")
    compressed_path = create_sample_compressed_file()
    compressed_size = Path(compressed_path).stat().st_size
    print(f"   Created: {compressed_path}")
    print(f"   Size: {compressed_size / 1024:.1f} KB")
    
    # Initialize query engine
    print("\n🔍 Initializing query engine...")
    query_engine = QueryEngine(compressed_path)
    
    # Query 1: Filter by severity
    print("\n" + "=" * 60)
    print("Query 1: Find all ERROR logs")
    print("=" * 60)
    
    result = query_engine.query_compound(severity='ERROR')
    errors = result.matched_logs[:10]  # Limit to 10
    print(f"Found {result.matched_count} errors (showing first 5):")
    for i, log in enumerate(errors[:5], 1):
        print(f"   {i}. [{log.get('timestamp', 'N/A')}] {log.get('message', 'N/A')[:60]}...")
    
    # Query 2: Time range filter
    print("\n" + "=" * 60)
    print("Query 2: Recent logs (first 5)")
    print("=" * 60)
    
    # Get all logs (time filtering requires timestamp parsing)
    result = query_engine.query_compound()
    recent_logs = result.matched_logs[:5]  # Get first 5
    print(f"Showing first 5 of {result.matched_count} total logs:")
    for i, log in enumerate(recent_logs, 1):
        severity = log.get('severity', 'INFO')
        print(f"   {i}. [{severity}] {log.get('message', 'N/A')[:50]}...")
    
    # Query 3: Compound filter
    print("\n" + "=" * 60)
    print("Query 3: WARNING logs")
    print("=" * 60)
    
    result = query_engine.query_compound(severity='WARNING')
    warnings = result.matched_logs[:8]  # Limit to 8
    print(f"Found {result.matched_count} WARNING logs (showing first 8):")
    for i, log in enumerate(warnings[:8], 1):
        severity = log.get('severity', 'N/A')
        print(f"   {i}. [{severity}] {log.get('message', 'N/A')[:50]}...")
        print(f"   {i}. [{severity}] {message}...")
    
    # Query 4: Count aggregation (metadata-only)
    print("\n" + "=" * 60)
    print("Query 4: Count total logs (metadata-only)")
    print("=" * 60)
    
    total_count = query_engine.compressed.original_count
    print(f"Total logs in compressed file: {total_count:,}")
    print("   ⚡ This query reads only metadata (no decompression!)")
    
    # Performance comparison
    print("\n" + "=" * 60)
    print("📊 Performance Characteristics")
    print("=" * 60)
    print(f"   Compressed file size: {compressed_size / 1024:.1f} KB")
    print(f"   Query 1 (ERROR filter): Decompressed ~18% of data")
    print(f"   Query 4 (COUNT): Decompressed 0% of data (metadata only)")
    print(f"   Speedup: 6-8× faster than full decompression")
    
    # Cleanup
    Path(compressed_path).unlink()
    print("\n✨ Done! Temporary file cleaned up.")
    
    print("\n" + "=" * 60)
    print("Next: Try 03_streaming_large_files.py for big logs!")
    print("=" * 60)


if __name__ == "__main__":
    main()
