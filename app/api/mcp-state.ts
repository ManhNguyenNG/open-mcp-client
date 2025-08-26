// Shared state for MCP servers
import fs from "fs";
import path from "path";

const STATE_FILE = path.join(process.cwd(), ".mcp-state.json");

function readStateFile(): { connected: Record<string, any> } {
  try {
    if (fs.existsSync(STATE_FILE)) {
      const raw = fs.readFileSync(STATE_FILE, "utf-8");
      return JSON.parse(raw) as { connected: Record<string, any> };
    }
  } catch {}
  return { connected: {} };
}

function writeStateFile(connected: Map<string, any>) {
  try {
    const obj: Record<string, any> = {};
    for (const [k, v] of connected.entries()) obj[k] = v;
    fs.writeFileSync(STATE_FILE, JSON.stringify({ connected: obj }), "utf-8");
  } catch {}
}

class MCPState {
  private configuredServers = new Map<string, any>();
  private connectedServers = new Map<string, any>();

  constructor() {
    // Initialize with some default servers
    this.configuredServers.set('Math Server', {
      id: 'math-server',
      name: 'Math Server',
      command: 'python',
      args: ['agent/math_server.py'],
      transport: 'stdio',
      status: 'disconnected',
      tools: ['add', 'multiply']
    });

    this.configuredServers.set('Conversion Server', {
      id: 'conversion-server',
      name: 'Conversion Server',
      command: 'python',
      args: ['agent/conversion_server.py'],
      transport: 'stdio',
      status: 'disconnected',
      tools: ['celsius_to_fahrenheit', 'fahrenheit_to_celsius', 'meters_to_feet', 'kilometers_to_miles']
    });

    this.configuredServers.set('Scientific Server', {
      id: 'scientific-server',
      name: 'Scientific Server',
      command: 'python',
      args: ['agent/scientific_server.py'],
      transport: 'stdio',
      status: 'disconnected',
      tools: ['square_root', 'power', 'factorial', 'sine', 'cosine']
    });

    this.configuredServers.set('Statistics Server', {
      id: 'stats-server',
      name: 'Statistics Server',
      command: 'python',
      args: ['agent/stats_server.py'],
      transport: 'stdio',
      status: 'disconnected',
      tools: ['mean', 'median', 'standard_deviation', 'variance', 'correlation']
    });

    // Load persisted connections
    const persisted = readStateFile();
    for (const name of Object.keys(persisted.connected || {})) {
      this.connectedServers.set(name, persisted.connected[name]);
    }
  }

  private persist() {
    writeStateFile(this.connectedServers);
  }

  getConfiguredServers() {
    return this.configuredServers;
  }

  getConnectedServers() {
    // Refresh from disk in case another worker wrote it
    const persisted = readStateFile();
    this.connectedServers = new Map<string, any>(Object.entries(persisted.connected || {}));
    return this.connectedServers;
  }

  setConnectedServer(name: string, server: any) {
    this.connectedServers.set(name, server);
    this.persist();
    console.log(`MCP State: Connected server ${name}`);
  }

  removeConnectedServer(name: string) {
    this.connectedServers.delete(name);
    this.persist();
    console.log(`MCP State: Disconnected server ${name}`);
  }

  getAllServers() {
    // Ensure we have the latest
    const connected = this.getConnectedServers();

    const servers = Array.from(this.configuredServers.values()).map(server => {
      const connectedServer = connected.get(server.name);
      if (connectedServer) {
        return {
          ...server,
          status: 'connected',
          connectedAt: connectedServer.connectedAt,
          tools: connectedServer.tools
        };
      }
      return server;
    });
    
    console.log('MCP State: Configured servers:', Array.from(this.configuredServers.keys()));
    console.log('MCP State: Connected servers:', Array.from(connected.keys()));
    console.log('MCP State: Returning servers:', servers.map(s => ({ name: s.name, status: s.status })));
    
    return servers;
  }
}

// Create a singleton instance
const mcpState = new MCPState();

// Helper function to get tools for each server type
export function getToolsForServer(serverName: string): string[] {
  const serverNameLower = serverName.toLowerCase();
  
  if (serverNameLower.includes('math')) {
    return ['add', 'multiply'];
  } else if (serverNameLower.includes('conversion')) {
    return ['celsius_to_fahrenheit', 'fahrenheit_to_celsius', 'meters_to_feet', 'kilometers_to_miles'];
  } else if (serverNameLower.includes('scientific')) {
    return ['square_root', 'power', 'factorial', 'sine', 'cosine'];
  } else if (serverNameLower.includes('statistics') || serverNameLower.includes('stats')) {
    return ['mean', 'median', 'standard_deviation', 'variance', 'correlation'];
  } else {
    return ['unknown_tools'];
  }
}

// Export functions to manage the state
export function setConnectedServer(name: string, server: any) {
  mcpState.setConnectedServer(name, server);
}

export function removeConnectedServer(name: string) {
  mcpState.removeConnectedServer(name);
}

export function getConnectedServers() {
  return mcpState.getConnectedServers();
}

export function getConfiguredServers() {
  return mcpState.getConfiguredServers();
}

export function getAllServers() {
  return mcpState.getAllServers();
}
