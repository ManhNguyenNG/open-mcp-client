"""
LLM Provider selection module.
Handles provider selection and model initialization for OpenAI and AWS Bedrock.
"""

from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel
import logging

from .config import get_bedrock_config
from .error_handling import (
    exponential_backoff_with_jitter, 
    with_timeout, 
    log_error_with_context,
    BedrockError
)
from .bedrock_client import ChatBedrock

logger = logging.getLogger(__name__)

def get_llm_provider() -> BaseChatModel:
    """
    Get the configured LLM provider based on environment variables.
    
    Returns:
        BaseChatModel: Configured chat model (OpenAI or Bedrock)
    
    Raises:
        ValueError: If provider configuration is invalid
    """
    bedrock_config = get_bedrock_config()
    
    if bedrock_config.is_bedrock_enabled():
        logger.info(f"Using AWS Bedrock provider with model: {bedrock_config.model_id}")
        return _create_bedrock_model()
    else:
        logger.info("Using OpenAI provider")
        return _create_openai_model()

@exponential_backoff_with_jitter(max_retries=3, base_delay=0.25, max_delay=2.0)
@with_timeout(timeout_seconds=30.0)
def _create_bedrock_model() -> ChatBedrock:
    """Create and configure Bedrock chat model with error handling and retry logic."""
    try:
        bedrock_config = get_bedrock_config()
        
        # Get AWS configuration
        aws_config = bedrock_config.get_aws_config()
        
        # Get model parameters
        model_params = bedrock_config.get_bedrock_params()
        
        # Create Bedrock model using our custom implementation
        model = ChatBedrock(
            model_id=bedrock_config.model_id,
            **aws_config,
            **model_params
        )
        
        logger.info(f"Bedrock model configured: {bedrock_config.model_id} in {bedrock_config.region}")
        return model
        
    except Exception as e:
        # Log error with context for debugging
        context = {
            "provider": "bedrock",
            "model_id": bedrock_config.model_id,
            "region": bedrock_config.region,
            "has_credentials": bool(bedrock_config.aws_access_key_id and bedrock_config.aws_secret_access_key)
        }
        log_error_with_context(e, context)
        
        # Re-raise as BedrockError for consistent error handling
        raise BedrockError(f"Failed to create Bedrock model: {e}")

def _create_openai_model() -> ChatOpenAI:
    """Create and configure OpenAI chat model."""
    try:
        # Use existing OpenAI configuration
        model = ChatOpenAI(model="gpt-4o")
        logger.info("OpenAI model configured: gpt-4o")
        return model
        
    except Exception as e:
        logger.error(f"Failed to create OpenAI model: {e}")
        raise ValueError(f"OpenAI configuration error: {e}")

def get_provider_info() -> dict:
    """
    Get information about the current provider configuration.
    Does not expose sensitive information.
    
    Returns:
        dict: Provider information (name, model, region if applicable)
    """
    bedrock_config = get_bedrock_config()
    
    if bedrock_config.is_bedrock_enabled():
        return {
            "provider": "bedrock",
            "model": bedrock_config.model_id,
            "region": bedrock_config.region,
            "has_credentials": bool(bedrock_config.aws_access_key_id and bedrock_config.aws_secret_access_key)
        }
    else:
        return {
            "provider": "openai",
            "model": "gpt-4o"
        }
