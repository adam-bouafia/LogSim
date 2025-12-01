"""
Example 08: FastAPI Async Service for Log Compression

Build a production-ready async REST API using FastAPI with:
- Automatic OpenAPI documentation (Swagger UI)
- Type hints and validation
- Async file handling
- Background tasks
- Streaming uploads

Endpoints:
- POST /compress - Upload and compress a log file
- GET /query - Query compressed logs with filters
- GET /count - Get log count (metadata-only)
- GET /stats/{file} - Get file statistics
- GET /health - Health check
- GET /docs - Interactive API documentation (Swagger UI)

Requirements:
    pip install fastapi uvicorn python-multipart aiofiles

Run:
    python 08_fastapi_service.py
    
    Or with uvicorn directly:
    uvicorn 08_fastapi_service:app --reload --host 0.0.0.0 --port 8000

Then visit:
    - API: http://localhost:8000
    - Docs: http://localhost:8000/docs
    - Alternative docs: http://localhost:8000/redoc
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Query, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import os
import aiofiles
from pathlib import Path
import time
from logpress import LogPress

# Initialize FastAPI app
app = FastAPI(
    title="LogPress API",
    description="Semantic log compression and querying service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
UPLOAD_FOLDER = "uploads"
COMPRESSED_FOLDER = "compressed"
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# Create folders
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(COMPRESSED_FOLDER, exist_ok=True)

# Initialize LogPress
lp = LogPress(min_support=3)


# Pydantic models for request/response validation
class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    uptime_seconds: float


class CompressionStats(BaseModel):
    original_size_mb: float
    compressed_size_mb: float
    compression_ratio: float
    space_saved_mb: float
    template_count: int


class CompressionResponse(BaseModel):
    success: bool
    original_file: str
    compressed_file: str
    download_url: str
    statistics: CompressionStats


class QueryResponse(BaseModel):
    success: bool
    file: str
    filters: Dict[str, Any]
    result_count: int
    logs: List[Dict[str, Any]]


class CountResponse(BaseModel):
    success: bool
    file: str
    total_logs: int
    file_size_mb: float


class FileInfo(BaseModel):
    filename: str
    size_mb: float
    download_url: str
    created_at: Optional[float] = None


class ListResponse(BaseModel):
    success: bool
    count: int
    files: List[FileInfo]


# Startup event
start_time = time.time()


@app.on_event("startup")
async def startup_event():
    """Initialize service on startup"""
    print("=" * 70)
    print("LogPress FastAPI Service Started")
    print("=" * 70)
    print(f"Docs: http://localhost:8000/docs")
    print(f"Alternative docs: http://localhost:8000/redoc")
    print("=" * 70)


@app.get("/", tags=["General"])
async def root():
    """Root endpoint with API information"""
    return {
        "service": "LogPress API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "compress": "POST /compress",
            "query": "GET /query",
            "count": "GET /count",
            "list": "GET /list"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """
    Health check endpoint
    
    Returns service status and uptime
    """
    return HealthResponse(
        status="healthy",
        service="LogPress API",
        version="1.0.0",
        uptime_seconds=time.time() - start_time
    )


@app.post("/compress", response_model=CompressionResponse, tags=["Compression"])
async def compress_logs(
    file: UploadFile = File(..., description="Log file to compress (.log)"),
    min_support: int = Query(3, ge=1, le=100, description="Minimum logs per template"),
    background_tasks: BackgroundTasks = None
):
    """
    Upload and compress a log file
    
    - **file**: Log file to compress (must be .log extension)
    - **min_support**: Minimum number of logs required to create a template (1-100)
    
    Returns compression statistics and download URL
    """
    # Validate file extension
    if not file.filename.endswith('.log'):
        raise HTTPException(
            status_code=400,
            detail="Only .log files are supported"
        )
    
    # Secure filename
    filename = Path(file.filename).name
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    
    try:
        # Save uploaded file asynchronously
        async with aiofiles.open(input_path, 'wb') as f:
            content = await file.read()
            
            # Check file size
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Max size: {MAX_FILE_SIZE / (1024*1024):.0f}MB"
                )
            
            await f.write(content)
        
        # Determine output filename
        output_filename = filename.replace('.log', '.lsc')
        output_path = os.path.join(COMPRESSED_FOLDER, output_filename)
        
        # Compress the file (CPU-bound, runs in thread pool)
        lp_custom = LogPress(min_support=min_support)
        stats = lp_custom.compress_file(input_path, output_path)
        
        # Schedule cleanup of input file in background
        if background_tasks:
            background_tasks.add_task(os.remove, input_path)
        
        # Return response
        return CompressionResponse(
            success=True,
            original_file=filename,
            compressed_file=output_filename,
            download_url=f"/download/{output_filename}",
            statistics=CompressionStats(
                original_size_mb=stats['original_size'] / (1024 * 1024),
                compressed_size_mb=stats['compressed_size'] / (1024 * 1024),
                compression_ratio=stats['compression_ratio'],
                space_saved_mb=stats.get('space_saved_mb', 0),
                template_count=stats.get('template_count', 0)
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Cleanup on error
        if os.path.exists(input_path):
            os.remove(input_path)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/query", response_model=QueryResponse, tags=["Querying"])
async def query_logs(
    file: str = Query(..., description="Compressed file name (e.g., app.lsc)"),
    severity: Optional[str] = Query(None, description="Filter by severity level (e.g., ERROR, WARN)"),
    timestamp_after: Optional[str] = Query(None, description="Filter logs after this timestamp"),
    timestamp_before: Optional[str] = Query(None, description="Filter logs before this timestamp"),
    limit: int = Query(100, ge=1, le=10000, description="Maximum results to return")
):
    """
    Query compressed logs with filters
    
    - **file**: Compressed file name (required)
    - **severity**: Filter by severity level (optional)
    - **timestamp_after**: Filter logs after timestamp (optional)
    - **timestamp_before**: Filter logs before timestamp (optional)
    - **limit**: Maximum results (1-10000, default: 100)
    
    Returns matching log entries
    """
    # Check file exists
    file_path = os.path.join(COMPRESSED_FOLDER, Path(file).name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File not found: {file}")
    
    try:
        # Build filter dict
        filters = {'limit': limit}
        if severity:
            filters['severity'] = severity
        if timestamp_after:
            filters['timestamp_after'] = timestamp_after
        if timestamp_before:
            filters['timestamp_before'] = timestamp_before
        
        # Query compressed logs (CPU-bound, runs in thread pool)
        results = lp.query(file_path, **filters)
        
        return QueryResponse(
            success=True,
            file=file,
            filters=filters,
            result_count=len(results),
            logs=results
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/count", response_model=CountResponse, tags=["Querying"])
async def count_logs(
    file: str = Query(..., description="Compressed file name (e.g., app.lsc)")
):
    """
    Count total logs in compressed file (metadata-only, very fast!)
    
    - **file**: Compressed file name (required)
    
    Returns total log count without decompression
    """
    file_path = os.path.join(COMPRESSED_FOLDER, Path(file).name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File not found: {file}")
    
    try:
        # Count logs (metadata-only)
        count = lp.count(file_path)
        file_size = os.path.getsize(file_path)
        
        return CountResponse(
            success=True,
            file=file,
            total_logs=count,
            file_size_mb=file_size / (1024 * 1024)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download/{filename}", tags=["Files"])
async def download_file(filename: str):
    """
    Download compressed file
    
    - **filename**: Name of the compressed file
    """
    file_path = os.path.join(COMPRESSED_FOLDER, Path(filename).name)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File not found: {filename}")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )


@app.get("/list", response_model=ListResponse, tags=["Files"])
async def list_compressed_files():
    """
    List all compressed files
    
    Returns list of all compressed files with metadata
    """
    try:
        files = []
        for filename in os.listdir(COMPRESSED_FOLDER):
            if filename.endswith('.lsc'):
                file_path = os.path.join(COMPRESSED_FOLDER, filename)
                file_size = os.path.getsize(file_path)
                created_at = os.path.getctime(file_path)
                
                files.append(FileInfo(
                    filename=filename,
                    size_mb=file_size / (1024 * 1024),
                    download_url=f"/download/{filename}",
                    created_at=created_at
                ))
        
        # Sort by creation time (newest first)
        files.sort(key=lambda x: x.created_at or 0, reverse=True)
        
        return ListResponse(
            success=True,
            count=len(files),
            files=files
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/delete/{filename}", tags=["Files"])
async def delete_file(filename: str):
    """
    Delete a compressed file
    
    - **filename**: Name of the file to delete
    """
    file_path = os.path.join(COMPRESSED_FOLDER, Path(filename).name)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File not found: {filename}")
    
    try:
        os.remove(file_path)
        return {
            "success": True,
            "message": f"Deleted {filename}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats/{filename}", tags=["Files"])
async def get_file_stats(filename: str):
    """
    Get detailed statistics for a compressed file
    
    - **filename**: Name of the compressed file
    """
    file_path = os.path.join(COMPRESSED_FOLDER, Path(filename).name)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File not found: {filename}")
    
    try:
        file_size = os.path.getsize(file_path)
        created_at = os.path.getctime(file_path)
        modified_at = os.path.getmtime(file_path)
        
        # Get log count
        count = lp.count(file_path)
        
        return {
            "success": True,
            "filename": filename,
            "size_bytes": file_size,
            "size_mb": file_size / (1024 * 1024),
            "total_logs": count,
            "created_at": created_at,
            "modified_at": modified_at
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 70)
    print("Starting LogPress FastAPI Service")
    print("=" * 70)
    print()
    print("API will be available at:")
    print("  • http://localhost:8000")
    print("  • http://localhost:8000/docs (Swagger UI)")
    print("  • http://localhost:8000/redoc (ReDoc)")
    print()
    print("Press CTRL+C to stop")
    print("=" * 70)
    print()
    
    # Run with uvicorn
    uvicorn.run(
        "08_fastapi_service:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes (dev only)
        log_level="info"
    )
