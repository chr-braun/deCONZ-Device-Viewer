import os
from pathlib import Path

# Configuration management with environment variable support
class Config:
    """Configuration class for deCONZ Device Viewer"""
    
    # Database configuration
    DB_PATH = os.environ.get('DECONZ_DB_PATH', 
                            str(Path.home() / '.local/share/deCONZ/zll.db'))
    
    # Flask configuration
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Server configuration
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT_START = int(os.environ.get('PORT_START', '8500'))
    PORT_END = int(os.environ.get('PORT_END', '8600'))
    
    # Application settings
    MAX_DEVICES = int(os.environ.get('MAX_DEVICES', '50'))
    CACHE_TIMEOUT = int(os.environ.get('CACHE_TIMEOUT', '300'))  # 5 minutes
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'deconz_viewer.log')
    
    @classmethod
    def validate_config(cls):
        """Validate configuration settings"""
        errors = []
        
        # Check if database path exists
        db_path = Path(cls.DB_PATH)
        if not db_path.exists():
            errors.append(f"Database file not found: {cls.DB_PATH}")
        elif not db_path.is_file():
            errors.append(f"Database path is not a file: {cls.DB_PATH}")
        
        # Validate port range
        if cls.PORT_START >= cls.PORT_END:
            errors.append("PORT_START must be less than PORT_END")
        
        # Validate numeric settings
        if cls.MAX_DEVICES <= 0:
            errors.append("MAX_DEVICES must be a positive integer")
        
        if cls.CACHE_TIMEOUT < 0:
            errors.append("CACHE_TIMEOUT must be non-negative")
        
        return errors

# Create configuration instance
config = Config()

