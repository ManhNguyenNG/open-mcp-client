import { NextRequest, NextResponse } from "next/server";
import { setConnectedServer, removeConnectedServer, getConnectedServers, getToolsForServer } from "../mcp-state";

// Endpoint pour connecter l'interface UI aux serveurs MCP
export async function POST(req: NextRequest) {
  try {
    const { serverName, command, args, transport = 'stdio' } = await req.json();

    if (!serverName || !command || !args) {
      return NextResponse.json(
        { error: 'Missing required fields: serverName, command, args' },
        { status: 400 }
      );
    }

    // Simuler la connexion au serveur MCP
    const connectionResult = {
      success: true,
      serverName,
      command,
      args: Array.isArray(args) ? args : [args],
      transport,
      connectedAt: new Date().toISOString(),
      status: 'connected',
      tools: getToolsForServer(serverName), // Get tools based on server name
      message: `Successfully connected to MCP server: ${serverName}`
    };

    // Store the connected server in the shared store
    setConnectedServer(serverName, connectionResult);

    console.log(`MCP Connection: ${serverName} via ${command} ${args.join(' ')}`);

    return NextResponse.json(connectionResult);

  } catch (error) {
    console.error('Error connecting to MCP server:', error);
    return NextResponse.json(
      { error: 'Failed to connect to MCP server' },
      { status: 500 }
    );
  }
}

// Endpoint pour lister les serveurs MCP connectés
export async function GET() {
  try {
    const connectedServers = getConnectedServers();
    
    // Convert Map to array
    const servers = Array.from(connectedServers.values());
    
    return NextResponse.json({
      servers,
      total: servers.length
    });

  } catch (error) {
    console.error('Error listing MCP servers:', error);
    return NextResponse.json(
      { error: 'Failed to list MCP servers' },
      { status: 500 }
    );
  }
}

// Endpoint pour déconnecter un serveur MCP
export async function DELETE(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const serverName = searchParams.get('serverName');

    if (!serverName) {
      return NextResponse.json(
        { error: 'Server name required' },
        { status: 400 }
      );
    }

    // Remove from connected servers
    removeConnectedServer(serverName);

    console.log(`MCP Disconnection: ${serverName}`);

    return NextResponse.json({
      success: true,
      serverName,
      wasConnected: true,
      message: `Successfully disconnected from MCP server: ${serverName}`
    });

  } catch (error) {
    console.error('Error disconnecting from MCP server:', error);
    return NextResponse.json(
      { error: 'Failed to disconnect from MCP server' },
      { status: 500 }
    );
  }
}
