import { NextRequest, NextResponse } from "next/server";
import { getConfiguredServers, getToolsForServer, getAllServers, getConnectedServers } from "../mcp-state";

// GET - List all MCP servers with their current status
export async function GET() {
  try {
    const servers = getAllServers();
    
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

// POST - Add a new MCP server
export async function POST(req: NextRequest) {
  try {
    const { name, command, args, transport = 'stdio' } = await req.json();

    if (!name || !command || !args) {
      return NextResponse.json(
        { error: 'Missing required fields: name, command, args' },
        { status: 400 }
      );
    }

    const newServer = {
      id: name.toLowerCase().replace(/\s+/g, '-'),
      name,
      command,
      args: Array.isArray(args) ? args : [args],
      transport,
      status: 'disconnected',
      tools: getToolsForServer(name)
    };

    const configuredServers = getConfiguredServers();
    configuredServers.set(name, newServer);

    console.log(`MCP Server added: ${name}`);

    return NextResponse.json({
      server: newServer,
      message: `MCP server ${name} added successfully`
    });

  } catch (error) {
    console.error('Error adding MCP server:', error);
    return NextResponse.json(
      { error: 'Failed to add MCP server' },
      { status: 500 }
    );
  }
}

// DELETE - Remove an MCP server
export async function DELETE(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const id = searchParams.get('id');

    if (!id) {
      return NextResponse.json(
        { error: 'Server ID required' },
        { status: 400 }
      );
    }

    const configuredServers = getConfiguredServers();
    const connectedServers = getConnectedServers();

    // Find server by ID
    let serverToRemove = null;
    for (const [name, server] of configuredServers.entries()) {
      if (server.id === id) {
        serverToRemove = { name, server };
        break;
      }
    }

    if (!serverToRemove) {
      return NextResponse.json(
        { error: 'Server not found' },
        { status: 404 }
      );
    }

    // Remove from both configured and connected servers
    configuredServers.delete(serverToRemove.name);
    connectedServers.delete(serverToRemove.name);

    console.log(`MCP Server removed: ${serverToRemove.name}`);

    return NextResponse.json({
      server: serverToRemove.server,
      message: `MCP server ${serverToRemove.name} removed successfully`
    });

  } catch (error) {
    console.error('Error removing MCP server:', error);
    return NextResponse.json(
      { error: 'Failed to remove MCP server' },
      { status: 500 }
    );
  }
}
