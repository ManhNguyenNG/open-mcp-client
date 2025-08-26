"use client";

import MCPServerManager from "./components/MCPServerManager";
import StreamingChat from "./components/StreamingChat";

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Gestionnaire MCP */}
          <div className="lg:col-span-1">
            <MCPServerManager 
              onServerConnected={(server) => {
                console.log(`MCP Server connected: ${server.name}`);
              }}
              onServerDisconnected={(serverName) => {
                console.log(`MCP Server disconnected: ${serverName}`);
              }}
            />
          </div>
          
          {/* Chat Interface (StreamingChat uniquement) */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-md h-[600px]">
              <StreamingChat />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
