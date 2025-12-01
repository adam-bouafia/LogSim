"""
Example 06: Batch Processing Multiple Log Files

Learn how to compress multiple log files efficiently using parallel processing.

Use cases:
- Nightly compression jobs
- Log archival systems
- Processing rotated log files
- Bulk compression of historical logs
- CI/CD pipeline integration

This example demonstrates:
1. Processing multiple files in parallel
2. Progress tracking and reporting
3. Error handling for individual files
4. Generating batch summary reports
"""

import os
import glob
import time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Dict, Tuple
from logpress import LogPress


def create_sample_log_files(output_dir: str = "temp_logs", num_files: int = 5):
    """Create sample log files for batch processing"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    log_templates = [
        "[{timestamp}] INFO Application started successfully",
        "[{timestamp}] ERROR Database connection failed: {error}",
        "[{timestamp}] WARN Memory usage above threshold: {percent}%",
        "[{timestamp}] INFO Request processed in {ms}ms",
        "[{timestamp}] DEBUG Cache hit for key: {key}",
    ]
    
    files_created = []
    
    for i in range(num_files):
        filename = f"{output_dir}/app-{i+1}.log"
        
        with open(filename, 'w') as f:
            # Create different sized files
            num_logs = 1000 * (i + 1)  # 1K, 2K, 3K, 4K, 5K lines
            
            for j in range(num_logs):
                timestamp = f"2024-12-01 10:{(j%60):02d}:{(j%60):02d}"
                template_idx = j % len(log_templates)
                template = log_templates[template_idx]
                
                # Fill in template variables
                log = template.format(
                    timestamp=timestamp,
                    error=f"error_{j%10}",
                    percent=50 + (j % 50),
                    ms=10 + (j % 100),
                    key=f"key_{j%100}"
                )
                
                f.write(log + "\n")
        
        file_size = os.path.getsize(filename)
        files_created.append((filename, file_size))
    
    return files_created


def compress_single_file(file_path: str, output_dir: str = "compressed_batch") -> Dict:
    """
    Compress a single file (used in parallel processing)
    
    Returns:
        Dictionary with compression results
    """
    try:
        start_time = time.time()
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Determine output filename
        input_name = Path(file_path).name
        output_name = input_name.replace('.log', '.lsc')
        output_path = os.path.join(output_dir, output_name)
        
        # Compress file
        lp = LogPress(min_support=3)
        stats = lp.compress_file(file_path, output_path)
        
        # Add timing and file info
        elapsed_time = time.time() - start_time
        stats['input_file'] = file_path
        stats['output_file'] = output_path
        stats['elapsed_time'] = elapsed_time
        stats['success'] = True
        stats['error'] = None
        
        return stats
        
    except Exception as e:
        return {
            'input_file': file_path,
            'output_file': None,
            'success': False,
            'error': str(e),
            'elapsed_time': time.time() - start_time if 'start_time' in locals() else 0
        }


def batch_compress_sequential(file_paths: List[str], output_dir: str = "compressed_batch") -> List[Dict]:
    """
    Compress files one by one (sequential processing)
    
    Slower but simpler and uses less memory
    """
    print("=" * 70)
    print("Sequential Batch Processing")
    print("=" * 70)
    print()
    
    results = []
    total_start = time.time()
    
    for i, file_path in enumerate(file_paths, 1):
        print(f"Processing {i}/{len(file_paths)}: {Path(file_path).name}...", end=" ")
        
        result = compress_single_file(file_path, output_dir)
        results.append(result)
        
        if result['success']:
            ratio = result.get('compression_ratio', 0)
            time_taken = result['elapsed_time']
            print(f"✓ {ratio:.1f}× in {time_taken:.2f}s")
        else:
            print(f"✗ FAILED: {result['error']}")
    
    total_time = time.time() - total_start
    
    print()
    print(f"Total time: {total_time:.2f}s")
    print()
    
    return results


def batch_compress_parallel(file_paths: List[str], output_dir: str = "compressed_batch", 
                            max_workers: int = 4) -> List[Dict]:
    """
    Compress files in parallel using multiple processes
    
    Faster for multiple files but uses more memory
    """
    print("=" * 70)
    print(f"Parallel Batch Processing ({max_workers} workers)")
    print("=" * 70)
    print()
    
    results = []
    total_start = time.time()
    
    # Use ProcessPoolExecutor for CPU-bound compression
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_file = {
            executor.submit(compress_single_file, file_path, output_dir): file_path
            for file_path in file_paths
        }
        
        # Process completed tasks as they finish
        completed = 0
        for future in as_completed(future_to_file):
            file_path = future_to_file[future]
            completed += 1
            
            try:
                result = future.result()
                results.append(result)
                
                filename = Path(file_path).name
                if result['success']:
                    ratio = result.get('compression_ratio', 0)
                    time_taken = result['elapsed_time']
                    print(f"[{completed}/{len(file_paths)}] ✓ {filename}: {ratio:.1f}× in {time_taken:.2f}s")
                else:
                    print(f"[{completed}/{len(file_paths)}] ✗ {filename}: FAILED - {result['error']}")
                    
            except Exception as e:
                print(f"[{completed}/{len(file_paths)}] ✗ {file_path}: EXCEPTION - {str(e)}")
                results.append({
                    'input_file': file_path,
                    'success': False,
                    'error': str(e)
                })
    
    total_time = time.time() - total_start
    
    print()
    print(f"Total time: {total_time:.2f}s")
    print(f"Speedup: {(len(file_paths) * results[0]['elapsed_time'] / total_time):.1f}× faster than sequential")
    print()
    
    return results


def generate_batch_report(results: List[Dict]):
    """Generate comprehensive batch processing report"""
    
    print("=" * 70)
    print("Batch Processing Report")
    print("=" * 70)
    print()
    
    # Overall statistics
    total_files = len(results)
    successful = sum(1 for r in results if r['success'])
    failed = total_files - successful
    
    print(f"Files Processed: {total_files}")
    print(f"  ✓ Successful:  {successful} ({successful/total_files*100:.1f}%)")
    print(f"  ✗ Failed:      {failed} ({failed/total_files*100:.1f}%)")
    print()
    
    # Compression statistics (only successful)
    successful_results = [r for r in results if r['success']]
    
    if successful_results:
        total_original = sum(r.get('original_size', 0) for r in successful_results)
        total_compressed = sum(r.get('compressed_size', 0) for r in successful_results)
        avg_ratio = sum(r.get('compression_ratio', 0) for r in successful_results) / len(successful_results)
        total_saved = total_original - total_compressed
        
        print("Compression Statistics:")
        print("-" * 70)
        print(f"Original size:    {total_original / (1024*1024):.2f} MB")
        print(f"Compressed size:  {total_compressed / (1024*1024):.2f} MB")
        print(f"Space saved:      {total_saved / (1024*1024):.2f} MB ({total_saved/total_original*100:.1f}%)")
        print(f"Average ratio:    {avg_ratio:.2f}×")
        print()
        
        # Performance statistics
        total_time = sum(r.get('elapsed_time', 0) for r in successful_results)
        avg_time = total_time / len(successful_results)
        throughput = (total_original / (1024*1024)) / total_time if total_time > 0 else 0
        
        print("Performance Statistics:")
        print("-" * 70)
        print(f"Total time:       {total_time:.2f}s")
        print(f"Average per file: {avg_time:.2f}s")
        print(f"Throughput:       {throughput:.2f} MB/s")
        print()
        
        # Per-file details
        print("Individual File Results:")
        print("-" * 70)
        print(f"{'File':<20} {'Size':<12} {'Ratio':<10} {'Time':<10} {'Status'}")
        print("-" * 70)
        
        for result in results:
            filename = Path(result['input_file']).name[:18]
            
            if result['success']:
                size_mb = result.get('original_size', 0) / (1024*1024)
                ratio = result.get('compression_ratio', 0)
                elapsed = result.get('elapsed_time', 0)
                status = "✓ OK"
                
                print(f"{filename:<20} {size_mb:>8.2f} MB  {ratio:>6.1f}×    {elapsed:>6.2f}s    {status}")
            else:
                print(f"{filename:<20} {'N/A':<12} {'N/A':<10} {'N/A':<10} ✗ FAILED")
        
        print()
    
    # List failures if any
    failed_results = [r for r in results if not r['success']]
    if failed_results:
        print("Failed Files:")
        print("-" * 70)
        for result in failed_results:
            filename = Path(result['input_file']).name
            error = result.get('error', 'Unknown error')
            print(f"  ✗ {filename}")
            print(f"    Error: {error}")
        print()


def demonstrate_batch_processing():
    """Main demonstration of batch processing"""
    
    print("=" * 70)
    print("Example 06: Batch Processing Multiple Log Files")
    print("=" * 70)
    print()
    
    # Step 1: Create sample files
    print("Step 1: Creating sample log files...")
    print("-" * 70)
    
    files_created = create_sample_log_files(num_files=5)
    
    for filename, size in files_created:
        print(f"  Created: {filename} ({size / 1024:.1f} KB)")
    
    total_size = sum(size for _, size in files_created)
    print(f"  Total: {len(files_created)} files, {total_size / (1024*1024):.2f} MB")
    print()
    
    file_paths = [f for f, _ in files_created]
    
    # Step 2: Sequential processing
    print("\nStep 2: Sequential Processing")
    print("-" * 70)
    results_seq = batch_compress_sequential(file_paths, output_dir="compressed_sequential")
    
    # Step 3: Parallel processing
    print("\nStep 3: Parallel Processing")
    print("-" * 70)
    results_par = batch_compress_parallel(file_paths, output_dir="compressed_parallel", max_workers=4)
    
    # Step 4: Generate report
    print("\nStep 4: Report Generation")
    generate_batch_report(results_par)
    
    # Cleanup
    print("Cleaning up sample files...")
    import shutil
    try:
        shutil.rmtree("temp_logs")
        shutil.rmtree("compressed_sequential")
        shutil.rmtree("compressed_parallel")
        print("✓ Cleanup complete")
    except Exception as e:
        print(f"✗ Cleanup error: {e}")


def demonstrate_directory_processing():
    """Show how to process all logs in a directory"""
    
    print()
    print("=" * 70)
    print("Processing Directory of Log Files")
    print("=" * 70)
    print()
    
    print("Example usage for production:")
    print("-" * 70)
    print("""
