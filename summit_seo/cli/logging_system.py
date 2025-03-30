"""Robust logging system for Summit SEO.

This module provides a comprehensive logging system for Summit SEO,
supporting various output formats, log levels, and destinations.
"""

import logging
import logging.config
import logging.handlers
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union, List

# Define custom log levels
TRACE = 5  # More detailed than DEBUG
logging.addLevelName(TRACE, "TRACE")

# Define log format constants
DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DETAILED_FORMAT = "%(asctime)s [%(process)d:%(thread)d] - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s"
MINIMAL_FORMAT = "%(levelname)s: %(message)s"
COLORED_FORMAT = "%(log_color)s%(levelname)-8s%(reset)s %(blue)s[%(name)s]%(reset)s %(message)s"


class SummitLogFilter(logging.Filter):
    """Filter for Summit SEO logs.
    
    Allows filtering log messages based on various criteria.
    """
    
    def __init__(self, name: str = "", include_modules: List[str] = None, exclude_modules: List[str] = None):
        """Initialize the filter.
        
        Args:
            name: Logger name to match.
            include_modules: List of module names to include.
            exclude_modules: List of module names to exclude.
        """
        super().__init__(name)
        self.include_modules = include_modules or []
        self.exclude_modules = exclude_modules or []
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Filter log records based on module name."""
        if self.include_modules and not any(record.name.startswith(mod) for mod in self.include_modules):
            return False
            
        if self.exclude_modules and any(record.name.startswith(mod) for mod in self.exclude_modules):
            return False
            
        return True


class SummitLogFormatter(logging.Formatter):
    """Enhanced log formatter for Summit SEO."""
    
    def __init__(self, fmt=None, datefmt=None, style='%', validate=True, **kwargs):
        """Initialize the formatter."""
        super().__init__(fmt, datefmt, style, validate, **kwargs)
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with enhanced information."""
        # Add timing information if not present
        if not hasattr(record, 'elapsed'):
            record.elapsed = time.time() - record.created
            
        # Add process and thread information if not present
        if not hasattr(record, 'processName'):
            record.processName = 'MainProcess' if record.process == os.getpid() else f'Process-{record.process}'
            
        return super().format(record)


class ColoredConsoleHandler(logging.StreamHandler):
    """A handler that adds color to console output."""
    
    COLORS = {
        'TRACE': '\033[37m',     # White
        'DEBUG': '\033[94m',     # Light blue
        'INFO': '\033[92m',      # Light green
        'WARNING': '\033[93m',   # Light yellow
        'ERROR': '\033[91m',     # Light red
        'CRITICAL': '\033[95m',  # Light magenta
        'RESET': '\033[0m',      # Reset
        'blue': '\033[34m',      # Blue
        'log_color': '',         # Set dynamically
        'reset': '\033[0m'       # Reset
    }
    
    def emit(self, record: logging.LogRecord) -> None:
        """Emit a colored log record."""
        # Set the log color based on level
        record.log_color = self.COLORS.get(record.levelname, '')
        record.blue = self.COLORS['blue']
        record.reset = self.COLORS['RESET']
        
        super().emit(record)


