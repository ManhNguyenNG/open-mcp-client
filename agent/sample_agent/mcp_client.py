"""
MCP Client for communicating with MCP servers using the complete protocol.
"""

import asyncio
import json
import logging
import subprocess
import time
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class MCPTransport(Enum):
    STDIO = "stdio"
    SSE = "sse"

@dataclass
class MCPServerConfig:
    """Configuration for an MCP server."""
    name: str
    command: str
    args: List[str]
    transport: MCPTransport = MCPTransport.STDIO
    working_directory: Optional[str] = None

class MCPSession:
    """Represents an active MCP session with a server."""
    
    def __init__(self, config: MCPServerConfig):
        self.config = config
        self.process: Optional[subprocess.Popen] = None
        self.session_id = f"{config.name}-{int(time.time())}"
        self.initialized = False
        self.tools: List[Dict[str, Any]] = []
        self.resources: List[Dict[str, Any]] = []
        self.prompts: List[Dict[str, Any]] = []
        
    async def initialize(self) -> bool:
        """Initialize the MCP session."""
        try:
            logger.info(f"Initializing MCP session for {self.config.name}")
            
            # Start the server process
            cmd = [self.config.command] + self.config.args
            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.config.working_directory
            )
            
            # Send initialization request
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {},
                        "prompts": {}
                    },
                    "clientInfo": {
                        "name": "langgraph-mcp-client",
                        "version": "1.0.0"
                    }
                }
            }
            
            success = await self._send_request(init_request)
            if not success:
                return False
            
            # Send initialized notification
            initialized_notification = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {}
            }
            
            await self._send_notification(initialized_notification)
            
            # List available tools, resources, and prompts
            await self._list_tools()
            await self._list_resources()
            await self._list_prompts()
            
            self.initialized = True
            logger.info(f"Successfully initialized MCP session for {self.config.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP session for {self.config.name}: {e}")
            return False
    
    async def _send_request(self, request: Dict[str, Any]) -> bool:
        """Send a JSON-RPC request to the server."""
        try:
            if not self.process:
                return False
                
            request_str = json.dumps(request) + "\n"
            self.process.stdin.write(request_str)
            self.process.stdin.flush()
            
            # Read response
            response_line = self.process.stdout.readline()
            if response_line:
                response = json.loads(response_line.strip())
                logger.debug(f"MCP response: {response}")
                
                if "error" in response:
                    logger.error(f"MCP error: {response['error']}")
                    return False
                    
                return True
            else:
                logger.error("No response from MCP server")
                return False
                
        except Exception as e:
            logger.error(f"Error sending request to MCP server: {e}")
            return False
    
    async def _send_notification(self, notification: Dict[str, Any]) -> bool:
        """Send a JSON-RPC notification to the server."""
        try:
            if not self.process:
                return False
                
            notification_str = json.dumps(notification) + "\n"
            self.process.stdin.write(notification_str)
            self.process.stdin.flush()
            return True
            
        except Exception as e:
            logger.error(f"Error sending notification to MCP server: {e}")
            return False
    
    async def _list_tools(self) -> bool:
        """List available tools from the server."""
        try:
            request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            if await self._send_request(request):
                # Parse tools from response
                response_line = self.process.stdout.readline()
                if response_line:
                    response = json.loads(response_line.strip())
                    if "result" in response and "tools" in response["result"]:
                        self.tools = response["result"]["tools"]
                        logger.info(f"Found {len(self.tools)} tools: {[t.get('name', 'unknown') for t in self.tools]}")
                        return True
            return False
            
        except Exception as e:
            logger.error(f"Error listing tools: {e}")
            return False
    
    async def _list_resources(self) -> bool:
        """List available resources from the server."""
        try:
            request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "resources/list",
                "params": {}
            }
            
            if await self._send_request(request):
                # Parse resources from response
                response_line = self.process.stdout.readline()
                if response_line:
                    response = json.loads(response_line.strip())
                    if "result" in response and "resources" in response["result"]:
                        self.resources = response["result"]["resources"]
                        logger.info(f"Found {len(self.resources)} resources")
                        return True
            return False
            
        except Exception as e:
            logger.error(f"Error listing resources: {e}")
            return False
    
    async def _list_prompts(self) -> bool:
        """List available prompts from the server."""
        try:
            request = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "prompts/list",
                "params": {}
            }
            
            if await self._send_request(request):
                # Parse prompts from response
                response_line = self.process.stdout.readline()
                if response_line:
                    response = json.loads(response_line.strip())
                    if "result" in response and "prompts" in response["result"]:
                        self.prompts = response["result"]["prompts"]
                        logger.info(f"Found {len(self.prompts)} prompts")
                        return True
            return False
            
        except Exception as e:
            logger.error(f"Error listing prompts: {e}")
            return False
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Any]:
        """Call a tool on the MCP server."""
        try:
            if not self.initialized:
                logger.error("MCP session not initialized")
                return None
            
            request = {
                "jsonrpc": "2.0",
                "id": int(time.time() * 1000),  # Unique ID
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            if await self._send_request(request):
                # Read tool response
                response_line = self.process.stdout.readline()
                if response_line:
                    response = json.loads(response_line.strip())
                    if "result" in response:
                        # Extract the result from the response
                        result = response["result"]
                        if "structuredContent" in result and "result" in result["structuredContent"]:
                            return result["structuredContent"]["result"]
                        elif "content" in result and len(result["content"]) > 0:
                            # Extract text content
                            content = result["content"][0]
                            if "text" in content:
                                return content["text"]
                        return result
                    elif "error" in response:
                        logger.error(f"Tool call error: {response['error']}")
                        return None
                        
            return None
            
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return None
    
    async def read_resource(self, uri: str) -> Optional[Any]:
        """Read a resource from the MCP server."""
        try:
            if not self.initialized:
                logger.error("MCP session not initialized")
                return None
            
            request = {
                "jsonrpc": "2.0",
                "id": int(time.time() * 1000),
                "method": "resources/read",
                "params": {
                    "uri": uri
                }
            }
            
            if await self._send_request(request):
                response_line = self.process.stdout.readline()
                if response_line:
                    response = json.loads(response_line.strip())
                    if "result" in response:
                        return response["result"]
                    elif "error" in response:
                        logger.error(f"Resource read error: {response['error']}")
                        return None
                        
            return None
            
        except Exception as e:
            logger.error(f"Error reading resource {uri}: {e}")
            return None
    
    async def close(self):
        """Close the MCP session."""
        try:
            if self.process:
                # Send shutdown notification
                shutdown_notification = {
                    "jsonrpc": "2.0",
                    "method": "notifications/exit",
                    "params": {}
                }
                await self._send_notification(shutdown_notification)
                
                # Terminate the process
                self.process.terminate()
                self.process.wait(timeout=5)
                self.process = None
                
            self.initialized = False
            logger.info(f"Closed MCP session for {self.config.name}")
            
        except Exception as e:
            logger.error(f"Error closing MCP session: {e}")

class MCPClient:
    """Client for managing multiple MCP server sessions."""
    
    def __init__(self):
        self.sessions: Dict[str, MCPSession] = {}
        self.session_configs: Dict[str, MCPServerConfig] = {}
    
    async def add_server(self, config: MCPServerConfig) -> bool:
        """Add and initialize an MCP server."""
        try:
            session = MCPSession(config)
            success = await session.initialize()
            
            if success:
                self.sessions[config.name] = session
                self.session_configs[config.name] = config
                logger.info(f"Successfully added MCP server: {config.name}")
                return True
            else:
                logger.error(f"Failed to add MCP server: {config.name}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding MCP server {config.name}: {e}")
            return False
    
    async def remove_server(self, server_name: str) -> bool:
        """Remove an MCP server session."""
        try:
            if server_name in self.sessions:
                session = self.sessions[server_name]
                await session.close()
                del self.sessions[server_name]
                del self.session_configs[server_name]
                logger.info(f"Removed MCP server: {server_name}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error removing MCP server {server_name}: {e}")
            return False
    
    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Optional[Any]:
        """Call a tool on a specific MCP server."""
        try:
            if server_name not in self.sessions:
                logger.error(f"Server {server_name} not found")
                return None
            
            session = self.sessions[server_name]
            return await session.call_tool(tool_name, arguments)
            
        except Exception as e:
            logger.error(f"Error calling tool {tool_name} on server {server_name}: {e}")
            return None
    
    async def read_resource(self, server_name: str, uri: str) -> Optional[Any]:
        """Read a resource from a specific MCP server."""
        try:
            if server_name not in self.sessions:
                logger.error(f"Server {server_name} not found")
                return None
            
            session = self.sessions[server_name]
            return await session.read_resource(uri)
            
        except Exception as e:
            logger.error(f"Error reading resource {uri} from server {server_name}: {e}")
            return None
    
    def get_server_info(self, server_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a server."""
        if server_name in self.sessions:
            session = self.sessions[server_name]
            return {
                "name": server_name,
                "initialized": session.initialized,
                "tools": session.tools,
                "resources": session.resources,
                "prompts": session.prompts,
                "config": {
                    "command": session.config.command,
                    "args": session.config.args,
                    "transport": session.config.transport.value
                }
            }
        return None
    
    def list_servers(self) -> List[str]:
        """List all connected servers."""
        return list(self.sessions.keys())
    
    async def close_all(self):
        """Close all MCP sessions."""
        for server_name in list(self.sessions.keys()):
            await self.remove_server(server_name)

# Global MCP client instance
mcp_client = MCPClient()
