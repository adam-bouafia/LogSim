#!/usr/bin/env python3
"""
Example 3: Streaming Large Log Files

This example shows how to compress large log files efficiently using streaming.
Processes logs in batches to avoid loading entire file into memory.

Usage:
    python 03_streaming_large_files.py [input_file] [output_file]
    python 03_streaming_large_files.py /var/log/app.log compressed.lsc
"""

from logpress.services import Compressor
from pathlib import Path
import sys
import time


def stream_compress_file(input_path: str, output_path: str, batch_size: int = 10000):
    """
    Compress large log file in batches
    
    Args:
        input_path: Path to input log file
        output_path: Path to output compressed file
        batch_size: Number of logs to process per batch
    """
    print(f"📂 Reading: {input_path}")
    print(f"💾 Output: {output_path}")
    print(f"📦 Batch size: {batch_size:,} logs\n")
    
    input_file = Path(input_path)
    if not input_file.exists():
        print(f"❌ Error: File not found: {input_path}")
        return
    
    # Get file stats
    file_size = input_file.stat().st_size
    print(f"📊 Input file size: {file_size / (1024 * 1024):.2f} MB")
    
    # Initialize compressor
    compressor = Compressor(min_support=3)
    
    # Read and compress in batches
    start_time = time.time()
    all_logs = []
    batch_count = 0
    
    print("\n🔄 Processing batches...")
    
    with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
        batch = []
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            batch.append(line)
            
            if len(batch) >= batch_size:
                batch_count += 1
                all_logs.extend(batch)
                print(f"   Batch {batch_count}: Processed {len(all_logs):,} logs", end='\r')
                batch = []
        
        # Process remaining logs
        if batch:
            batch_count += 1
            all_logs.extend(batch)
    
    print(f"\n   ✅ Read {len(all_logs):,} logs in {batch_count} batches")
    
    # Compress all logs
    print("\n🗜️  Compressing...")
    compress_start = time.time()
    compressed, stats = compressor.compress(all_logs)
    compress_time = time.time() - compress_start
    
    # Save compressed file
    print("💾 Saving compressed file...")
    compressor.save(Path(output_path))
    
    # Calculate results
    total_time = time.time() - start_time
    output_size = Path(output_path).stat().st_size
    throughput = file_size / (1024 * 1024) / total_time  # MB/s
    
    # Display results
    print("\n" + "=" * 60)
    print("✅ Compression Complete!")
    print("=" * 60)
    print(f"   Input size:         {file_size / (1024 * 1024):.2f} MB")
    print(f"   Output size:        {output_size / (1024 * 1024):.2f} MB")
    print(f"   Compression ratio:  {stats.compression_ratio:.2f}×")
    print(f"   Space saved:        {(1 - stats.compressed_size / stats.original_size) * 100:.1f}%")
    print(f"\n   Templates found:    {stats.template_count}")
    print(f"   Logs compressed:    {stats.log_count}")
    print(f"\n   Compression time:   {compress_time:.2f}s")
    print(f"   Total time:         {total_time:.2f}s")
    print(f"   Throughput:         {throughput:.2f} MB/s")
    print("=" * 60)


def create_sample_large_file():
    """Create a sample large log file for demonstration"""
    sample_log_template = [
        "[{timestamp}] INFO Application started on port 8080",
        "[{timestamp}] ERROR Database connection failed: timeout after 30s",
        "[{timestamp}] WARNING High memory usage: {memory}% used",
        "[{timestamp}] INFO User {user} logged in from {ip}",
        "[{timestamp}] ERROR Failed to process request: invalid token",
        "[{timestamp}] INFO Background task completed: duration={duration}s",
    ]
    
    output_file = Path("sample_large.log")
    print(f"🔧 Creating sample large log file: {output_file}")
    
    with open(output_file, 'w') as f:
        for i in range(50000):  # 50K logs = ~10MB
            timestamp = f"2024-12-01 10:{i // 3600:02d}:{(i // 60) % 60:02d}"
            log = sample_log_template[i % len(sample_log_template)]
            log = log.format(
                timestamp=timestamp,
                memory=75 + (i % 20),
                user=f"user{i % 100}",
                ip=f"192.168.{i % 255}.{i % 255}",
                duration=10 + (i % 50)
            )
            f.write(log + '\n')
    
    size = output_file.stat().st_size
    print(f"   ✅ Created {output_file} ({size / (1024 * 1024):.2f} MB)")
    return str(output_file)


def main():
    print("=" * 60)
    print("LogPress Example 3: Streaming Large Files")
    print("=" * 60)
    print()
    
    # Check command line arguments
    if len(sys.argv) >= 3:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
    else:
        print("📝 No input file specified. Creating sample data...")
        print()
        input_file = create_sample_large_file()
        output_file = "sample_compressed.lsc"
    
    # Compress the file
    stream_compress_file(input_file, output_file, batch_size=10000)
    
    # Cleanup sample file if created
    if len(sys.argv) < 3:
        Path(input_file).unlink()
        Path(output_file).unlink()
        print("\n🧹 Cleaned up sample files")
    
    print("\n" + "=" * 60)
    print("💡 Tip: Use this for large production log files!")
    print("   Example: python 03_streaming_large_files.py /var/log/app.log out.lsc")
    print("=" * 60)


if __name__ == "__main__":
    main()
