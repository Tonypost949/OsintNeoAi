import { streamText, tool } from "ai";
import { createOpenAI } from "@ai-sdk/openai";
import { z } from "zod/v4";
import { ENV } from "./env";
import { createPatchedFetch } from "./patchedFetch";
// In-memory session store
const sessionStore = new Map<string, any[]>();

export interface GenkitAgentConfig {
  name: string;
  systemInstruction: string;
  tools: Record<string, any>;
  interruptTools?: string[]; // Tools requiring human approval
}

export class GenkitAgent {
  name: string;
  systemInstruction: string;
  tools: Record<string, any>;
  interruptTools: string[];
  private provider: any;

  constructor(config: GenkitAgentConfig) {
    this.name = config.name;
    this.systemInstruction = config.systemInstruction;
    this.tools = config.tools;
    this.interruptTools = config.interruptTools || [];

    const baseURL = ENV.forgeApiUrl.endsWith("/v1")
      ? ENV.forgeApiUrl
      : `${ENV.forgeApiUrl}/v1`;

    this.provider = createOpenAI({
      baseURL,
      apiKey: ENV.forgeApiKey,
      fetch: createPatchedFetch(fetch),
    });
  }

  /**
   * Retrieves or initializes the message history for a given session.
   */
  private getSessionHistory(sessionId: string): any[] {
    const sessionKey = `agent_session:${this.name}:${sessionId}`;
    let history = sessionStore.get(sessionKey);
    if (!history) {
      history = [];
      sessionStore.set(sessionKey, history);
    }
    return history;
  }

  /**
   * Saves updated message history for a session.
   */
  private saveSessionHistory(sessionId: string, history: any[]) {
    const sessionKey = `agent_session:${this.name}:${sessionId}`;
    sessionStore.set(sessionKey, history);
  }

  /**
   * Runs the chat loop, executing tools, handling persistence, and checking interrupts.
   */
  async chat(sessionId: string, userMessage: string, approvedToolCallId?: string) {
    const history = this.getSessionHistory(sessionId);
    
    // Add user message if not just resuming from an approved interrupt
    if (!approvedToolCallId) {
      history.push({ role: "user", content: userMessage });
    }

    const wrappedTools: Record<string, any> = {};

    // Wrap tools to support human-in-the-loop validation
    for (const [name, t] of Object.entries(this.tools)) {
      wrappedTools[name] = tool({
        description: t.description || "",
        parameters: t.inputSchema || t.parameters || z.object({}),
        execute: async (args: any) => {
          // Check if this tool requires human approval
          if (this.interruptTools.includes(name)) {
            // Generate a unique execution placeholder
            throw new Error(`INTERRUPTED: Tool '${name}' requires user approval.`);
          }
          return await t.execute(args);
        }
      } as any);
    }

    try {
      const response = await streamText({
        model: this.provider.chat("gpt-4o"),
        system: this.systemInstruction,
        messages: history,
        tools: wrappedTools,
      });

      const text = await response.text;
      
      // Save assistant message to local session history
      history.push({ role: "assistant", content: text });
      this.saveSessionHistory(sessionId, history);

      return {
        status: "success",
        text,
        history
      };

    } catch (err: any) {
      if (err.message && err.message.includes("INTERRUPTED")) {
        return {
          status: "interrupted",
          error: err.message,
          message: "This action requires your confirmation before execution.",
          history
        };
      }
      throw err;
    }
  }
}
