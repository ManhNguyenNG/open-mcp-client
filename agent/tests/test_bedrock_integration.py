"""
Unit tests for AWS Bedrock integration.
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from sample_agent.config import BedrockConfig
from sample_agent.llm_provider import get_llm_provider, get_provider_info
from sample_agent.error_handling import (
    categorize_bedrock_error,
    BedrockThrottlingError,
    BedrockPermissionError,
    BedrockValidationError,
    BedrockTimeoutError
)

class TestBedrockConfig:
    """Test BedrockConfig class."""
    
    def test_default_config(self):
        """Test default configuration when no env vars are set."""
        with patch.dict(os.environ, {}, clear=True):
            # Should fail because Bedrock is default but no credentials
            with pytest.raises(ValueError, match="AWS credentials required"):
                BedrockConfig()
    
    def test_bedrock_provider_config(self):
        """Test Bedrock provider configuration."""
        env_vars = {
            "LLM_PROVIDER": "bedrock",
            "AWS_ACCESS_KEY_ID": "test-key",
            "AWS_SECRET_ACCESS_KEY": "test-secret",
            "AWS_REGION": "us-west-2",
            "BEDROCK_MODEL_ID": "test-model"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = BedrockConfig()
            assert config.provider == "bedrock"
            assert config.region == "us-west-2"
            assert config.model_id == "test-model"
            assert config.aws_access_key_id == "test-key"
            assert config.aws_secret_access_key == "test-secret"
    
    def test_openai_provider_config(self):
        """Test OpenAI provider configuration."""
        env_vars = {
            "LLM_PROVIDER": "openai"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = BedrockConfig()
            assert config.provider == "openai"
    
    def test_missing_credentials_error(self):
        """Test error when Bedrock is enabled but credentials are missing."""
        env_vars = {
            "LLM_PROVIDER": "bedrock"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValueError, match="AWS credentials required"):
                BedrockConfig()
    
    def test_invalid_region_error(self):
        """Test error when region is invalid."""
        env_vars = {
            "LLM_PROVIDER": "bedrock",
            "AWS_ACCESS_KEY_ID": "test-key",
            "AWS_SECRET_ACCESS_KEY": "test-secret",
            "AWS_REGION": "invalid"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValueError, match="Invalid AWS region"):
                BedrockConfig()
    
    def test_invalid_model_id_error(self):
        """Test error when model ID is invalid."""
        env_vars = {
            "LLM_PROVIDER": "bedrock",
            "AWS_ACCESS_KEY_ID": "test-key",
            "AWS_SECRET_ACCESS_KEY": "test-secret",
            "BEDROCK_MODEL_ID": "x"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValueError, match="Invalid Bedrock model ID"):
                BedrockConfig()
    
    def test_optional_parameters(self):
        """Test optional parameter parsing."""
        env_vars = {
            "LLM_PROVIDER": "bedrock",
            "AWS_ACCESS_KEY_ID": "test-key",
            "AWS_SECRET_ACCESS_KEY": "test-secret",
            "BEDROCK_MAX_TOKENS": "1000",
            "BEDROCK_TEMPERATURE": "0.7",
            "BEDROCK_TOP_P": "0.9",
            "BEDROCK_STOP": "stop1,stop2,stop3"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = BedrockConfig()
            assert config.max_tokens == 1000
            assert config.temperature == 0.7
            assert config.top_p == 0.9
            assert config.stop_sequences == ["stop1", "stop2", "stop3"]
    
    def test_invalid_parameter_values(self):
        """Test handling of invalid parameter values."""
        env_vars = {
            "LLM_PROVIDER": "bedrock",
            "AWS_ACCESS_KEY_ID": "test-key",
            "AWS_SECRET_ACCESS_KEY": "test-secret",
            "BEDROCK_MAX_TOKENS": "invalid",
            "BEDROCK_TEMPERATURE": "invalid"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = BedrockConfig()
            assert config.max_tokens is None
            assert config.temperature is None

class TestLLMProvider:
    """Test LLM provider selection."""
    
    def test_bedrock_provider_default(self):
        """Test that Bedrock is the default provider."""
        env_vars = {
            "AWS_ACCESS_KEY_ID": "test-key",
            "AWS_SECRET_ACCESS_KEY": "test-secret"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('sample_agent.llm_provider.ChatBedrock') as mock_bedrock:
                mock_model = MagicMock()
                mock_bedrock.return_value = mock_model
                
                model = get_llm_provider()
                
                mock_bedrock.assert_called_once()
                assert model == mock_model
    
    def test_openai_provider_selection(self):
        """Test OpenAI provider selection."""
        env_vars = {
            "LLM_PROVIDER": "openai"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('sample_agent.llm_provider.ChatOpenAI') as mock_openai:
                mock_model = MagicMock()
                mock_openai.return_value = mock_model
                
                model = get_llm_provider()
                
                mock_openai.assert_called_once_with(model="gpt-4o")
                assert model == mock_model
    
    def test_provider_info_bedrock(self):
        """Test provider info for Bedrock (default)."""
        env_vars = {
            "AWS_ACCESS_KEY_ID": "test-key",
            "AWS_SECRET_ACCESS_KEY": "test-secret",
            "AWS_REGION": "us-west-2",
            "BEDROCK_MODEL_ID": "test-model"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            info = get_provider_info()
            assert info["provider"] == "bedrock"
            assert info["model"] == "test-model"
            assert info["region"] == "us-west-2"
            assert info["has_credentials"] is True
    
    def test_provider_info_openai(self):
        """Test provider info for OpenAI."""
        env_vars = {
            "LLM_PROVIDER": "openai"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            info = get_provider_info()
            assert info["provider"] == "openai"
            assert info["model"] == "gpt-4o"

class TestErrorHandling:
    """Test error handling and categorization."""
    
    def test_throttling_error_categorization(self):
        """Test throttling error categorization."""
        error = Exception("ThrottlingException: Rate exceeded")
        categorized = categorize_bedrock_error(error)
        assert isinstance(categorized, BedrockThrottlingError)
        assert "rate exceeded" in str(categorized).lower()
    
    def test_permission_error_categorization(self):
        """Test permission error categorization."""
        error = Exception("AccessDeniedException: Access denied")
        categorized = categorize_bedrock_error(error)
        assert isinstance(categorized, BedrockPermissionError)
        assert "access denied" in str(categorized).lower()
    
    def test_validation_error_categorization(self):
        """Test validation error categorization."""
        error = Exception("ValidationException: Invalid parameter")
        categorized = categorize_bedrock_error(error)
        assert isinstance(categorized, BedrockValidationError)
        assert "invalid" in str(categorized).lower()
    
    def test_timeout_error_categorization(self):
        """Test timeout error categorization."""
        error = Exception("TimeoutException: Request timed out")
        categorized = categorize_bedrock_error(error)
        assert isinstance(categorized, BedrockTimeoutError)
        assert "timed out" in str(categorized).lower()
    
    def test_generic_error_categorization(self):
        """Test generic error categorization."""
        error = Exception("Some other error")
        categorized = categorize_bedrock_error(error)
        assert isinstance(categorized, BedrockError)
        assert "bedrock service error" in str(categorized).lower()

if __name__ == "__main__":
    pytest.main([__file__])
