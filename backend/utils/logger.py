import logging
import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any

try:
    import watchtower
    CLOUDWATCH_AVAILABLE = True
except ImportError:
    CLOUDWATCH_AVAILABLE = False

def setup_logging(
    log_level: str = None,
    enable_cloudwatch: bool = None,
    log_group: str = '/aws/lambda/news-intelligence-lambda',
    stream_name: str = None
) -> logging.Logger:
    """
    Setup logging configuration for the news intelligence system
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_cloudwatch: Whether to enable CloudWatch logging
        log_group: CloudWatch log group name
        stream_name: CloudWatch stream name (defaults to timestamp)
        
    Returns:
        Configured logger instance
    """
    # Get configuration from environment if not provided
    if log_level is None:
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    if enable_cloudwatch is None:
        enable_cloudwatch = os.getenv('ENABLE_CLOUDWATCH', 'true').lower() == 'true'
    
    if stream_name is None:
        stream_name = f"news-intelligence-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
    
    # Create logger
    logger = logging.getLogger('news-intelligence')
    logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # CloudWatch handler (if available and enabled)
    if enable_cloudwatch and CLOUDWATCH_AVAILABLE:
        try:
            cloudwatch_handler = watchtower.CloudWatchLogHandler(
                log_group=log_group,
                stream_name=stream_name,
                use_queues=True,
                send_interval=5,
                max_batch_size=1000
            )
            cloudwatch_handler.setFormatter(formatter)
            logger.addHandler(cloudwatch_handler)
            logger.info("CloudWatch logging enabled")
        except Exception as e:
            logger.warning(f"CloudWatch logging failed to initialize: {e}")
    elif enable_cloudwatch and not CLOUDWATCH_AVAILABLE:
        logger.warning("CloudWatch logging requested but watchtower not available")
    
    logger.info(f"Logging initialized at level {log_level}")
    return logger

def setup_lambda_logging():
    """Setup logging specifically for AWS Lambda environment"""
    return setup_logging(
        log_level=os.getenv('LOG_LEVEL', 'INFO'),
        enable_cloudwatch=True,
        log_group='/aws/lambda/news-intelligence-lambda'
    )

def log_request(logger: logging.Logger, event: Dict[str, Any], context: Any):
    """Log Lambda request information"""
    logger.info("Lambda request started", extra={
        'request_id': getattr(context, 'aws_request_id', 'local'),
        'function_name': getattr(context, 'function_name', 'news-intelligence-lambda'),
        'function_version': getattr(context, 'function_version', '$LATEST'),
        'memory_limit': getattr(context, 'memory_limit_in_mb', 'unknown'),
        'remaining_time': getattr(context, 'get_remaining_time_in_millis', lambda: 0)()
    })
    
    # Log event (be careful about sensitive data)
    safe_event = sanitize_event_for_logging(event)
    logger.debug(f"Event: {safe_event}")

def log_response(logger: logging.Logger, response: Dict[str, Any], context: Any):
    """Log Lambda response information"""
    logger.info("Lambda request completed", extra={
        'request_id': getattr(context, 'aws_request_id', 'local'),
        'status_code': response.get('statusCode', 'unknown'),
        'response_size': len(response.get('body', ''))
    })

def sanitize_event_for_logging(event: Dict[str, Any]) -> Dict[str, Any]:
    """Remove sensitive information from event for logging"""
    safe_event = event.copy()
    
    # Remove API keys and sensitive data
    sensitive_keys = ['api_key', 'apiKey', 'token', 'password', 'secret', 'key']
    
    def sanitize_dict(data: Any) -> Any:
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                if any(sensitive in key.lower() for sensitive in sensitive_keys):
                    sanitized[key] = '***REDACTED***'
                else:
                    sanitized[key] = sanitize_dict(value)
            return sanitized
        elif isinstance(data, list):
            return [sanitize_dict(item) for item in data]
        else:
            return data
    
    return sanitize_dict(safe_event)

