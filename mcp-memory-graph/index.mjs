#!/usr/bin/env node
/**
 * MCP Memory Graph - Knowledge graph integration via MCP protocol
 */

import { spawn } from 'child_process';
import { homedir } from 'os';
import { join } from 'path';

// Configuration
const MCP_SERVER_PATH = process.env.MCP_MEMORY_SERVER || join(
  homedir(),
  '.openclaw/workspace/mcp-servers/src/memory/dist/index.js'
);

/**
 * MCP Client - communicates with memory server via stdio
 */
class MCPMemoryClient {
  constructor() {
    this.process = null;
    this.requestId = 0;
    this.pendingRequests = new Map();
  }

  /**
   * Start MCP server
   */
  async start() {
    return new Promise((resolve, reject) => {
      this.process = spawn('node', [MCP_SERVER_PATH], {
        stdio: ['pipe', 'pipe', 'pipe']
      });

      let buffer = '';

      this.process.stdout.on('data', (data) => {
        buffer += data.toString();
        
        // Process complete JSON-RPC messages
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (!line.trim()) continue;
          
          try {
            const message = JSON.parse(line);
            
            if (message.id && this.pendingRequests.has(message.id)) {
              const { resolve, reject } = this.pendingRequests.get(message.id);
              this.pendingRequests.delete(message.id);
              
              if (message.error) {
                reject(new Error(message.error.message));
              } else {
                resolve(message.result);
              }
            }
          } catch (error) {
            console.error('Failed to parse message:', line, error);
          }
        }
      });

      this.process.stderr.on('data', (data) => {
        console.error('MCP Server error:', data.toString());
      });

      this.process.on('error', reject);
      this.process.on('exit', (code) => {
        if (code !== 0) {
          console.error(`MCP Server exited with code ${code}`);
        }
      });

      // Wait for server to be ready
      setTimeout(resolve, 1000);
    });
  }

  /**
   * Send JSON-RPC request
   */
  async request(method, params = {}) {
    return new Promise((resolve, reject) => {
      const id = ++this.requestId;
      
      const message = {
        jsonrpc: '2.0',
        id,
        method,
        params
      };

      this.pendingRequests.set(id, { resolve, reject });

      this.process.stdin.write(JSON.stringify(message) + '\n');

      // Timeout after 10s
      setTimeout(() => {
        if (this.pendingRequests.has(id)) {
          this.pendingRequests.delete(id);
          reject(new Error('Request timeout'));
        }
      }, 10000);
    });
  }

  /**
   * Stop MCP server
   */
  stop() {
    if (this.process) {
      this.process.kill();
      this.process = null;
    }
  }
}

/**
 * High-level API
 */
export async function addEntity(name, description, type = 'entity') {
  const client = new MCPMemoryClient();
  
  try {
    await client.start();
    
    const result = await client.request('tools/call', {
      name: 'create_entities',
      arguments: {
        entities: [{
          name,
          entityType: type,
          observations: [description]
        }]
      }
    });

    return result;
  } finally {
    client.stop();
  }
}

export async function addRelation(from, relation, to, type = 'relation') {
  const client = new MCPMemoryClient();
  
  try {
    await client.start();
    
    const result = await client.request('tools/call', {
      name: 'create_relations',
      arguments: {
        relations: [{
          from,
          to,
          relationType: relation
        }]
      }
    });

    return result;
  } finally {
    client.stop();
  }
}

export async function search(query) {
  const client = new MCPMemoryClient();
  
  try {
    await client.start();
    
    const result = await client.request('tools/call', {
      name: 'search_nodes',
      arguments: {
        query
      }
    });

    return result;
  } finally {
    client.stop();
  }
}

export async function openNodes(names) {
  const client = new MCPMemoryClient();
  
  try {
    await client.start();
    
    const result = await client.request('tools/call', {
      name: 'open_nodes',
      arguments: {
        names
      }
    });

    return result;
  } finally {
    client.stop();
  }
}

/**
 * CLI
 */
async function main() {
  const command = process.argv[2];
  const args = process.argv.slice(3);

  try {
    switch (command) {
      case 'add-entity': {
        const [name, description, type] = args;
        if (!name || !description) {
          console.error('Usage: node index.mjs add-entity <name> <description> [type]');
          process.exit(1);
        }
        const result = await addEntity(name, description, type);
        console.log('Entity created:', result);
        break;
      }

      case 'add-relation': {
        const [from, relation, to, type] = args;
        if (!from || !relation || !to) {
          console.error('Usage: node index.mjs add-relation <from> <relation> <to> [type]');
          process.exit(1);
        }
        const result = await addRelation(from, relation, to, type);
        console.log('Relation created:', result);
        break;
      }

      case 'search': {
        const [query] = args;
        if (!query) {
          console.error('Usage: node index.mjs search <query>');
          process.exit(1);
        }
        const result = await search(query);
        console.log('Search results:', JSON.stringify(result, null, 2));
        break;
      }

      case 'open': {
        if (args.length === 0) {
          console.error('Usage: node index.mjs open <name1> [name2] ...');
          process.exit(1);
        }
        const result = await openNodes(args);
        console.log('Nodes:', JSON.stringify(result, null, 2));
        break;
      }

      default:
        console.log(`
MCP Memory Graph CLI

Usage:
  node index.mjs add-entity <name> <description> [type]
  node index.mjs add-relation <from> <relation> <to> [type]
  node index.mjs search <query>
  node index.mjs open <name1> [name2] ...

Examples:
  node index.mjs add-entity "OpenClaw" "AI assistant framework" "software"
  node index.mjs add-relation "OpenClaw" "uses" "Claude" "dependency"
  node index.mjs search "OpenClaw"
  node index.mjs open "OpenClaw" "Claude"

Environment:
  MCP_MEMORY_SERVER=${MCP_SERVER_PATH}
        `);
        break;
    }
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

// Run CLI if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}
