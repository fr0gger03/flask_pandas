# Large File Upload Support Guide (10GB+)

This guide documents the implementation of 10GB file upload support for the Flask Workload Parser application. The changes enable handling of very large Excel files containing thousands of rows of workload data.

## Overview of Changes

The following components have been updated to support 10GB file uploads:

1. **Flask Configuration** - Updated MAX_CONTENT_LENGTH
2. **Gunicorn Configuration** - Extended timeouts and worker settings
3. **Nginx Configuration** - Optimized for large file uploads
4. **Docker Configuration** - Enhanced resource limits and volumes
5. **Data Processing** - Improved memory management for large files
6. **Form Validation** - Enhanced user experience with size indicators

## Configuration Changes

### 1. Flask Application (`parser/config.py`)

```python
# File upload configuration for large files (10GB)
MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 10737418240))  # 10GB default
SEND_FILE_MAX_AGE_DEFAULT = 0  # Disable caching for uploads
```

**Key Changes:**
- Set MAX_CONTENT_LENGTH to 10GB (10,737,418,240 bytes)
- Made configurable via environment variable
- Disabled file caching for better memory management

### 2. Gunicorn Configuration (`gunicorn.conf.py`)

```python
# Timeouts - Extended for large file uploads and processing (10GB files)
timeout = 3600  # 1 hour for very large file uploads and processing
```

**Key Changes:**
- Increased timeout from 5 minutes to 1 hour
- Maintained worker restart settings for memory management
- Enabled preload_app for better memory usage

### 3. Nginx Configuration (`nginx.conf`)

```nginx
# File upload configuration for 10GB files
client_max_body_size 10G;
client_body_timeout 3600s;    # 1 hour for upload
client_header_timeout 3600s;  # 1 hour for headers

# Buffer settings for large uploads
client_body_buffer_size 1M;
client_body_temp_path /tmp/nginx_upload;
```

**Key Changes:**
- Set client_max_body_size to 10G
- Extended all timeouts to 1 hour
- Optimized buffering for large files
- Disabled proxy buffering for upload endpoints
- Added specific configuration for upload routes

### 4. Docker Compose Configurations

#### Production with Nginx (`docker-compose.nginx.yml`)
```yaml
# Increased resource limits for large file processing
deploy:
  resources:
    limits:
      memory: 4G
      cpus: '2.0'
    reservations:
      memory: 1G
      cpus: '1.0'
```

**Key Changes:**
- Increased memory limit to 4GB for app container
- Added dedicated nginx service with upload optimization
- Shared volumes for temporary upload storage
- Enhanced health checks and monitoring

### 5. Environment Configuration

Created `.env.production.template` with:
```bash
# File Upload Configuration - 10GB Support
MAX_CONTENT_LENGTH=10737418240  # 10GB in bytes
UPLOAD_TIMEOUT=3600  # 1 hour
PANDAS_CHUNK_SIZE=10000
PANDAS_MAX_MEMORY=2048  # 2GB
```

## Data Processing Improvements

### Enhanced Data Validation (`parser/transform/data_validation.py`)

```python
def filetype_validation(input_path, fn):
    """Validate file type for Excel workbooks, optimized for large files."""
    # Check file size for logging
    file_path = Path(input_path) / fn
    if file_path.exists():
        file_size = file_path.stat().st_size
        print(f"File size: {file_size / 1024 / 1024:.2f} MB")
    
    # Use context manager for better memory management
    with pd.ExcelFile(os.path.join(input_path, fn)) as vmfile:
        # Processing logic...
```

**Key Improvements:**
- Added file size logging for monitoring
- Used context managers for better memory management
- Enhanced error handling for large files
- Added file information utility function

### Form Enhancements (`parser/forms.py`)

```python
class UploadFileForm(FlaskForm):
    file = FileField('Excel File (up to 10GB)', validators=[
        FileRequired(),
        FileAllowed(['xls', 'xlsx'], 'Excel files only! (.xls or .xlsx)')
    ], render_kw={
        "accept": ".xls,.xlsx",
        "class": "form-control-file",
        "id": "file-upload",
        "data-max-size": "10737418240"  # 10GB in bytes
    })
```

**Key Improvements:**
- Updated field label to indicate 10GB support
- Added client-side validation attributes
- Enhanced user experience with clear size limits

## Deployment Options

### Option 1: Production with Direct Gunicorn
```bash
docker compose -f docker-compose.production.yml --env-file .env.production up -d
```
- Direct access to Gunicorn on port 8000
- Good for simple deployments
- No nginx overhead

### Option 2: Production with Nginx (Recommended)
```bash
docker compose -f docker-compose.nginx.yml --env-file .env.production up -d
```
- Nginx reverse proxy on port 80
- Optimized for large file uploads
- Better performance and security
- SSL termination support

### Option 3: Development with Large File Testing
```bash
docker compose -f compose.yaml up -d
```
- Development environment with 10GB support
- Hot reload and debugging enabled

## Performance Considerations

### Memory Management
- **App Container**: 4GB memory limit for large file processing
- **Pandas Operations**: 2GB memory limit with chunking
- **Nginx Buffering**: Optimized for minimal memory usage
- **Temporary Storage**: Dedicated volumes for upload processing

### Processing Optimization
- **Chunked Reading**: Process large Excel files in chunks
- **Context Managers**: Proper resource cleanup
- **Worker Recycling**: Prevent memory leaks with max_requests
- **Connection Pooling**: Efficient database connections