def log_error(logger: logging.Logger, error: Exception, context: Any, event: Dict[str, Any] = None):
    """Log error with context"""
    error_info = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        'request_id': getattr(context, 'aws_request_id', 'local'),
        'function_name': getattr(context, 'function_name', 'news-intelligence-lambda')
    }
    
    if event:
        safe_event = sanitize_event_for_logging(event)
        error_info['event'] = safe_event
    
    logger.error(f"Error occurred: {error}", extra=error_info, exc_info=True)

def log_performance(logger: logging.Logger, operation: str, duration: float, metadata: Dict[str, Any] = None):
    """Log performance metrics"""
    perf_info = {
        'operation': operation,
        'duration_ms': duration * 1000,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if metadata:
        perf_info.update(metadata)
    
    logger.info(f"Performance: {operation} completed in {duration:.3f}s", extra=perf_info)

def create_performance_logger(logger: logging.Logger):
    """Create a performance logger context manager"""
    import time
    
    class PerformanceLogger:
        def __init__(self, operation: str, metadata: Dict[str, Any] = None):
            self.operation = operation
            self.metadata = metadata or {}
            self.start_time = None
        
        def __enter__(self):
            self.start_time = time.time()
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            if self.start_time:
                duration = time.time() - self.start_time
                if exc_type is None:
                    log_performance(logger, self.operation, duration, self.metadata)
                else:
                    logger.error(f"Performance: {self.operation} failed after {duration:.3f}s", extra={
                        'operation': self.operation,
                        'duration_ms': duration * 1000,
                        'error': str(exc_val),
                        'error_type': exc_type.__name__
                    })
    
    return PerformanceLogger

class StructuredLogger:
    """Structured logging wrapper for consistent log formatting"""
    
    def __init__(self, logger: logging.Logger, component: str):
        self.logger = logger
        self.component = component
    
    def info(self, message: str, **kwargs):
        """Log info message with component context"""
        self.logger.info(message, extra={'component': self.component, **kwargs})
    
    def warning(self, message: str, **kwargs):
        """Log warning message with component context"""
        self.logger.warning(message, extra={'component': self.component, **kwargs})
    
    def error(self, message: str, error: Exception = None, **kwargs):
        """Log error message with component context"""
        extra = {'component': self.component, **kwargs}
        if error:
            extra['error_type'] = type(error).__name__
            extra['error_message'] = str(error)
        self.logger.error(message, extra=extra, exc_info=True)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with component context"""
        self.logger.debug(message, extra={'component': self.component, **kwargs})
    
    def performance(self, operation: str, duration: float, **kwargs):
        """Log performance metrics"""
        log_performance(self.logger, operation, duration, {
            'component': self.component,
            **kwargs
        })

# Global logger instance
_global_logger = None

def get_logger(name: str = 'news-intelligence') -> logging.Logger:
    """Get the global logger instance"""
    global _global_logger
    if _global_logger is None:
        _global_logger = setup_logging()
    return _global_logger

def get_structured_logger(component: str, name: str = 'news-intelligence') -> StructuredLogger:
    """Get a structured logger for a specific component"""
    logger = get_logger(name)
    return StructuredLogger(logger, component)

if __name__ == "__main__":
    # Test logging setup
    logger = setup_logging(log_level='DEBUG')
    
    # Test basic logging
    logger.info("Testing basic logging")
    logger.debug("Debug message")
    logger.warning("Warning message")
    logger.error("Error message")
    
    # Test structured logger
    structured = get_structured_logger('test-component')
    structured.info("Structured info message")
    structured.error("Structured error message")
    
    # Test performance logging
    import time
    time.sleep(0.1)
    structured.performance('test_operation', 0.1, metadata={'test': 'value'})
    
    # Test performance context manager
    perf_logger = create_performance_logger(logger)
    with perf_logger('test_operation_with_context', {'context': 'test'}):
        time.sleep(0.05)
    
    print("Logging test completed")