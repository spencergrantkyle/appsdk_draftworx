declare module "@modelcontextprotocol/sdk/dist/server/index.js" {
  export class Server {
    constructor(info: any, capabilities: any);
    connect(transport: any): Promise<void>;
    close(): Promise<void>;
    setRequestHandler(schema: any, handler: any): void;
  }
}

declare module "@modelcontextprotocol/sdk/dist/server/sse.js" {
  export class SSEServerTransport {
    constructor(path: string, response: any);
    readonly sessionId: string;
    onclose?: () => Promise<void> | void;
    onerror?: (error: unknown) => void;
    handlePostMessage(req: any, res: any): Promise<void>;
  }
}

declare module "@modelcontextprotocol/sdk/dist/types.js" {
  export const CallToolRequestSchema: any;
  export const ListToolsRequestSchema: any;
  export type CallToolRequest = any;
  export type ListToolsRequest = any;
  export type Tool = any;
}