### Storage Requirements
- **Upload Directory**: Persistent volume for temporary files
- **Database**: Separate volume for PostgreSQL data
- **Logs**: Dedicated volume for application and nginx logs
- **Temporary Files**: Shared volume for nginx upload processing

## File Size Limits

| Size | Bytes | Configuration |
|------|-------|---------------|
| 100MB | 104,857,600 | Previous default |
| 1GB | 1,073,741,824 | Small datasets |
| 5GB | 5,368,709,120 | Medium datasets |
| **10GB** | **10,737,418,240** | **Current default** |
| 20GB | 21,474,836,480 | Very large datasets |

## Monitoring and Troubleshooting

### Health Checks
All services include comprehensive health checks:
- **App**: HTTP health endpoint at `/health`
- **Database**: PostgreSQL ready check
- **Nginx**: HTTP availability check
- **Redis**: Ping response (if enabled)

### Log Monitoring
```bash
# Monitor all services
docker compose -f docker-compose.nginx.yml logs -f

# Monitor specific service
docker compose -f docker-compose.nginx.yml logs -f app
docker compose -f docker-compose.nginx.yml logs -f nginx

# Check upload progress
docker compose -f docker-compose.nginx.yml exec app tail -f /app/logs/flask.log
```

### Common Issues and Solutions

#### 1. 413 Request Entity Too Large
- **Cause**: Nginx or Flask file size limit exceeded
- **Solution**: Check MAX_CONTENT_LENGTH and client_max_body_size

#### 2. 504 Gateway Timeout
- **Cause**: Processing timeout during large file upload
- **Solution**: Increase proxy timeouts and Gunicorn timeout

#### 3. Out of Memory Errors
- **Cause**: Insufficient memory for large file processing
- **Solution**: Increase container memory limits or use chunked processing

#### 4. Disk Space Issues
- **Cause**: Large temporary files filling disk
- **Solution**: Monitor disk usage and configure cleanup policies

### Performance Monitoring
```bash
# Check resource usage
docker stats

# Monitor disk usage
docker system df

# Check volume usage
docker volume ls
docker volume inspect <volume_name>
```

## Security Considerations

### File Upload Security
- **File Type Validation**: Strict Excel file type checking
- **Size Limits**: Configurable maximum file sizes
- **Virus Scanning**: Consider integrating antivirus scanning
- **User Authentication**: Required for all upload operations

### Network Security
- **Container Isolation**: Services communicate via internal networks
- **Port Exposure**: Only necessary ports exposed externally
- **SSL/TLS**: HTTPS configuration templates provided
- **Security Headers**: Nginx configured with security headers

### Data Protection
- **Temporary File Cleanup**: Automatic cleanup after processing
- **Database Security**: Strong passwords and network isolation
- **Logging**: Comprehensive audit trails
- **Backup Strategy**: Regular database and volume backups

## Testing Large File Uploads

### Test File Creation
```bash
# Create test Excel file (if needed)
python -c "
import pandas as pd
import numpy as np

# Create large dataset
rows = 100000  # Adjust for desired file size
data = {
    'VM_Name': [f'vm-{i:06d}' for i in range(rows)],
    'vCPU': np.random.randint(1, 16, rows),
    'vRAM_MB': np.random.randint(512, 32768, rows),
    'Storage_GB': np.random.randint(10, 1000, rows),
    'OS': np.random.choice(['Windows', 'Linux', 'Other'], rows),
    'State': np.random.choice(['Running', 'Stopped'], rows)
}

df = pd.DataFrame(data)
df.to_excel('large_test_file.xlsx', index=False)
print(f'Created test file with {rows} rows')
"
```

### Upload Testing
```bash
# Test upload via curl
curl -X POST \
  -F "file=@large_test_file.xlsx" \
  -F "project_id=1" \
  http://localhost/upload

# Monitor upload progress
docker compose -f docker-compose.nginx.yml logs -f nginx
```

## Migration from Previous Version

### Steps to Enable 10GB Support

1. **Update Environment Variables**
   ```bash
   cp .env.production.template .env.production
   # Edit .env.production with your values
   ```

2. **Deploy with New Configuration**
   ```bash
   # Option A: With Nginx (recommended)
   docker compose -f docker-compose.nginx.yml --env-file .env.production up -d

   # Option B: Direct Gunicorn
   docker compose -f docker-compose.production.yml --env-file .env.production up -d
   ```

3. **Verify Configuration**
   ```bash
   # Check file size limits
   curl -I http://localhost/health
   
   # Test upload endpoint
   curl -X OPTIONS http://localhost/upload
   ```

4. **Monitor Initial Deployment**
   ```bash
   docker compose logs -f
   docker stats
   ```

### Rollback Plan
If issues occur, rollback to previous configuration:
```bash
# Stop services
docker compose down

# Use previous compose file
docker compose -f docker-compose.production.yml up -d

# Restore previous environment
# (restore from backup)
```

## Future Enhancements

### Possible Improvements
- **Streaming Uploads**: Implement chunked upload for better UX
- **Progress Indicators**: Real-time upload progress
- **Compression**: Support for compressed Excel files
- **Parallel Processing**: Multi-threaded file processing
- **Caching**: Redis-based caching for processed data
- **File Validation**: Enhanced content validation

### Scaling Considerations
- **Load Balancing**: Multiple app instances behind nginx
- **Database Scaling**: Read replicas for large datasets
- **Storage Scaling**: Network-attached storage for uploads
- **CDN Integration**: Content delivery for static assets

This implementation provides a robust foundation for handling large file uploads while maintaining security, performance, and scalability.