class LoggingSystem:
    """Comprehensive logging system for Summit SEO."""
    
    def __init__(self):
        """Initialize the logging system."""
        self.root_logger = logging.getLogger()
        self.configured = False
        self.log_directory = None
    
    def configure(
        self, 
        log_level: Union[int, str] = logging.INFO,
        console_output: bool = True,
        file_output: bool = False,
        log_directory: Optional[str] = None,
        log_format: str = DEFAULT_FORMAT,
        use_colors: bool = True,
        include_modules: List[str] = None,
        exclude_modules: List[str] = None,
        log_file_prefix: str = "summit_seo",
        max_file_size_mb: int = 10,
        backup_count: int = 5,
        syslog_output: bool = False,
        syslog_address: Optional[str] = None,
        propagate: bool = False
    ) -> None:
        """Configure the logging system.
        
        Args:
            log_level: Logging level (DEBUG, INFO, etc.).
            console_output: Whether to log to console.
            file_output: Whether to log to file.
            log_directory: Directory for log files.
            log_format: Format string for log messages.
            use_colors: Whether to use colors in console output.
            include_modules: List of module names to include.
            exclude_modules: List of module names to exclude.
            log_file_prefix: Prefix for log file names.
            max_file_size_mb: Maximum log file size in MB.
            backup_count: Number of backup log files to keep.
            syslog_output: Whether to log to syslog.
            syslog_address: Syslog server address.
            propagate: Whether to propagate logs to parent loggers.
        """
        # Convert string level to int if needed
        if isinstance(log_level, str):
            log_level = getattr(logging, log_level.upper(), logging.INFO)
        
        # Reset logging configuration
        logging.shutdown()
        self.root_logger.handlers.clear()
        
        # Set the base log level
        self.root_logger.setLevel(log_level)
        
        # Create handler filter
        log_filter = SummitLogFilter(
            include_modules=include_modules,
            exclude_modules=exclude_modules
        )
        
        # Configure console logging
        if console_output:
            if use_colors and sys.stdout.isatty():
                console_handler = ColoredConsoleHandler(sys.stdout)
                console_formatter = logging.Formatter(COLORED_FORMAT)
            else:
                console_handler = logging.StreamHandler(sys.stdout)
                console_formatter = logging.Formatter(log_format)
                
            console_handler.setFormatter(console_formatter)
            console_handler.addFilter(log_filter)
            self.root_logger.addHandler(console_handler)
        
        # Configure file logging
        if file_output:
            # Set up log directory
            if log_directory:
                self.log_directory = Path(log_directory)
            else:
                self.log_directory = Path.cwd() / "logs"
                
            self.log_directory.mkdir(exist_ok=True, parents=True)
            
            # Create rotating file handler for general logs
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file_path = self.log_directory / f"{log_file_prefix}_{timestamp}.log"
            
            file_handler = logging.handlers.RotatingFileHandler(
                filename=log_file_path,
                maxBytes=max_file_size_mb * 1024 * 1024,
                backupCount=backup_count,
                encoding='utf-8'
            )
            
            file_formatter = SummitLogFormatter(DETAILED_FORMAT)
            file_handler.setFormatter(file_formatter)
            file_handler.addFilter(log_filter)
            self.root_logger.addHandler(file_handler)
            
            # Create separate handler for errors (ERROR and above)
            error_log_path = self.log_directory / f"{log_file_prefix}_errors_{timestamp}.log"
            error_handler = logging.handlers.RotatingFileHandler(
                filename=error_log_path,
                maxBytes=max_file_size_mb * 1024 * 1024,
                backupCount=backup_count,
                encoding='utf-8'
            )
            
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(file_formatter)
            error_handler.addFilter(log_filter)
            self.root_logger.addHandler(error_handler)
        
        # Configure syslog logging
        if syslog_output:
            try:
                if syslog_address:
                    # Remote syslog
                    parts = syslog_address.split(':')
                    host = parts[0]
                    port = int(parts[1]) if len(parts) > 1 else 514
                    syslog_handler = logging.handlers.SysLogHandler(
                        address=(host, port)
                    )
                else:
                    # Local syslog
                    syslog_handler = logging.handlers.SysLogHandler()
                    
                syslog_formatter = logging.Formatter(MINIMAL_FORMAT)
                syslog_handler.setFormatter(syslog_formatter)
                syslog_handler.addFilter(log_filter)
                self.root_logger.addHandler(syslog_handler)
            except (OSError, ValueError) as e:
                # Fall back to console for syslog error message
                fallback = logging.StreamHandler(sys.stderr)
                fallback.setFormatter(logging.Formatter(MINIMAL_FORMAT))
                self.root_logger.addHandler(fallback)
                self.root_logger.error(f"Failed to set up syslog handler: {e}")
                self.root_logger.removeHandler(fallback)
        
        # Set configured flag
        self.configured = True
        
        # Log configuration complete
        logging.info(f"Logging system configured with level {logging.getLevelName(log_level)}")
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger with the specified name.
        
        Args:
            name: Logger name (usually __name__ of the module).
            
        Returns:
            A configured logger instance.
        """
        logger = logging.getLogger(name)
        
        # Add trace method
        def trace(msg, *args, **kwargs):
            logger.log(TRACE, msg, *args, **kwargs)
            
        logger.trace = trace
        
        return logger


# Create global instance
logging_system = LoggingSystem()


def configure_logging(config: Dict[str, Any] = None) -> None:
    """Configure the logging system with the provided config.
    
    Args:
        config: Dictionary with configuration options.
    """
    # Default config if none provided
    if config is None:
        config = {
            "log_level": "INFO",
            "console_output": True,
            "file_output": False
        }
        
    # Configure the logging system
    logging_system.configure(**config)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name.
    
    Args:
        name: Logger name (usually __name__ of the module).
        
    Returns:
        A configured logger instance.
    """
    return logging_system.get_logger(name)


# Apply default configuration
configure_logging() 