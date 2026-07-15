"""
Logging utility module for MLB Data Pipeline.

This module provides centralized logging configuration with support for both
console and file output in standard and JSON formats.

Author: Data Engineering Team
Date: 2026-07-15
"""

import json
import logging
import logging.handlers
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    
    Converts log records to JSON format for easier parsing and analysis.
    Includes timestamp, log level, logger name, message, and additional context.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format a log record as JSON string.
        
        Args:
            record: LogRecord instance to format.
            
        Returns:
            JSON-formatted string representation of the log record.
        """
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add any extra fields from LogRecord
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)
        
        return json.dumps(log_data, default=str)


class StandardFormatter(logging.Formatter):
    """
    Custom standard formatter for human-readable logging.
    
    Provides clear, readable output with colors for console output.
    """

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",      # Cyan
        "INFO": "\033[32m",       # Green
        "WARNING": "\033[33m",    # Yellow
        "ERROR": "\033[31m",      # Red
        "CRITICAL": "\033[41m",   # Red background
        "RESET": "\033[0m",       # Reset
    }

    def format(self, record: logging.LogRecord) -> str:
        """
        Format a log record in standard human-readable format.
        
        Args:
            record: LogRecord instance to format.
            
        Returns:
            Formatted string with optional color codes.
        """
        # Check if output is to console (for color coding)
        use_color = hasattr(sys.stderr, "isatty") and sys.stderr.isatty()
        
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
        
        if use_color:
            level_color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
            level_str = f"{level_color}{record.levelname}{self.COLORS['RESET']}"
        else:
            level_str = record.levelname
        
        message = record.getMessage()
        
        # Format base message
        log_str = f"[{timestamp}] {level_str:>10} | {record.name:20} | {message}"
        
        # Add exception info if present
        if record.exc_info:
            log_str += f"\n{self.formatException(record.exc_info)}"
        
        return log_str


def setup_logger(
    name: str,
    log_dir: str = "logs",
    level: str = "INFO",
    format_type: str = "standard",
    console_output: bool = True,
    file_output: bool = True,
    max_bytes: int = 10485760,  # 10MB
    backup_count: int = 5,
) -> logging.Logger:
    """
    Set up a configured logger instance.
    
    Creates a logger with both console and file handlers. Supports both
    standard and JSON formatting. File output uses rotating file handler
    to prevent log files from becoming too large.
    
    Args:
        name: Logger name (typically __name__).
        log_dir: Directory to store log files. Defaults to "logs".
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        format_type: Format type - "standard" or "json".
        console_output: Whether to output to console. Defaults to True.
        file_output: Whether to output to file. Defaults to True.
        max_bytes: Maximum bytes per log file before rotation.
        backup_count: Number of backup log files to keep.
        
    Returns:
        Configured logger instance.
        
    Example:
        >>> logger = setup_logger(__name__, level="DEBUG")
        >>> logger.info("Application started")
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Choose formatter
    if format_type.lower() == "json":
        formatter = JSONFormatter()
    else:
        formatter = StandardFormatter()
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler with rotation
    if file_output:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        
        log_file = log_path / f"{name.replace('.', '_')}.log"
        
        # Use rotating file handler to manage log file size
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
        )
        file_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Prevent propagation to avoid duplicate logs
    logger.propagate = False
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger instance.
    
    Convenience function to get a logger by name. If logger hasn't been
    configured with setup_logger(), returns a basic configured logger.
    
    Args:
        name: Logger name (typically __name__).
        
    Returns:
        Logger instance.
    """
    logger = logging.getLogger(name)
    
    # If logger has no handlers, set up basic configuration
    if not logger.handlers:
        logger = setup_logger(name)
    
    return logger


def log_execution_time(logger: logging.Logger, operation: str):
    """
    Decorator to log function execution time.
    
    Logs the start, end, and duration of function execution.
    Useful for performance monitoring.
    
    Args:
        logger: Logger instance.
        operation: Description of the operation being performed.
        
    Example:
        >>> @log_execution_time(logger, "Data extraction")
        >>> def extract_data():
        >>>     pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.info(f"Starting: {operation}")
            import time
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"Completed: {operation} (Duration: {duration:.2f}s)")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"Failed: {operation} (Duration: {duration:.2f}s) - Error: {str(e)}",
                    exc_info=True
                )
                raise
        
        return wrapper
    return decorator


# Module-level logger initialization
if __name__ != "__main__":
    # Set up root logger for the module
    _module_logger = setup_logger(
        name="statsbomb_mlb",
        log_dir="logs",
        level="INFO",
        format_type="standard",
        console_output=True,
        file_output=True,
    )
