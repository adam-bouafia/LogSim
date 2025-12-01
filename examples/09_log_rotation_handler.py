"""
Example 09: Log Rotation Handler

Automatically compress logs when they are rotated using file system monitoring.

Use cases:
- Integration with logrotate
- Automatic compression on rotation
- Real-time log archival
- Disk space management
- Production log pipeline

This example shows how to:
1. Monitor a directory for new/rotated log files
2. Automatically compress them when created
3. Optionally delete originals after compression
4. Track compression statistics
5. Handle errors gracefully

Requirements:
    pip install watchdog

Run:
    python 09_log_rotation_handler.py /path/to/logs /path/to/compressed

Integration with logrotate:
    Add to /etc/logrotate.d/myapp:
    
    /var/log/myapp/*.log {
        daily
        rotate 7
        compress
        delaycompress
        postrotate
            # Trigger LogPress compression
            python /opt/logpress/09_log_rotation_handler.py --once /var/log/myapp
        endscript
    }
"""

import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent
from logpress import LogPress


class LogCompressionHandler(FileSystemEventHandler):
    """
    File system event handler for automatic log compression
    
    Monitors a directory and compresses log files when:
    - New .log files are created (rotation)
    - Files with .log.1, .log.2, etc. extensions appear
    """
    
    def __init__(
        self,
        output_dir: str,
        min_support: int = 3,
        delete_original: bool = False,
        min_size_kb: int = 10
    ):
        """
        Initialize the compression handler
        
        Args:
            output_dir: Directory to store compressed files
            min_support: Minimum logs per template
            delete_original: Whether to delete original after compression
            min_size_kb: Minimum file size to compress (KB)
        """
        super().__init__()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.lp = LogPress(min_support=min_support)
        self.delete_original = delete_original
        self.min_size_bytes = min_size_kb * 1024
        
        # Statistics
        self.stats = {
            'files_processed': 0,
            'files_failed': 0,
            'total_original_size': 0,
            'total_compressed_size': 0,
            'total_time': 0.0
        }
        
        # Track processed files to avoid duplicates
        self.processed_files = set()
    
    def should_process(self, file_path: str) -> bool:
        """
        Determine if a file should be compressed
        
        Args:
            file_path: Path to the file
        
        Returns:
            True if file should be processed
        """
        path = Path(file_path)
        
        # Check if already processed
        if str(path) in self.processed_files:
            return False
        
        # Check file extension patterns
        valid_extensions = [
            '.log',           # Regular log files
            '.log.1',         # Rotated logs
            '.log.2',
            '.log.3',
        ]
        
        # Check if file matches any valid pattern
        is_log_file = any(str(path).endswith(ext) for ext in valid_extensions)
        if not is_log_file:
            return False
        
        # Check file size
        try:
            if os.path.getsize(file_path) < self.min_size_bytes:
                print(f"⊘ Skipping {path.name} (too small)")
                return False
        except OSError:
            return False
        
        # Check if output already exists
        output_name = f"{path.stem}.lsc"
        output_path = self.output_dir / output_name
        if output_path.exists():
            print(f"⊘ Skipping {path.name} (already compressed)")
            return False
        
        return True
    
    def compress_file(self, file_path: str):
        """
        Compress a single log file
        
        Args:
            file_path: Path to the log file
        """
        path = Path(file_path)
        
        try:
            # Wait a moment to ensure file is fully written
            time.sleep(0.5)
            
            # Determine output path
            output_name = f"{path.stem}.lsc"
            output_path = self.output_dir / output_name
            
            print(f"🔄 Compressing {path.name}...", end=" ", flush=True)
            start_time = time.time()
            
            # Compress the file
            stats = self.lp.compress_file(str(path), str(output_path))
            
            elapsed = time.time() - start_time
            
            # Update statistics
            self.stats['files_processed'] += 1
            self.stats['total_original_size'] += stats['original_size']
            self.stats['total_compressed_size'] += stats['compressed_size']
            self.stats['total_time'] += elapsed
            
            # Mark as processed
            self.processed_files.add(str(path))
            
            # Print success
            ratio = stats['compression_ratio']
            saved_mb = stats.get('space_saved_mb', 0)
            print(f"✓ {ratio:.1f}× ratio, saved {saved_mb:.1f} MB ({elapsed:.2f}s)")
            
            # Delete original if requested
            if self.delete_original:
                os.remove(file_path)
                print(f"  🗑️  Deleted original: {path.name}")
            
        except Exception as e:
            self.stats['files_failed'] += 1
            print(f"✗ FAILED: {str(e)}")
    
    def on_created(self, event: FileCreatedEvent):
        """
        Called when a new file is created
        
        Args:
            event: File system event
        """
        if event.is_directory:
            return
        
        if self.should_process(event.src_path):
            self.compress_file(event.src_path)
    
    def on_modified(self, event):
        """
        Called when a file is modified
        
        We check if it's a newly rotated file that should be compressed
        """
        if event.is_directory:
            return
        
        # Only process if it looks like a rotated log
        if '.log.' in event.src_path and self.should_process(event.src_path):
            self.compress_file(event.src_path)
    
    def print_stats(self):
        """Print compression statistics"""
        print()
        print("=" * 70)
        print("Compression Statistics")
        print("=" * 70)
        
        if self.stats['files_processed'] > 0:
            print(f"Files processed:     {self.stats['files_processed']}")
            print(f"Files failed:        {self.stats['files_failed']}")
            
            orig_mb = self.stats['total_original_size'] / (1024 * 1024)
            comp_mb = self.stats['total_compressed_size'] / (1024 * 1024)
            saved_mb = orig_mb - comp_mb
            avg_ratio = orig_mb / comp_mb if comp_mb > 0 else 0
            
            print(f"Original size:       {orig_mb:.2f} MB")
            print(f"Compressed size:     {comp_mb:.2f} MB")
            print(f"Space saved:         {saved_mb:.2f} MB ({saved_mb/orig_mb*100:.1f}%)")
            print(f"Average ratio:       {avg_ratio:.2f}×")
            print(f"Total time:          {self.stats['total_time']:.2f}s")
            print(f"Avg time per file:   {self.stats['total_time']/self.stats['files_processed']:.2f}s")
        else:
            print("No files processed yet")
        
        print("=" * 70)