# Process all .log files in a directory
import glob
from logpress import LogPress

log_dir = "/var/log/myapp/"
output_dir = "/var/log/myapp/compressed/"

# Find all log files
log_files = glob.glob(f"{log_dir}/**/*.log", recursive=True)

# Compress each file
lp = LogPress(min_support=5)
for log_file in log_files:
    output_file = log_file.replace(log_dir, output_dir).replace('.log', '.lsc')
    stats = lp.compress_file(log_file, output_file)
    print(f"Compressed {log_file}: {stats['compression_ratio']:.1f}×")

# Or use parallel processing (shown in this example)
results = batch_compress_parallel(log_files, output_dir, max_workers=8)
    """)
    print()


if __name__ == "__main__":
    demonstrate_batch_processing()
    demonstrate_directory_processing()
    
    print("=" * 70)
    print("Key Takeaways:")
    print("=" * 70)
    print("""
1. Sequential processing is simpler but slower
2. Parallel processing speeds up batch jobs significantly
3. Use max_workers = CPU count for best performance
4. Error handling prevents one failure from stopping the batch
5. Reports provide visibility into batch job results

When to use batch processing:
✓ Nightly log compression jobs
✓ Processing rotated log files
✓ Bulk archival of historical logs
✓ CI/CD pipeline integration
✓ Large-scale log management

Performance tips:
- Use parallel processing for >3 files
- Set max_workers = CPU cores (typically 4-8)
- Process files in order of size (largest first)
- Monitor memory usage with many concurrent workers
- Use sequential for very large individual files

Next steps:
- Integrate with your log rotation system
- Schedule as cron job or systemd timer
- Add monitoring and alerting
- Store reports for audit trails
    """)
