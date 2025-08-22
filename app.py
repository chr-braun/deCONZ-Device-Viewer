#!/usr/bin/env python3
"""
deCONZ Device Viewer - Optimized Flask Application

A modern web application for viewing and monitoring Zigbee devices
from a deCONZ database with real-time updates and responsive design.
"""

import logging
import sqlite3
import socket
import sys
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
from threading import Lock
from typing import Dict, List, Optional, Any

from flask import Flask, render_template, jsonify, request, abort
from werkzeug.exceptions import InternalServerError

from config import config

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Flask application setup
app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['DEBUG'] = config.DEBUG

# Global cache and connection management
cache = {}
cache_lock = Lock()
db_lock = Lock()


class DatabaseManager:
    """Manages database connections and queries with connection pooling"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._connection = None
        
    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection with proper configuration"""
        if self._connection is None:
            try:
                self._connection = sqlite3.connect(
                    self.db_path,
                    check_same_thread=False,
                    timeout=10.0
                )
                self._connection.row_factory = sqlite3.Row
                logger.info(f"Connected to database: {self.db_path}")
            except sqlite3.Error as e:
                logger.error(f"Database connection failed: {e}")
                raise
        return self._connection
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a query with error handling and logging"""
        with db_lock:
            try:
                conn = self.get_connection()
                cursor = conn.execute(query, params)
                results = [dict(row) for row in cursor.fetchall()]
                logger.debug(f"Query executed successfully: {query[:50]}...")
                return results
            except sqlite3.Error as e:
                logger.error(f"Query execution failed: {e}")
                logger.error(f"Query: {query}")
                logger.error(f"Params: {params}")
                raise
    
    def close(self):
        """Close the database connection"""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("Database connection closed")


def cache_result(timeout: int = 300):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}_{hash(str(args) + str(kwargs))}"
            
            with cache_lock:
                # Check if cached result exists and is still valid
                if cache_key in cache:
                    cached_data, cached_time = cache[cache_key]
                    if datetime.now() - cached_time < timedelta(seconds=timeout):
                        logger.debug(f"Cache hit for {cache_key}")
                        return cached_data
                
                # Execute function and cache result
                try:
                    result = func(*args, **kwargs)
                    cache[cache_key] = (result, datetime.now())
                    logger.debug(f"Cache miss for {cache_key}, result cached")
                    return result
                except Exception as e:
                    logger.error(f"Function {func.__name__} failed: {e}")
                    raise
        
        return wrapper
    return decorator


def handle_errors(func):
    """Decorator for comprehensive error handling"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except sqlite3.Error as e:
            logger.error(f"Database error in {func.__name__}: {e}")
            error_msg = "Database connection error. Please check if deCONZ is running."
            if request.path.startswith('/api/'):
                return jsonify({'error': error_msg, 'type': 'database_error'}), 500
            return render_template('index.html', error=error_msg, devices=[])
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            error_msg = "An unexpected error occurred. Please try again."
            if request.path.startswith('/api/'):
                return jsonify({'error': error_msg, 'type': 'internal_error'}), 500
            return render_template('index.html', error=error_msg, devices=[])
    
    return wrapper


# Initialize database manager
try:
    db_manager = DatabaseManager(config.DB_PATH)
except Exception as e:
    logger.critical(f"Failed to initialize database manager: {e}")
    db_manager = None


@cache_result(timeout=config.CACHE_TIMEOUT)
def get_devices_from_db() -> List[Dict[str, Any]]:
    """Fetch device data from deCONZ database with enhanced information"""
    if not db_manager:
        raise RuntimeError("Database manager not initialized")
    
    # Enhanced query to get more device information
    query = """
    SELECT 
        d.id,
        d.name,
        d.type,
        d.manufacturername as manufacturer,
        d.modelid as model,
        d.swversion as software_version,
        d.lastseen,
        s.name as state_name,
        s.value as state_value
    FROM devices d
    LEFT JOIN device_states s ON d.id = s.device_id
    WHERE d.id IS NOT NULL
    ORDER BY d.lastseen DESC, d.id ASC
    LIMIT ?
    """
    
    try:
        results = db_manager.execute_query(query, (config.MAX_DEVICES,))
        
        # Process and enhance device data
        devices = {}
        for row in results:
            device_id = row['id']
            if device_id not in devices:
                devices[device_id] = {
                    'id': device_id,
                    'name': row['name'] or f'Device {device_id}',
                    'type': row['type'],
                    'manufacturer': row['manufacturer'],
                    'model': row['model'],
                    'software_version': row['software_version'],
                    'last_seen': format_timestamp(row['lastseen']),
                    'states': {}
                }
            
            # Add state information if available
            if row['state_name'] and row['state_value']:
                devices[device_id]['states'][row['state_name']] = row['state_value']
        
        device_list = list(devices.values())
        logger.info(f"Retrieved {len(device_list)} devices from database")
        return device_list
        
    except sqlite3.OperationalError:
        # Fallback to simpler query if advanced query fails
        logger.warning("Advanced query failed, falling back to simple query")
        simple_query = """
        SELECT id, name, type, manufacturername as manufacturer, 
               modelid as model, lastseen
        FROM devices 
        WHERE id IS NOT NULL
        ORDER BY lastseen DESC, id ASC
        LIMIT ?
        """
        
        results = db_manager.execute_query(simple_query, (config.MAX_DEVICES,))
        device_list = []
        for row in results:
            device_list.append({
                'id': row['id'],
                'name': row['name'] or f'Device {row["id"]}',
                'type': row['type'],
                'manufacturer': row['manufacturer'],
                'model': row['model'],
                'last_seen': format_timestamp(row['lastseen']),
                'states': {}
            })
        
        logger.info(f"Retrieved {len(device_list)} devices using fallback query")
        return device_list


