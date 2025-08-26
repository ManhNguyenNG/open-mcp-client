"""
Custom Bedrock client implementation using boto3 directly.
This avoids the langchain-aws dependency conflict.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Iterator, AsyncIterator
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.outputs import ChatResult, ChatGeneration
import boto3
from botocore.exceptions import ClientError, BotoCoreError

logger = logging.getLogger(__name__)

class ChatBedrock(BaseChatModel):
    """
    Custom Bedrock chat model implementation.
    """
    
    def __init__(
        self,
        model_id: str,
        region_name: str = "us-east-1",
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_session_token: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        stop: Optional[List[str]] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.model_id = model_id
        self.region_name = region_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.stop = stop
        
        # Initialize Bedrock client
        self.client = boto3.client(
            'bedrock-runtime',
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token
        )
        
        logger.info(f"Bedrock client initialized for model: {model_id} in region: {region_name}")
    
    def _format_messages_for_bedrock(self, messages: List[BaseMessage]) -> Dict[str, Any]:
        """
        Format messages for Bedrock API.
        """
        # Convert messages to Bedrock format
        formatted_messages = []
        
        for message in messages:
            if isinstance(message, SystemMessage):
                # System messages are typically handled differently
                continue
            elif isinstance(message, HumanMessage):
                formatted_messages.append({
                    "role": "user",
                    "content": message.content
                })
            elif isinstance(message, AIMessage):
                formatted_messages.append({
                    "role": "assistant",
                    "content": message.content
                })
        
        # Build request body
        body = {
            "messages": formatted_messages,
            "anthropic_version": "bedrock-2023-05-31"
        }
        
        # Add optional parameters
        if self.max_tokens is not None:
            body["max_tokens"] = self.max_tokens
        if self.temperature is not None:
            body["temperature"] = self.temperature
        if self.top_p is not None:
            body["top_p"] = self.top_p
        if self.stop is not None:
            body["stop_sequences"] = self.stop
        
        return body
    
    def _invoke_bedrock(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoke Bedrock model.
        """
        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            return response_body
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            if error_code == 'ThrottlingException':
                raise Exception(f"Throttling error: {error_message}")
            elif error_code == 'AccessDeniedException':
                raise Exception(f"Access denied: {error_message}")
            elif error_code == 'ValidationException':
                raise Exception(f"Validation error: {error_message}")
            else:
                raise Exception(f"Bedrock error ({error_code}): {error_message}")
                
        except BotoCoreError as e:
            raise Exception(f"Boto3 error: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        Generate a response from the model.
        """
        try:
            # Format messages for Bedrock
            body = self._format_messages_for_bedrock(messages)
            
            # Override stop sequences if provided
            if stop is not None:
                body["stop_sequences"] = stop
            
            # Invoke Bedrock
            response = self._invoke_bedrock(body)
            
            # Extract content from response
            content = response.get('content', [{}])[0].get('text', '')
            
            # Create AIMessage
            ai_message = AIMessage(content=content)
            
            # Create ChatGeneration
            generation = ChatGeneration(message=ai_message)
            
            return ChatResult(generations=[generation])
            
        except Exception as e:
            logger.error(f"Error in Bedrock generation: {e}")
            raise
    
    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        Async version of generate.
        """
        # For now, use synchronous version
        # In a real implementation, you might want to use asyncio.to_thread
        return self._generate(messages, stop, run_manager, **kwargs)
    
    @property
    def _llm_type(self) -> str:
        """Return type of LLM."""
        return "bedrock"
