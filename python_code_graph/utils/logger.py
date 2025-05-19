import logging
import sys
from typing import Optional, Dict, Any

class Logger:
    """Simple logger for the code graph generator."""
    
    def __init__(self, name: str = "python-code-graph", level: int = logging.INFO):
        """
        Initialize the logger.
        
        Args:
            name: Logger name
            level: Logging level
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Add console handler if not already added
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            
    def set_level(self, level: int):
        """Set the logging level."""
        self.logger.setLevel(level)
        
    def debug(self, message: str, **kwargs):
        """Log a debug message."""
        self._log(logging.DEBUG, message, **kwargs)
        
    def info(self, message: str, **kwargs):
        """Log an info message."""
        self._log(logging.INFO, message, **kwargs)
        
    def warning(self, message: str, **kwargs):
        """Log a warning message."""
        self._log(logging.WARNING, message, **kwargs)
        
    def error(self, message: str, **kwargs):
        """Log an error message."""
        self._log(logging.ERROR, message, **kwargs)
        
    def _log(self, level: int, message: str, **kwargs):
        """Log a message with optional keyword arguments."""
        if kwargs:
            self.logger.log(level, f"{message} {kwargs}")
        else:
            self.logger.log(level, message)
            
# Create default logger
default_logger = Logger()

def get_logger():
    """Get the default logger."""
    return default_logger