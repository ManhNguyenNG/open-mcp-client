"""
Error handling and resilience module for AWS Bedrock integration.
Handles retry logic, error categorization, and user-friendly error messages.
"""

import time
import random
import logging
from typing import Optional, Callable, Any
from functools import wraps

logger = logging.getLogger(__name__)

class BedrockError(Exception):
    """Base exception for Bedrock-related errors."""
    pass

class BedrockThrottlingError(BedrockError):
    """Exception raised when Bedrock returns throttling error."""
    pass

class BedrockPermissionError(BedrockError):
    """Exception raised when Bedrock returns permission error."""
    pass

class BedrockValidationError(BedrockError):
    """Exception raised when Bedrock returns validation error."""
    pass

class BedrockTimeoutError(BedrockError):
    """Exception raised when Bedrock request times out."""
    pass

def categorize_bedrock_error(error: Exception) -> BedrockError:
    """
    Categorize AWS/Bedrock errors into user-friendly exceptions.
    
    Args:
        error: The original exception from boto3/bedrock
        
    Returns:
        BedrockError: Categorized exception with user-friendly message
    """
    error_str = str(error).lower()
    
    # Throttling errors
    if any(keyword in error_str for keyword in ["throttling", "rate exceeded", "too many requests"]):
        return BedrockThrottlingError(
            "Request rate exceeded. Please wait a moment and try again. "
            "If this persists, consider reducing request frequency."
        )
    
    # Permission errors
    if any(keyword in error_str for keyword in ["access denied", "unauthorized", "forbidden", "permission"]):
        return BedrockPermissionError(
            "Access denied. Please check your AWS credentials and permissions. "
            "Ensure your IAM role/user has Bedrock access permissions."
        )
    
    # Validation errors
    if any(keyword in error_str for keyword in ["validation", "invalid", "bad request"]):
        return BedrockValidationError(
            "Invalid request parameters. Please check your model ID, region, and request format."
        )
    
    # Timeout errors
    if any(keyword in error_str for keyword in ["timeout", "timed out"]):
        return BedrockTimeoutError(
            "Request timed out. Please try again. If this persists, the service may be experiencing high load."
        )
    
    # Generic error
    return BedrockError(f"Bedrock service error: {error}")

def exponential_backoff_with_jitter(
    max_retries: int = 3,
    base_delay: float = 0.25,
    max_delay: float = 2.0,
    jitter_factor: float = 0.1
) -> Callable:
    """
    Decorator for exponential backoff with jitter.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        jitter_factor: Jitter factor (0.0 to 1.0)
        
    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                    
                except Exception as e:
                    last_exception = e
                    
                    # Don't retry on the last attempt
                    if attempt == max_retries:
                        break
                    
                    # Categorize the error
                    categorized_error = categorize_bedrock_error(e)
                    
                    # Only retry on throttling errors
                    if not isinstance(categorized_error, BedrockThrottlingError):
                        logger.warning(f"Non-retriable error on attempt {attempt + 1}: {categorized_error}")
                        raise categorized_error
                    
                    # Calculate delay with exponential backoff and jitter
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    jitter = delay * jitter_factor * random.random()
                    total_delay = delay + jitter
                    
                    logger.warning(
                        f"Throttling error on attempt {attempt + 1}/{max_retries + 1}, "
                        f"retrying in {total_delay:.2f}s: {categorized_error}"
                    )
                    
                    time.sleep(total_delay)
            
            # If we get here, all retries failed
            logger.error(f"All {max_retries + 1} attempts failed. Last error: {last_exception}")
            raise categorize_bedrock_error(last_exception)
        
        return wrapper
    return decorator

def with_timeout(timeout_seconds: float = 30.0) -> Callable:
    """
    Decorator to add timeout to function calls.
    
    Args:
        timeout_seconds: Timeout in seconds
        
    Returns:
        Decorated function with timeout
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            import asyncio
            import concurrent.futures
            
            # Check if function is async
            if asyncio.iscoroutinefunction(func):
                # For async functions, use asyncio.wait_for
                try:
                    return asyncio.wait_for(func(*args, **kwargs), timeout=timeout_seconds)
                except asyncio.TimeoutError:
                    raise BedrockTimeoutError(
                        f"Request timed out after {timeout_seconds} seconds. "
                        "Please try again or check your network connection."
                    )
            else:
                # For sync functions, use ThreadPoolExecutor with timeout
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(func, *args, **kwargs)
                    try:
                        return future.result(timeout=timeout_seconds)
                    except concurrent.futures.TimeoutError:
                        raise BedrockTimeoutError(
                            f"Request timed out after {timeout_seconds} seconds. "
                            "Please try again or check your network connection."
                        )
        
        return wrapper
    return decorator

def log_error_with_context(error: Exception, context: dict) -> None:
    """
    Log error with structured context for debugging.
    
    Args:
        error: The exception that occurred
        context: Additional context (provider, region, model, etc.)
    """
    # Redact sensitive information
    safe_context = {
        k: v for k, v in context.items() 
        if k not in ['aws_access_key_id', 'aws_secret_access_key', 'aws_session_token']
    }
    
    logger.error(
        f"Bedrock error occurred: {type(error).__name__}: {error}",
        extra={
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": safe_context
        }
    )