def watch_directory(
    log_dir: str,
    output_dir: str,
    min_support: int = 3,
    delete_original: bool = False,
    min_size_kb: int = 10
):
    """
    Watch a directory for new log files and compress them automatically
    
    Args:
        log_dir: Directory to monitor
        output_dir: Directory to store compressed files
        min_support: Minimum logs per template
        delete_original: Whether to delete original after compression
        min_size_kb: Minimum file size to compress (KB)
    """
    print("=" * 70)
    print("LogPress Log Rotation Handler")
    print("=" * 70)
    print()
    print(f"Monitoring:  {log_dir}")
    print(f"Output:      {output_dir}")
    print(f"Min support: {min_support}")
    print(f"Delete orig: {delete_original}")
    print(f"Min size:    {min_size_kb} KB")
    print()
    print("Press CTRL+C to stop")
    print("=" * 70)
    print()
    
    # Create event handler and observer
    event_handler = LogCompressionHandler(
        output_dir=output_dir,
        min_support=min_support,
        delete_original=delete_original,
        min_size_kb=min_size_kb
    )
    
    observer = Observer()
    observer.schedule(event_handler, log_dir, recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping...")
        observer.stop()
        observer.join()
        
        # Print final statistics
        event_handler.print_stats()
        print("\nGoodbye!")


def compress_existing_files(
    log_dir: str,
    output_dir: str,
    min_support: int = 3,
    delete_original: bool = False,
    min_size_kb: int = 10
):
    """
    Compress all existing log files in a directory (one-time operation)
    
    Useful for:
    - Initial setup
    - Cron job integration
    - Logrotate postrotate script
    
    Args:
        log_dir: Directory containing log files
        output_dir: Directory to store compressed files
        min_support: Minimum logs per template
        delete_original: Whether to delete original after compression
        min_size_kb: Minimum file size to compress (KB)
    """
    print("=" * 70)
    print("LogPress Batch Compression")
    print("=" * 70)
    print()
    print(f"Input:       {log_dir}")
    print(f"Output:      {output_dir}")
    print(f"Min support: {min_support}")
    print(f"Delete orig: {delete_original}")
    print(f"Min size:    {min_size_kb} KB")
    print("=" * 70)
    print()
    
    handler = LogCompressionHandler(
        output_dir=output_dir,
        min_support=min_support,
        delete_original=delete_original,
        min_size_kb=min_size_kb
    )
    
    # Find all log files
    log_files = []
    for ext in ['.log', '.log.[0-9]*']:
        log_files.extend(Path(log_dir).glob(f'*{ext}'))
    
    # Remove duplicates and sort
    log_files = sorted(set(log_files))
    
    print(f"Found {len(log_files)} log files to process\n")
    
    # Process each file
    for log_file in log_files:
        if handler.should_process(str(log_file)):
            handler.compress_file(str(log_file))
    
    # Print statistics
    handler.print_stats()


def main():
    """Main entry point with CLI argument parsing"""
    parser = argparse.ArgumentParser(
        description="LogPress Log Rotation Handler - Automatically compress rotated logs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Watch directory for new logs
  python 09_log_rotation_handler.py /var/log/myapp /var/log/compressed

  # Compress existing logs once (for cron/logrotate)
  python 09_log_rotation_handler.py --once /var/log/myapp /var/log/compressed

  # Watch and delete originals after compression
  python 09_log_rotation_handler.py --delete /var/log/myapp /var/log/compressed

  # Custom minimum template support
  python 09_log_rotation_handler.py --min-support 5 /var/log/myapp /var/log/compressed
        """
    )
    
    parser.add_argument(
        'log_dir',
        help='Directory to monitor for log files'
    )
    
    parser.add_argument(
        'output_dir',
        nargs='?',
        default='compressed',
        help='Directory to store compressed files (default: compressed)'
    )
    
    parser.add_argument(
        '--once',
        action='store_true',
        help='Compress existing files once and exit (for cron/logrotate)'
    )
    
    parser.add_argument(
        '--min-support',
        type=int,
        default=3,
        help='Minimum logs per template (default: 3)'
    )
    
    parser.add_argument(
        '--delete',
        action='store_true',
        help='Delete original files after successful compression'
    )
    
    parser.add_argument(
        '--min-size',
        type=int,
        default=10,
        help='Minimum file size to compress in KB (default: 10)'
    )
    
    args = parser.parse_args()
    
    # Validate directories
    if not os.path.isdir(args.log_dir):
        print(f"Error: Log directory does not exist: {args.log_dir}")
        sys.exit(1)
    
    # Run appropriate mode
    if args.once:
        # One-time compression of existing files
        compress_existing_files(
            log_dir=args.log_dir,
            output_dir=args.output_dir,
            min_support=args.min_support,
            delete_original=args.delete,
            min_size_kb=args.min_size
        )
    else:
        # Watch mode
        watch_directory(
            log_dir=args.log_dir,
            output_dir=args.output_dir,
            min_support=args.min_support,
            delete_original=args.delete,
            min_size_kb=args.min_size
        )


if __name__ == "__main__":
    main()
