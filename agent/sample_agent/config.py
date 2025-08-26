"""
Configuration module for AWS Bedrock integration.
Handles environment variables, validation, and defaults.
"""

import os
from typing import Optional, Dict, List, Any, Union
import logging

logger = logging.getLogger(__name__)

class BedrockConfig:
    """Configuration for AWS Bedrock integration."""
    
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "bedrock").lower()
        self.region = os.getenv("AWS_REGION", "us-east-1")
        self.model_id = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0")
        
        # Optional tuning parameters
        self.max_tokens = self._parse_int_env("BEDROCK_MAX_TOKENS")
        self.temperature = self._parse_float_env("BEDROCK_TEMPERATURE")
        self.top_p = self._parse_float_env("BEDROCK_TOP_P")
        self.stop_sequences = self._parse_list_env("BEDROCK_STOP")
        
        # AWS credentials (will be resolved by boto3)
        self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.aws_session_token = os.getenv("AWS_SESSION_TOKEN")
        
        self._validate_config()
    
    def _parse_int_env(self, env_var: str) -> Optional[int]:
        """Parse integer environment variable."""
        value = os.getenv(env_var)
        if value is not None:
            try:
                return int(value)
            except ValueError:
                logger.warning(f"Invalid integer value for {env_var}: {value}")
                return None
        return None
    
    def _parse_float_env(self, env_var: str) -> Optional[float]:
        """Parse float environment variable."""
        value = os.getenv(env_var)
        if value is not None:
            try:
                return float(value)
            except ValueError:
                logger.warning(f"Invalid float value for {env_var}: {value}")
                return None
        return None
    
    def _parse_list_env(self, env_var: str) -> Optional[list[str]]:
        """Parse comma-separated list environment variable."""
        value = os.getenv(env_var)
        if value is not None:
            return [item.strip() for item in value.split(",") if item.strip()]
        return None
    
    def _validate_config(self):
        """Validate configuration and log warnings for defaults."""
        if self.provider == "bedrock":
            # Log defaults when not explicitly set
            if os.getenv("AWS_REGION") is None:
                logger.warning(f"AWS_REGION not set, defaulting to: {self.region}")
            
            if os.getenv("BEDROCK_MODEL_ID") is None:
                logger.warning(f"BEDROCK_MODEL_ID not set, defaulting to: {self.model_id}")
            
            # Validate required credentials
            if not self.aws_access_key_id or not self.aws_secret_access_key:
                raise ValueError(
                    "AWS credentials required for Bedrock provider. "
                    "Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables."
                )
            
            # Validate region format (basic check)
            if not self.region or len(self.region) < 3:
                raise ValueError(f"Invalid AWS region: {self.region}")
            
            # Validate model ID format (basic check)
            if not self.model_id or len(self.model_id) < 5:
                raise ValueError(f"Invalid Bedrock model ID: {self.model_id}")
        elif self.provider == "openai":
            # Log that OpenAI is being used
            logger.info("Using OpenAI provider (explicitly set)")
        else:
            raise ValueError(f"Unsupported provider: {self.provider}. Supported providers: 'openai', 'bedrock'")
    
    def is_bedrock_enabled(self) -> bool:
        """Check if Bedrock provider is enabled."""
        return self.provider == "bedrock"
    
    def get_bedrock_params(self) -> Dict[str, Any]:
        """Get Bedrock parameters for model invocation."""
        params = {}
        
        if self.max_tokens is not None:
            params["max_tokens"] = self.max_tokens
        
        if self.temperature is not None:
            params["temperature"] = self.temperature
        
        if self.top_p is not None:
            params["top_p"] = self.top_p
        
        if self.stop_sequences is not None:
            params["stop"] = self.stop_sequences
        
        return params
    
    def get_aws_config(self) -> Dict[str, Any]:
        """Get AWS configuration for Bedrock client."""
        config = {
            "region_name": self.region,
        }
        
        # Only set credentials if explicitly provided
        if self.aws_access_key_id:
            config["aws_access_key_id"] = self.aws_access_key_id
        if self.aws_secret_access_key:
            config["aws_secret_access_key"] = self.aws_secret_access_key
        if self.aws_session_token:
            config["aws_session_token"] = self.aws_session_token
        
        return config

def get_bedrock_config() -> BedrockConfig:
    """Get the global Bedrock configuration instance."""
    if not hasattr(get_bedrock_config, '_instance'):
        get_bedrock_config._instance = BedrockConfig()
    return get_bedrock_config._instance

# Global configuration instance (lazy loading)
bedrock_config = None

def _get_bedrock_config():
    """Lazy loading of the global configuration."""
    global bedrock_config
    if bedrock_config is None:
        bedrock_config = BedrockConfig()
    return bedrock_config