def format_timestamp(timestamp: Optional[str]) -> Optional[str]:
    """Format timestamp for display"""
    if not timestamp:
        return None
    
    try:
        # Handle different timestamp formats
        if 'T' in timestamp:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        else:
            dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError) as e:
        logger.warning(f"Failed to format timestamp {timestamp}: {e}")
        return timestamp


def find_free_port(start: Optional[int] = None, end: Optional[int] = None) -> int:
    """Find a free port in the specified range with enhanced error handling"""
    start = start or config.PORT_START
    end = end or config.PORT_END
    
    logger.info(f"Searching for free port in range {start}-{end}")
    
    for port in range(start, end + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((config.HOST, port))
                logger.info(f"Found free port: {port}")
                return port
        except OSError as e:
            logger.debug(f"Port {port} is not available: {e}")
            continue
    
    raise RuntimeError(f"No free port available in range {start}-{end}")


# Web Routes
@app.route("/")
@handle_errors
def index():
    """Main page displaying device information"""
    logger.info("Index page requested")
    
    try:
        devices = get_devices_from_db()
        logger.info(f"Rendering index page with {len(devices)} devices")
        return render_template('index.html', devices=devices, error=None)
    except Exception as e:
        logger.error(f"Failed to load devices: {e}")
        error_msg = "Failed to load device data. Please check your deCONZ installation."
        return render_template('index.html', devices=[], error=error_msg)


# API Routes
@app.route("/api/devices")
@handle_errors
def api_devices():
    """API endpoint for device data"""
    logger.info("API devices endpoint requested")
    
    try:
        devices = get_devices_from_db()
        return jsonify({
            'devices': devices,
            'count': len(devices),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"API devices request failed: {e}")
        return jsonify({
            'error': 'Failed to retrieve device data',
            'type': 'api_error'
        }), 500


@app.route("/api/devices/<int:device_id>")
@handle_errors
def api_device_detail(device_id: int):
    """API endpoint for individual device details"""
    logger.info(f"API device detail requested for device {device_id}")
    
    try:
        devices = get_devices_from_db()
        device = next((d for d in devices if d['id'] == device_id), None)
        
        if not device:
            return jsonify({'error': 'Device not found'}), 404
        
        return jsonify(device)
    except Exception as e:
        logger.error(f"API device detail request failed: {e}")
        return jsonify({
            'error': 'Failed to retrieve device details',
            'type': 'api_error'
        }), 500


@app.route("/api/health")
def api_health():
    """Health check endpoint"""
    try:
        # Quick database connectivity check
        if db_manager:
            db_manager.execute_query("SELECT 1")
            db_status = "connected"
        else:
            db_status = "disconnected"
        
        return jsonify({
            'status': 'healthy',
            'database': db_status,
            'timestamp': datetime.now().isoformat(),
            'version': '2.0.0'
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 503


@app.route("/api/cache/clear", methods=['POST'])
def api_clear_cache():
    """Clear application cache"""
    global cache
    with cache_lock:
        cache.clear()
        logger.info("Application cache cleared")
    
    return jsonify({
        'message': 'Cache cleared successfully',
        'timestamp': datetime.now().isoformat()
    })


# Error handlers
@app.errorhandler(404)
def not_found(error):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Endpoint not found'}), 404
    return render_template('index.html', 
                         devices=[], 
                         error="Page not found"), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error'}), 500
    return render_template('index.html', 
                         devices=[], 
                         error="Internal server error"), 500


def validate_environment():
    """Validate the application environment and configuration"""
    logger.info("Validating application environment...")
    
    # Validate configuration
    config_errors = config.validate_config()
    if config_errors:
        for error in config_errors:
            logger.error(f"Configuration error: {error}")
        
        # Continue with warnings if only non-critical errors
        if any('Database file not found' in error for error in config_errors):
            logger.warning("Database file not found - application will work with limited functionality")
        else:
            logger.error("Critical configuration errors found")
            return False
    
    logger.info("Environment validation completed")
    return True


def cleanup():
    """Cleanup resources on application shutdown"""
    logger.info("Cleaning up application resources...")
    if db_manager:
        db_manager.close()
    logger.info("Cleanup completed")


if __name__ == "__main__":
    # Validate environment before starting
    if not validate_environment():
        logger.critical("Environment validation failed - exiting")
        sys.exit(1)
    
    try:
        port = find_free_port()
        logger.info(f"🚀 Starting optimized deCONZ Device Viewer on {config.HOST}:{port}")
        logger.info(f"Debug mode: {config.DEBUG}")
        logger.info(f"Database: {config.DB_PATH}")
        
        # Register cleanup handler
        import atexit
        atexit.register(cleanup)
        
        app.run(
            host=config.HOST, 
            port=port, 
            debug=config.DEBUG,
            threaded=True
        )
        
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
        cleanup()
    except Exception as e:
        logger.critical(f"Failed to start application: {e}")
        cleanup()
        sys.exit(1)

