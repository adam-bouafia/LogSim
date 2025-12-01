#!/usr/bin/env python3
"""
Example 1: Basic Log Compression with LogPress

This example demonstrates the simplest way to compress logs using LogPress.
Perfect for getting started in under 5 minutes.

Usage:
    python 01_basic_compression.py
"""

from logpress.services import Compressor
from pathlib import Path


def main():
    print("=" * 60)
    print("LogPress Example 1: Basic Compression")
    print("=" * 60)
    
    # Sample log data (in real usage, read from files)
    sample_logs = [
        "[2024-12-01 10:00:00] INFO User login successful: user_id=12345",
        "[2024-12-01 10:00:01] ERROR Database connection failed: timeout after 30s",
        "[2024-12-01 10:00:02] INFO User login successful: user_id=67890",
        "[2024-12-01 10:00:03] WARNING High memory usage: 85% used",
        "[2024-12-01 10:00:04] INFO User logout: user_id=12345",
        "[2024-12-01 10:00:05] ERROR Database connection failed: timeout after 30s",
        "[2024-12-01 10:00:06] INFO User login successful: user_id=11111",
        "[2024-12-01 10:00:07] INFO Processing request: endpoint=/api/users",
        "[2024-12-01 10:00:08] ERROR Database connection failed: timeout after 30s",
        "[2024-12-01 10:00:09] INFO User logout: user_id=67890",
    ]
    
    print(f"\n📊 Original Data:")
    print(f"   Logs: {len(sample_logs)}")
    print(f"   Size: {sum(len(log) for log in sample_logs)} bytes")
    print(f"\n📝 Sample logs:")
    for log in sample_logs[:3]:
        print(f"   {log}")
    print(f"   ... and {len(sample_logs) - 3} more")
    
    # Step 1: Create compressor
    print("\n🔧 Creating compressor...")
    compressor = Compressor(
        min_support=2,  # Minimum logs needed to form a template
    )
    
    # Step 2: Compress logs
    print("🗜️  Compressing logs...")
    compressed, stats = compressor.compress(sample_logs)
    
    # Step 3: Display results
    print("\n✅ Compression Complete!")
    print(f"   Compressed Size: {stats.compressed_size} bytes")
    print(f"   Compression Ratio: {stats.compression_ratio:.2f}×")
    print(f"   Templates Extracted: {stats.template_count}")
    print(f"   Logs Compressed: {stats.log_count}")
    
    # Step 4: Save to file
    output_path = Path("example_output.lsc")
    print(f"\n💾 Saving to {output_path}...")
    compressor.save(output_path)
    print(f"   Saved! File size: {output_path.stat().st_size} bytes")
    
    # Step 5: Demonstrate loading
    print("\n📂 Loading compressed file...")
    loaded = compressor.load(str(output_path))
    print(f"   Loaded successfully! Contains {len(loaded.templates)} templates")
    
    # Display extracted templates
    print("\n📋 Extracted Templates:")
    for i, template in enumerate(loaded.templates[:3], 1):
        print(f"   {i}. {template['pattern']}")
        print(f"      Matches: {template['match_count']} logs")
    
    # Cleanup
    output_path.unlink()
    print("\n✨ Done! Output file cleaned up.")
    
    print("\n" + "=" * 60)
    print("Next: Try 02_query_compressed_logs.py to query this data!")
    print("=" * 60)


if __name__ == "__main__":
    main()
