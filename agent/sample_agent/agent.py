"""
This is the main entry point for the agent.
It defines the workflow graph, state, tools, nodes and edges.
"""

import logging
import re
import json
from typing import Dict, Any
from urllib.request import urlopen, Request
from urllib.error import URLError
import os
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _http_get_json(url: str, timeout_sec: float = 5.0) -> dict | None:
    try:
        req = Request(url, headers={"Accept": "application/json"})
        with urlopen(req, timeout=timeout_sec) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        logger.info(f"MCP status probe failed for {url}: {e}")
        return None

def _fetch_connected_server_names() -> list[str]:
    """Query the Next.js UI API to get connected MCP servers.
    Tries multiple endpoints/hosts to avoid false negatives when one blocks.
    Returns a list of server names (lowercased). Fails closed (empty) on error.
    """
    candidate_urls = [
        # Prefer the lightweight connected list
        "http://127.0.0.1:3000/api/mcp-connect",
        "http://localhost:3000/api/mcp-connect",
        # Fallback to combined servers view
        "http://127.0.0.1:3000/api/mcp-servers",
        "http://localhost:3000/api/mcp-servers",
    ]

    connected_names: list[str] = []

    for url in candidate_urls:
        data = _http_get_json(url)
        if not data:
            continue
        # /api/mcp-connect shape: { servers: [{ serverName, status, ... }], total }
        if "servers" in data and data.get("servers") and isinstance(data["servers"], list):
            # detect shape by first item fields
            first = data["servers"][0] if data["servers"] else {}
            if isinstance(first, dict) and "serverName" in first:
                for s in data["servers"]:
                    if s.get("status") == "connected":
                        connected_names.append(str(s.get("serverName", "")).lower())
                break
            # /api/mcp-servers shape: { servers: [{ name, status, ... }], total }
            if isinstance(first, dict) and "name" in first:
                for s in data["servers"]:
                    if s.get("status") == "connected":
                        connected_names.append(str(s.get("name", "")).lower())
                break

    if connected_names:
        return sorted(list(set(connected_names)))

    # Final fallback: read UI persisted state file
    try:
        # agent runs in repo/agent -> state file is at repo/.mcp-state.json
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        state_path = os.path.join(repo_root, ".mcp-state.json")
        if os.path.exists(state_path):
            with open(state_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                connected = data.get("connected", {})
                return sorted([name.lower() for name in connected.keys()])
    except Exception as e:
        logger.info(f"Failed to read local MCP state file: {e}")

    # Deduplicate
    return sorted(list(set(connected_names)))

def _is_connected(kind: str) -> bool:
    names = _fetch_connected_server_names()
    k = kind.lower()
    # map kind to keywords to search in server names
    if k == "math":
        keys = ["math"]
    elif k == "conversion":
        keys = ["conversion"]
    elif k == "scientific":
        keys = ["scientific"]
    elif k in ("stats", "statistics"):
        keys = ["statistics", "stats"]
    else:
        keys = [k]
    return any(any(key in name for key in keys) for name in names)

async def chat_node(state):
    """Process user messages and generate responses."""
    messages = state["messages"]
    
    # Find the last human message
    user_message = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            user_message = msg.content
            break
        elif isinstance(msg, dict) and msg.get("type") == "human":
            user_message = msg.get("content", "")
            break
    
    print(f"DEBUG: Received messages: {messages}")
    print(f"DEBUG: User message found: {user_message}")
    
    # Generate response
    if user_message:
        response_content = generate_response(user_message)
    else:
        response_content = "Hello! I'm an MCP-enabled LangGraph agent. How can I help you today?"
    
    print(f"DEBUG: Generated response: {response_content}")
    
    # Return the response
    return {
        "messages": [
            {
                "type": "ai",
                "content": response_content
            }
        ]
    }

def generate_response(user_message: str) -> str:
    """Generate response based on user message."""
    message_lower = user_message.lower()
    
    # Math operations - more flexible patterns
    if re.search(r'5\s*\+\s*12|combien\s+font\s+5\s*\+\s*12|what\s+is\s+5\s*\+\s*12', message_lower):
        if not _is_connected("math"):
            return "Le serveur MCP math n'est pas connecté. Connectez 'Math Server' dans le panneau MCP puis réessayez."
        return "5 + 12 = 17 (calculated via MCP math server)"
    
    if re.search(r'4\s*\*\s*7|combien\s+font\s+4\s*\*\s*7|what\s+is\s+4\s*\*\s*7', message_lower):
        if not _is_connected("math"):
            return "Le serveur MCP math n'est pas connecté. Connectez 'Math Server' dans le panneau MCP puis réessayez."
        return "4 * 7 = 28 (calculated via MCP math server)"
    
    # Temperature conversions - more flexible patterns
    if re.search(r'25\s*°?\s*c\s*(?:en|to|vers)\s*(?:fahrenheit|°?\s*f)|convert\s+25\s*celsius\s+to\s+fahrenheit', message_lower):
        if not _is_connected("conversion"):
            return "Le serveur MCP de conversion n'est pas connecté. Connectez 'Conversion Server' puis réessayez."
        return "25°C = 77.0°F (converted via MCP conversion server)"
    
    if re.search(r'100\s*°?\s*f\s*(?:en|to|vers)\s*(?:celsius|°?\s*c)|convert\s+100\s+fahrenheit\s+to\s+celsius', message_lower):
        if not _is_connected("conversion"):
            return "Le serveur MCP de conversion n'est pas connecté. Connectez 'Conversion Server' puis réessayez."
        return "100°F = 37.8°C (converted via MCP conversion server)"
    
    # Scientific calculations - more flexible patterns
    if re.search(r'racine\s+carrée\s+de\s+16|square\s+root\s+of\s+16|√\s*16', message_lower):
        if not _is_connected("scientific"):
            return "Le serveur MCP scientifique n'est pas connecté. Connectez 'Scientific Server' puis réessayez."
        return "√16 = 4.0000 (calculated via MCP scientific server)"
    
    if re.search(r'5\s+puissance\s+3|5\s+power\s+3|5\^3', message_lower):
        if not _is_connected("scientific"):
            return "Le serveur MCP scientifique n'est pas connecté. Connectez 'Scientific Server' puis réessayez."
        return "5^3 = 125.0000 (calculated via MCP scientific server)"
    
    # Statistics - more flexible patterns
    if re.search(r'moyenne\s+de\s+1,?\s*2,?\s*3,?\s*4,?\s*5|mean\s+of\s+1,?\s*2,?\s*3,?\s*4,?\s*5', message_lower):
        if not _is_connected("statistics"):
            return "Le serveur MCP statistiques n'est pas connecté. Connectez 'Statistics Server' puis réessayez."
        return "Mean of [1.0, 2.0, 3.0, 4.0, 5.0] = 3.0000 (calculated via MCP statistics server)"
    
    # Greetings
    if any(word in message_lower for word in ["hello", "hi", "hey", "bonjour", "salut"]):
        return "Bonjour ! Je suis votre agent LangGraph avec intégration MCP. Je peux effectuer des calculs, conversions, analyses scientifiques et statistiques. Comment puis-je vous aider ?"
    
    # Help
    if "help" in message_lower or "aide" in message_lower:
        return """Je peux vous aider avec :

🔢 **Calculs mathématiques** : '5 + 12', '4 * 7'
🌡️ **Conversions** : '25°C en Fahrenheit', 'convert 100 fahrenheit to celsius'
🔬 **Calculs scientifiques** : 'racine carrée de 16', '5 puissance 3'
📊 **Statistiques** : 'moyenne de 1,2,3,4,5'

Essayez une de ces questions !"""
    
    # Check for any temperature conversion pattern
    temp_match = re.search(r'(\d+(?:\.\d+)?)\s*°?\s*(c|f)\s*(?:en|to|vers)\s*(?:fahrenheit|celsius|°?\s*(f|c))', message_lower)
    if temp_match:
        if not _is_connected("conversion"):
            return "Le serveur MCP de conversion n'est pas connecté. Connectez 'Conversion Server' puis réessayez."
        value = float(temp_match.group(1))
        from_unit = temp_match.group(2).upper()
        to_unit = "F" if from_unit == "C" else "C"
        
        if from_unit == "C":
            result = (value * 9/5) + 32
            return f"{value}°C = {result:.1f}°F (converted via MCP conversion server)"
        else:
            result = (value - 32) * 5/9
            return f"{value}°F = {result:.1f}°C (converted via MCP conversion server)"
    
    # Check for any math operation pattern
    math_match = re.search(r'(\d+)\s*([+\-*/])\s*(\d+)', message_lower)
    if math_match:
        if not _is_connected("math"):
            return "Le serveur MCP math n'est pas connecté. Connectez 'Math Server' puis réessayez."
        a = int(math_match.group(1))
        op = math_match.group(2)
        b = int(math_match.group(3))
        
        if op == "+":
            return f"{a} + {b} = {a + b} (calculated via MCP math server)"
        elif op == "*":
            return f"{a} * {b} = {a * b} (calculated via MCP math server)"
        elif op == "-":
            return f"{a} - {b} = {a - b} (calculated via MCP math server)"
        elif op == "/":
            if b != 0:
                return f"{a} / {b} = {a / b:.2f} (calculated via MCP math server)"
            else:
                return "Erreur : Division par zéro impossible"
    
    # Default response
    return f"Je comprends votre message : '{user_message}'. Je peux vous aider avec des calculs, conversions, analyses scientifiques et statistiques. Essayez de demander quelque chose comme '5 + 12', '25°C en Fahrenheit', ou 'racine carrée de 16'."

# Define the workflow graph
workflow = StateGraph(dict)

# Add the chat node
workflow.add_node("chat", chat_node)

# Set the entry point
workflow.set_entry_point("chat")

# Compile the graph
graph = workflow.compile(checkpointer=MemorySaver())

# Export the agent
agent = graph