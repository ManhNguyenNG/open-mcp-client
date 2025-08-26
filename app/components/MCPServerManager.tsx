'use client';

import React, { useState, useEffect } from 'react';

interface MCPServer {
  id: string;
  name: string;
  command: string;
  args: string[];
  transport: 'stdio' | 'sse';
  status: 'connected' | 'disconnected' | 'error';
  connectedAt?: string;
  tools?: string[];
}

interface MCPServerManagerProps {
  onServerConnected?: (server: MCPServer) => void;
  onServerDisconnected?: (serverName: string) => void;
}

export default function MCPServerManager({ onServerConnected, onServerDisconnected }: MCPServerManagerProps) {
  const [servers, setServers] = useState<MCPServer[]>([]);
  const [loading, setLoading] = useState(false);
  const [newServer, setNewServer] = useState({
    name: '',
    command: 'python',
    args: ['agent/math_server.py'],
    transport: 'stdio' as const
  });

  // Charger les serveurs MCP existants
  useEffect(() => {
    loadMCPServers();
  }, []);

  const loadMCPServers = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/mcp-servers');
      const data = await response.json();
      setServers(data.servers || []);
    } catch (error) {
      console.error('Error loading MCP servers:', error);
    } finally {
      setLoading(false);
    }
  };

  const connectToServer = async (server: MCPServer) => {
    try {
      setLoading(true);
      const response = await fetch('/api/mcp-connect', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          serverName: server.name,
          command: server.command,
          args: server.args,
          transport: server.transport
        }),
      });

      const result = await response.json();
      
      if (result.success) {
        // Mettre à jour le statut du serveur
        setServers(prev => prev.map(s => 
          s.id === server.id 
            ? { ...s, status: 'connected', connectedAt: result.connectedAt, tools: result.tools }
            : s
        ));
        
        onServerConnected?.(server);
        console.log(`Connected to MCP server: ${server.name}`);
      } else {
        console.error('Failed to connect to MCP server:', result.error);
      }
    } catch (error) {
      console.error('Error connecting to MCP server:', error);
    } finally {
      setLoading(false);
    }
  };

  const disconnectFromServer = async (serverName: string) => {
    try {
      setLoading(true);
      const response = await fetch(`/api/mcp-connect?serverName=${serverName}`, {
        method: 'DELETE',
      });

      const result = await response.json();
      
      if (result.success) {
        // Mettre à jour le statut du serveur
        setServers(prev => prev.map(s => 
          s.name === serverName 
            ? { ...s, status: 'disconnected', connectedAt: undefined, tools: undefined }
            : s
        ));
        
        onServerDisconnected?.(serverName);
        console.log(`Disconnected from MCP server: ${serverName}`);
      } else {
        console.error('Failed to disconnect from MCP server:', result.error);
      }
    } catch (error) {
      console.error('Error disconnecting from MCP server:', error);
    } finally {
      setLoading(false);
    }
  };

  const addServer = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/mcp-servers', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newServer),
      });

      const result = await response.json();
      
      if (result.server) {
        setServers(prev => [...prev, result.server]);
        setNewServer({
          name: '',
          command: 'python',
          args: ['agent/math_server.py'],
          transport: 'stdio'
        });
        console.log('MCP server added successfully');
      } else {
        console.error('Failed to add MCP server:', result.error);
      }
    } catch (error) {
      console.error('Error adding MCP server:', error);
    } finally {
      setLoading(false);
    }
  };

  const removeServer = async (serverId: string) => {
    try {
      setLoading(true);
      const response = await fetch(`/api/mcp-servers?id=${serverId}`, {
        method: 'DELETE',
      });

      const result = await response.json();
      
      if (result.server) {
        setServers(prev => prev.filter(s => s.id !== serverId));
        console.log('MCP server removed successfully');
      } else {
        console.error('Failed to remove MCP server:', result.error);
      }
    } catch (error) {
      console.error('Error removing MCP server:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">MCP Server Manager</h2>
      
      {/* Statistiques */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-blue-600">{servers.length}</div>
          <div className="text-sm text-blue-800">Total Servers</div>
        </div>
        <div className="bg-green-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-green-600">
            {servers.filter(s => s.status === 'connected').length}
          </div>
          <div className="text-sm text-green-800">Connected</div>
        </div>
        <div className="bg-red-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-red-600">
            {servers.filter(s => s.status === 'error').length}
          </div>
          <div className="text-sm text-red-800">Errors</div>
        </div>
      </div>

      {/* Ajouter un nouveau serveur */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg">
        <h3 className="text-lg font-semibold mb-4 text-gray-700">Add New MCP Server</h3>
        <div className="grid grid-cols-2 gap-4">
          <input
            type="text"
            placeholder="Server Name"
            value={newServer.name}
            onChange={(e) => setNewServer(prev => ({ ...prev, name: e.target.value }))}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <input
            type="text"
            placeholder="Command (e.g., python)"
            value={newServer.command}
            onChange={(e) => setNewServer(prev => ({ ...prev, command: e.target.value }))}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <input
            type="text"
            placeholder="Args (e.g., agent/math_server.py)"
            value={newServer.args.join(' ')}
            onChange={(e) => setNewServer(prev => ({ ...prev, args: e.target.value.split(' ') }))}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <select
            value={newServer.transport}
            onChange={(e) => setNewServer(prev => ({ ...prev, transport: e.target.value as 'stdio' | 'sse' }))}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="stdio">STDIO</option>
            <option value="sse">SSE</option>
          </select>
        </div>
        <button
          onClick={addServer}
          disabled={loading || !newServer.name}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Adding...' : 'Add Server'}
        </button>
      </div>

      {/* Liste des serveurs */}
      <div>
        <h3 className="text-lg font-semibold mb-4 text-gray-700">MCP Servers</h3>
        {servers.length === 0 ? (
          <p className="text-gray-500 text-center py-8">No MCP servers configured</p>
        ) : (
          <div className="space-y-4">
            {servers.map((server) => (
              <div key={server.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <h4 className="font-semibold text-gray-800">{server.name}</h4>
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      server.status === 'connected' ? 'bg-green-100 text-green-800' :
                      server.status === 'error' ? 'bg-red-100 text-red-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {server.status}
                    </span>
                    <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">
                      {server.transport}
                    </span>
                  </div>
                  <div className="flex space-x-2">
                    {server.status === 'connected' ? (
                      <button
                        onClick={() => disconnectFromServer(server.name)}
                        disabled={loading}
                        className="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
                      >
                        Disconnect
                      </button>
                    ) : (
                      <button
                        onClick={() => connectToServer(server)}
                        disabled={loading}
                        className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
                      >
                        Connect
                      </button>
                    )}
                    <button
                      onClick={() => removeServer(server.id)}
                      disabled={loading}
                      className="px-3 py-1 text-sm bg-gray-600 text-white rounded hover:bg-gray-700 disabled:opacity-50"
                    >
                      Remove
                    </button>
                  </div>
                </div>
                <div className="text-sm text-gray-600">
                  <p><strong>Command:</strong> {server.command} {server.args.join(' ')}</p>
                  {server.connectedAt && (
                    <p><strong>Connected:</strong> {new Date(server.connectedAt).toLocaleString()}</p>
                  )}
                  {server.tools && server.tools.length > 0 && (
                    <p><strong>Tools:</strong> {server.tools.join(', ')}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
