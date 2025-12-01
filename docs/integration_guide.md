# Integration Guide

How to integrate LogPress into existing systems and workflows.

## Table of Contents

- [Flask/FastAPI Integration](#flaskfastapi-integration)
- [Log Rotation Handler](#log-rotation-handler)
- [Docker Integration](#docker-integration)
- [Kubernetes Deployment](#kubernetes-deployment)
- [AWS S3 Integration](#aws-s3-integration)
- [CI/CD Pipeline](#cicd-pipeline)

## Flask/FastAPI Integration

**Note**: Complete working examples are in the `examples/` directory:
- **Example 07**: [07_flask_api.py](../examples/07_flask_api.py) - Full Flask REST API with 7 endpoints
- **Example 08**: [08_fastapi_service.py](../examples/08_fastapi_service.py) - FastAPI with OpenAPI docs

### Installation

```bash
# Flask
pip install LogPress[web]

# FastAPI
pip install LogPress[api]
```

### Flask Example

```python
from flask import Flask, request, jsonify
from logpress import LogPress

app = Flask(__name__)
lp = LogPress()

@app.route('/compress', methods=['POST'])
def compress_logs():
    """Compress uploaded log file"""
    file = request.files['logfile']
    output_path = f"compressed/{file.filename}.lsc"
    
    stats = lp.compress_file(file, output_path)
    return jsonify(stats)

@app.route('/query', methods=['GET'])
def query_logs():
    """Query compressed logs"""
    filename = request.args.get('file')
    severity = request.args.get('severity')
    limit = int(request.args.get('limit', 100))
    
    results = lp.query(f"compressed/{filename}", severity=severity, limit=limit)
    return jsonify({'logs': results, 'count': len(results)})

if __name__ == '__main__':
    app.run(debug=True)
```

**See [examples/07_flask_api.py](../examples/07_flask_api.py) for the complete implementation with all endpoints.**

### FastAPI Example

```python
from fastapi import FastAPI, UploadFile, File, Query
from logpress import LogPress
from typing import Optional, List

app = FastAPI(title="LogPress API")
lp = LogPress()

@app.post("/compress")
async def compress_logs(file: UploadFile = File(...)):
    """Compress uploaded log file"""
    content = await file.read()
    lines = content.decode().splitlines()
    
    compressed, stats = lp.compress_lines(lines)
    
    # Save to storage
    output_path = f"compressed/{file.filename}.lsc"
    with open(output_path, 'wb') as f:
        f.write(compressed)
    
    return {"filename": file.filename, **stats}

@app.get("/query")
async def query_logs(
    file: str,
    severity: Optional[str] = None,
    timestamp_after: Optional[str] = None,
    timestamp_before: Optional[str] = None,
    limit: int = Query(100, le=10000)
):
    """Query compressed logs with filters"""
    results = lp.query(
        f"compressed/{file}",
        severity=severity,
        timestamp_after=timestamp_after,
        timestamp_before=timestamp_before,
        limit=limit
    )
    return {"logs": results, "count": len(results)}

@app.get("/count")
async def count_logs(file: str):
    """Get total log count (metadata-only, fast!)"""
    count = lp.count(f"compressed/{file}")
    return {"file": file, "total_logs": count}
```

## Log Rotation Handler

**Note**: Complete working example: [09_log_rotation_handler.py](../examples/09_log_rotation_handler.py)

### Installation

```bash
pip install LogPress[monitoring]
```

### Quick Usage

```bash
# Monitor directory and auto-compress rotated logs
python examples/09_log_rotation_handler.py /var/log/myapp /compressed

# One-time compression of existing rotated logs
python examples/09_log_rotation_handler.py /var/log/myapp /compressed --once

# Auto-delete originals after compression
python examples/09_log_rotation_handler.py /var/log/myapp /compressed --delete
```

### Basic Integration

Automatically compress logs when rotated:

```python
import os
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from logpress import LogPress

class LogCompressionHandler(FileSystemEventHandler):
    """Compress logs when they are rotated"""
    
    def __init__(self, compress_dir='compressed'):
        self.lp = LogPress()
        self.compress_dir = Path(compress_dir)
        self.compress_dir.mkdir(exist_ok=True)
    
    def on_created(self, event):
        """Handle new rotated log files"""
        if event.is_directory:
            return
        
        # Only process rotated logs (e.g., app.log.1, app.log.2)
        if '.log.' in event.src_path or event.src_path.endswith('.log'):
            self.compress_log(event.src_path)
    
    def compress_log(self, log_path):
        """Compress a log file"""
        log_file = Path(log_path)
        output = self.compress_dir / f"{log_file.name}.lsc"
        
        print(f"Compressing {log_file.name}...")
        stats = self.lp.compress_file(str(log_file), str(output))
        
        print(f"  ✓ Compressed: {stats['compression_ratio']:.1f}× ratio")
        print(f"  ✓ Saved: {stats['space_saved_mb']:.1f} MB")
        
        # Optionally delete original after compression
        # log_file.unlink()

def watch_log_directory(log_dir='logs', compress_dir='compressed'):
    """Watch log directory for new files"""
    event_handler = LogCompressionHandler(compress_dir)
    observer = Observer()
    observer.schedule(event_handler, log_dir, recursive=False)
    observer.start()
    
    print(f"Watching {log_dir}/ for new logs...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == '__main__':
    watch_log_directory()
```

Install watchdog: `pip install watchdog`

## Docker Integration

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install LogPress
RUN pip install --no-cache-dir LogPress

# Copy application code
COPY . .

# Volume for logs
VOLUME ["/logs", "/compressed"]

# Run compression service
CMD ["python", "compression_service.py"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  logpress:
    image: python:3.11-slim
    volumes:
      - ./logs:/logs
      - ./compressed:/compressed
    environment:
      - LOG_DIR=/logs
      - COMPRESS_DIR=/compressed
    command: |
      sh -c "pip install LogPress && python -c '
      from logpress import LogPress
      import glob
      
      lp = LogPress()
      for log in glob.glob(\"/logs/*.log\"):
          output = log.replace(\"/logs\", \"/compressed\").replace(\".log\", \".lsc\")
          stats = lp.compress_file(log, output)
          print(f\"{log}: {stats[\"compression_ratio\"]:.1f}×\")
      '"
```

## Kubernetes Deployment

### CronJob for Scheduled Compression

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: logpress-compress
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: logpress
            image: python:3.11-slim
            command:
            - /bin/sh
            - -c
            - |
              pip install LogPress
              python /scripts/compress_logs.py
            volumeMounts:
            - name: logs
              mountPath: /logs
            - name: compressed
              mountPath: /compressed
            - name: scripts
              mountPath: /scripts
          restartPolicy: OnFailure
          volumes:
          - name: logs
            persistentVolumeClaim:
              claimName: logs-pvc
          - name: compressed
            persistentVolumeClaim:
              claimName: compressed-pvc
          - name: scripts
            configMap:
              name: logpress-scripts
```

### ConfigMap with Compression Script

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: logpress-scripts
data:
  compress_logs.py: |
    from logpress import LogPress
    import glob
    import os
    
    lp = LogPress()
    log_dir = os.environ.get('LOG_DIR', '/logs')
    compress_dir = os.environ.get('COMPRESS_DIR', '/compressed')
    
    for log_file in glob.glob(f"{log_dir}/*.log"):
        filename = os.path.basename(log_file)
        output = f"{compress_dir}/{filename}.lsc"
        
        stats = lp.compress_file(log_file, output)
        print(f"{filename}: {stats['compression_ratio']:.1f}× ratio, saved {stats['space_saved_mb']:.1f} MB")
```

## AWS S3 Integration

```python
import boto3
from io import BytesIO
from logpress import LogPress

class S3LogCompressor:
    def __init__(self, bucket_name):
        self.s3 = boto3.client('s3')
        self.bucket = bucket_name
        self.lp = LogPress()
    
    def compress_s3_log(self, log_key, output_key=None):
        """Download log from S3, compress, upload back"""
        if output_key is None:
            output_key = log_key.replace('.log', '.lsc')
        
        # Download log
        print(f"Downloading s3://{self.bucket}/{log_key}")
        obj = self.s3.get_object(Bucket=self.bucket, Key=log_key)
        content = obj['Body'].read().decode()
        
        # Compress
        lines = content.splitlines()
        compressed, stats = self.lp.compress_lines(lines)
        
        # Upload compressed
        print(f"Uploading s3://{self.bucket}/{output_key}")
        self.s3.put_object(
            Bucket=self.bucket,
            Key=output_key,
            Body=compressed,
            ContentType='application/octet-stream'
        )
        
        # Optional: Delete original
        # self.s3.delete_object(Bucket=self.bucket, Key=log_key)
        
        return stats
    
    def query_s3_log(self, log_key, **filters):
        """Query compressed log from S3"""
        # Download compressed log
        obj = self.s3.get_object(Bucket=self.bucket, Key=log_key)
        compressed_data = obj['Body'].read()
        
        # Save temporarily
        temp_path = '/tmp/temp_compressed.lsc'
        with open(temp_path, 'wb') as f:
            f.write(compressed_data)
        
        # Query
        results = self.lp.query(temp_path, **filters)
        return results

# Usage
compressor = S3LogCompressor('my-logs-bucket')
stats = compressor.compress_s3_log('logs/2024/12/app.log')
print(f"Compressed: {stats['compression_ratio']:.1f}×")

errors = compressor.query_s3_log('logs/2024/12/app.lsc', severity='ERROR', limit=100)
```

## CI/CD Pipeline

### GitHub Actions

```yaml
name: Compress Logs

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:

jobs:
  compress:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install LogPress
      run: pip install LogPress
    
    - name: Compress logs
      run: |
        python -c "
        from logpress import LogPress
        import glob
        
        lp = LogPress()
        for log in glob.glob('logs/*.log'):
            output = log.replace('.log', '.lsc')
            stats = lp.compress_file(log, output)
            print(f'{log}: {stats[\"compression_ratio\"]:.1f}×')
        "
    
    - name: Upload compressed logs
      uses: actions/upload-artifact@v3
      with:
        name: compressed-logs
        path: logs/*.lsc
```

### GitLab CI

```yaml
compress_logs:
  image: python:3.11-slim
  stage: process
  script:
    - pip install LogPress
    - |
      python -c "
      from logpress import LogPress
      import glob
      
      lp = LogPress()
      for log in glob.glob('logs/*.log'):
          output = log.replace('.log', '.lsc')
          stats = lp.compress_file(log, output)
          print(f'{log}: {stats[\"compression_ratio\"]:.1f}×')
      "
  artifacts:
    paths:
      - logs/*.lsc
    expire_in: 30 days
  only:
    - schedules
```

## Performance Considerations

### Batch Processing

For large workloads:

```python
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from logpress import LogPress

def compress_file(log_path):
    """Compress a single file"""
    lp = LogPress()
    output = log_path.replace('.log', '.lsc')
    return lp.compress_file(log_path, output)

# Process files in parallel
log_files = list(Path('logs').glob('*.log'))

with ProcessPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(compress_file, [str(f) for f in log_files]))

for result in results:
    print(f"Compressed: {result['compression_ratio']:.1f}×")
```

### Memory Management

For very large files:

```python
from logpress import Compressor

def compress_large_file(input_path, output_path, batch_size=10000):
    """Compress file in batches to manage memory"""
    compressor = Compressor()
    
    with open(input_path, 'r') as f:
        batch = []
        for line in f:
            batch.append(line.strip())
            
            if len(batch) >= batch_size:
                compressor.process_batch(batch)
                batch = []
        
        # Process remaining
        if batch:
            compressor.process_batch(batch)
    
    # Save compressed
    compressor.save(output_path)
```

## Next Steps

- **Examples**: See [`examples/`](../examples/) for working code
- **API Reference**: [Complete API documentation](api_reference.md)
- **Performance**: [Tuning guide](performance_tuning.md)
