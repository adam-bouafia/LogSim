"""
Example 07: Flask REST API for Log Compression

Build a REST API for log compression and querying using Flask.

Endpoints:
- POST /compress - Upload and compress a log file
- GET /query - Query compressed logs
- GET /count - Get log count (metadata-only)
- GET /health - Health check

Use cases:
- Centralized log compression service
- Web-based log analysis tool
- Microservice for log management
- Integration with existing web applications

Requirements:
    pip install Flask flask-cors

Run:
    python 07_flask_api.py
    
Then test with:
    curl -X POST -F "file=@app.log" http://localhost:5000/compress
    curl "http://localhost:5000/query?file=app.lsc&severity=ERROR&limit=10"
"""

from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
from pathlib import Path
from typing import Dict, List
from logpress import LogPress

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['COMPRESSED_FOLDER'] = 'compressed'

# Create folders if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['COMPRESSED_FOLDER'], exist_ok=True)

# Initialize LogPress
lp = LogPress(min_support=3)


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    
    Returns:
        JSON with service status
    """
    return jsonify({
        'status': 'healthy',
        'service': 'LogPress API',
        'version': '1.0.0'
    })


@app.route('/compress', methods=['POST'])
def compress_logs():
    """
    Upload and compress a log file
    
    Request:
        - file: Log file (multipart/form-data)
        - min_support: (optional) Minimum logs per template
    
    Returns:
        JSON with compression statistics and download URL
    
    Example:
        curl -X POST -F "file=@app.log" http://localhost:5000/compress
    """
    # Check if file is in request
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    # Check if filename is empty
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400
    
    # Check file extension
    if not file.filename.endswith('.log'):
        return jsonify({'error': 'Only .log files are supported'}), 400
    
    try:
        # Secure the filename
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save uploaded file
        file.save(input_path)
        
        # Determine output filename
        output_filename = filename.replace('.log', '.lsc')
        output_path = os.path.join(app.config['COMPRESSED_FOLDER'], output_filename)
        
        # Get optional parameters
        min_support = request.form.get('min_support', 3, type=int)
        lp_custom = LogPress(min_support=min_support)
        
        # Compress the file
        stats = lp_custom.compress_file(input_path, output_path)
        
        # Clean up input file (optional)
        # os.remove(input_path)
        
        # Return results
        return jsonify({
            'success': True,
            'original_file': filename,
            'compressed_file': output_filename,
            'download_url': f'/download/{output_filename}',
            'statistics': {
                'original_size_mb': stats['original_size'] / (1024 * 1024),
                'compressed_size_mb': stats['compressed_size'] / (1024 * 1024),
                'compression_ratio': stats['compression_ratio'],
                'space_saved_mb': stats.get('space_saved_mb', 0),
                'template_count': stats.get('template_count', 0)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/query', methods=['GET'])
def query_logs():
    """
    Query compressed logs with filters
    
    Query Parameters:
        - file: Compressed file name (required)
        - severity: Filter by severity level
        - timestamp_after: Filter logs after timestamp
        - timestamp_before: Filter logs before timestamp
        - limit: Maximum results (default: 100)
    
    Returns:
        JSON with matching log entries
    
    Example:
        curl "http://localhost:5000/query?file=app.lsc&severity=ERROR&limit=10"
    """
    # Get required parameter
    filename = request.args.get('file')
    if not filename:
        return jsonify({'error': 'Missing required parameter: file'}), 400
    
    # Check file exists
    file_path = os.path.join(app.config['COMPRESSED_FOLDER'], secure_filename(filename))
    if not os.path.exists(file_path):
        return jsonify({'error': f'File not found: {filename}'}), 404
    
    try:
        # Get optional filter parameters
        severity = request.args.get('severity')
        timestamp_after = request.args.get('timestamp_after')
        timestamp_before = request.args.get('timestamp_before')
        limit = request.args.get('limit', 100, type=int)
        
        # Build filter dict
        filters = {'limit': limit}
        if severity:
            filters['severity'] = severity
        if timestamp_after:
            filters['timestamp_after'] = timestamp_after
        if timestamp_before:
            filters['timestamp_before'] = timestamp_before
        
        # Query compressed logs
        results = lp.query(file_path, **filters)
        
        return jsonify({
            'success': True,
            'file': filename,
            'filters': filters,
            'result_count': len(results),
            'logs': results
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/count', methods=['GET'])
def count_logs():
    """
    Count total logs in compressed file (metadata-only, fast!)
    
    Query Parameters:
        - file: Compressed file name (required)
    
    Returns:
        JSON with log count
    
    Example:
        curl "http://localhost:5000/count?file=app.lsc"
    """
    filename = request.args.get('file')
    if not filename:
        return jsonify({'error': 'Missing required parameter: file'}), 400
    
    file_path = os.path.join(app.config['COMPRESSED_FOLDER'], secure_filename(filename))
    if not os.path.exists(file_path):
        return jsonify({'error': f'File not found: {filename}'}), 404
    
    try:
        # Count logs (metadata-only)
        count = lp.count(file_path)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        return jsonify({
            'success': True,
            'file': filename,
            'total_logs': count,
            'file_size_mb': file_size / (1024 * 1024)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """
    Download compressed file
    
    Example:
        curl -O http://localhost:5000/download/app.lsc
    """
    file_path = os.path.join(app.config['COMPRESSED_FOLDER'], secure_filename(filename))
    
    if not os.path.exists(file_path):
        return jsonify({'error': f'File not found: {filename}'}), 404
    
    return send_file(file_path, as_attachment=True)


@app.route('/list', methods=['GET'])
def list_compressed_files():
    """
    List all compressed files
    
    Returns:
        JSON with list of compressed files
    
    Example:
        curl http://localhost:5000/list
    """
    try:
        files = []
        for filename in os.listdir(app.config['COMPRESSED_FOLDER']):
            if filename.endswith('.lsc'):
                file_path = os.path.join(app.config['COMPRESSED_FOLDER'], filename)
                file_size = os.path.getsize(file_path)
                
                files.append({
                    'filename': filename,
                    'size_mb': file_size / (1024 * 1024),
                    'download_url': f'/download/{filename}'
                })
        
        return jsonify({
            'success': True,
            'count': len(files),
            'files': files
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    """
    Delete a compressed file
    
    Example:
        curl -X DELETE http://localhost:5000/delete/app.lsc
    """
    file_path = os.path.join(app.config['COMPRESSED_FOLDER'], secure_filename(filename))
    
    if not os.path.exists(file_path):
        return jsonify({'error': f'File not found: {filename}'}), 404
    
    try:
        os.remove(file_path)
        return jsonify({
            'success': True,
            'message': f'Deleted {filename}'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({
        'error': 'File too large',
        'max_size_mb': app.config['MAX_CONTENT_LENGTH'] / (1024 * 1024)
    }), 413


@app.errorhandler(500)
def internal_server_error(error):
    """Handle internal server errors"""
    return jsonify({
        'error': 'Internal server error',
        'message': str(error)
    }), 500


def print_api_documentation():
    """Print API documentation on startup"""
    print("=" * 70)
    print("LogPress Flask API Server")
    print("=" * 70)
    print()
    print("Endpoints:")
    print("-" * 70)
    print("  GET  /health              - Health check")
    print("  POST /compress            - Upload and compress log file")
    print("  GET  /query               - Query compressed logs")
    print("  GET  /count               - Count logs (metadata-only)")
    print("  GET  /download/<file>     - Download compressed file")
    print("  GET  /list                - List all compressed files")
    print("  DELETE /delete/<file>     - Delete compressed file")
    print()
    print("Example Usage:")
    print("-" * 70)
    print("  # Compress a log file")
    print('  curl -X POST -F "file=@app.log" http://localhost:5000/compress')
    print()
    print("  # Query ERROR logs")
    print('  curl "http://localhost:5000/query?file=app.lsc&severity=ERROR&limit=10"')
    print()
    print("  # Count total logs")
    print('  curl "http://localhost:5000/count?file=app.lsc"')
    print()
    print("  # List all files")
    print('  curl http://localhost:5000/list')
    print()
    print("=" * 70)
    print()


if __name__ == '__main__':
    print_api_documentation()
    
    # Run the Flask app
    # In production, use a WSGI server like gunicorn:
    # gunicorn -w 4 -b 0.0.0.0:5000 07_flask_api:app
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True  # Set to False in production
    )
