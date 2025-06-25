# Gunicorn configuration for Flask Workload Parser
# Based on official Gunicorn documentation: https://docs.gunicorn.org/en/stable/configure.html

import multiprocessing
import os

# Server socket configuration
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
# Flask documentation recommends CPU cores * 2 + 1 for sync workers
# Reference: https://flask.palletsprojects.com/en/stable/deploying/gunicorn/
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"  # Best for CPU-intensive workloads like pandas processing
worker_connections = 1000

# Timeouts - Extended for file processing operations
timeout = 300  # 5 minutes for large file uploads and processing
keepalive = 2

# Worker lifecycle management
# Helps prevent memory leaks in long-running processes
max_requests = 1000
max_requests_jitter = 50

# Logging configuration
# Reference: https://docs.gunicorn.org/en/stable/settings.html#logging
accesslog = "-"  # Log to stdout for container environments
errorlog = "-"   # Log to stderr for container environments
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming for monitoring
proc_name = 'flask-workload-parser'

# Server mechanics
daemon = False  # Don't daemonize in container environments
pidfile = '/tmp/gunicorn.pid'
user = None     # Let container handle user switching
group = None
tmp_upload_dir = None

# Security settings
# Reference: https://docs.gunicorn.org/en/stable/settings.html#security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Preload application for better memory usage
# Reference: https://docs.gunicorn.org/en/stable/settings.html#preload-app
preload_app = True

# Environment variables
raw_env = [
    'FLASK_ENV=production',
]

# Worker restart settings
max_worker_restart = 10
restart_worker_on_failure = True
