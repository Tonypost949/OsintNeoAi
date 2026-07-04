/**
 * AIChatBox Component
 *
 * A production-ready chat component built on AI SDK v6's useChat hook.
 *
 * ## Architecture
 *
 * This component follows a "controlled by React Query" pattern:
 * - Messages are loaded from your data layer (e.g., tRPC/React Query)
 * - Passed to this component as `initialMessages`
 * - On chat completion, `onFinish` callback lets you update your cache
 * - Chat switching is handled via `setMessages` when props change
 *
 * ## Usage
 *
 * ```tsx
 * // In your page component
 * const messagesQuery = trpc.chat.loadMessages.useQuery({ chatId });
 * const trpcUtils = trpc.useUtils();
 *
 * <AIChatBox
 *   chatId={chatId}
 *   initialMessages={messagesQuery.data ?? []}
 *   onFinish={(messages) => {
 *     // Update React Query cache with final messages
 *     trpcUtils.chat.loadMessages.setData({ chatId }, messages);
 *   }}
 * />
 * ```
 *
 * ## Tool Rendering
 *
 * Customize how tool invocations appear in the chat:
 *
 * ```tsx
 * <AIChatBox
 *   renderToolPart={(part) => {
 *     // part.type is `tool-${toolName}` (e.g., "tool-searchPokemon")
 *     // part.state is the tool invocation state
 *     // part.input/output contain the tool data
 *     if (part.type === "tool-searchPokemon") {
 *       return <PokemonResults data={part.output} />;
 *     }
 *     return null; // Use default renderer
 *   }}
 * />
 * ```
 *
 * @see https://sdk.vercel.ai/docs/ai-sdk-ui/chatbot - AI SDK Chat Documentation
 */

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Markdown } from "@/components/Markdown";
import { cn } from "@/lib/utils";
import { Loader2, Send, Sparkles } from "lucide-react";
import { useState, useRef, useEffect, ReactNode } from "react";
import { useChat } from "@ai-sdk/react";
import { DefaultChatTransport } from "ai";

// ============================================================================
// TYPES
// Note: For AI SDK types like UIMessage, UIMessagePart, ChatStatus,
// import them directly from "ai" package in your consuming code.
// ============================================================================

import type { UIMessage, UIMessagePart, UIToolInvocation } from "ai";

/**
 * Tool invocation state derived from AI SDK's UIToolInvocation type.
 * Represents the lifecycle of a tool call.
 */
export type ToolInvocationState = UIToolInvocation<any>["state"];

/**
 * Helper to check if a tool is still loading (input phase)
 */
export function isToolLoading(state: ToolInvocationState): boolean {
  return state === "input-streaming" || state === "input-available";
}

/**
 * Helper to check if a tool has errored
 */
export function isToolError(state: ToolInvocationState): boolean {
  return state === "output-error";
}

/**
 * Helper to check if a tool completed successfully
 */
export function isToolComplete(state: ToolInvocationState): boolean {
  return state === "output-available";
}

// ============================================================================
// COMPONENT PROPS
// ============================================================================

/**
 * Props for custom tool part rendering.
 * The `part` object contains the full tool invocation data from AI SDK.
 */
export interface ToolPartRendererProps {
  /** The tool part from the message - type is `tool-${toolName}` */
  part: UIMessagePart & { type: `tool-${string}` };
  /** Extracted tool name for convenience */
  toolName: string;
  /** Current state of the tool invocation */
  state: ToolInvocationState;
  /** Tool input (available after input-streaming) */
  input?: unknown;
  /** Tool output (available when state is output-available) */
  output?: unknown;
  /** Error text (available when state is output-error) */
  errorText?: string;
}

export type ToolPartRenderer = (props: ToolPartRendererProps) => ReactNode;

export interface AIChatBoxProps {
  /** API endpoint for chat (default: "/api/chat") */
  api?: string;

  /** Unique chat ID - changing this triggers message sync */
  chatId: string;

  /** Optional user ID to send with requests */
  userId?: number;

  /**
   * Initial messages loaded from your data layer.
   * When this changes (e.g., switching chats), messages are synced via setMessages.
   */
  initialMessages: UIMessage[];

  /**
   * Called when chat completes (streaming finished).
   * Use this to update your React Query cache or persist messages.
   */
  onFinish?: (messages: UIMessage[]) => void;

  /**
   * Custom renderer for tool parts.
   * Return null to use the default JSON renderer.
   */
  renderToolPart?: ToolPartRenderer;

  /** Placeholder text for the input field */
  placeholder?: string;

  /** Additional CSS classes for the container */
  className?: string;

  /** Message shown when chat is empty */
  emptyStateMessage?: string;

  /** Suggested prompts shown in empty state */
  suggestedPrompts?: string[];
}

// ============================================================================
// DEFAULT TOOL RENDERER
// ============================================================================

function DefaultToolPartRenderer({ toolName, state, output, errorText }: ToolPartRendererProps) {
  if (isToolLoading(state)) {
    return (
      <div className="flex items-center gap-2 p-3 bg-muted/50 rounded-lg my-2">
        <Loader2 className="size-4 animate-spin" />
        <span className="text-sm text-muted-foreground">Running {toolName}...</span>
      </div>
    );
  }

  if (isToolError(state)) {
    return (
      <div className="p-3 bg-destructive/10 rounded-lg my-2 text-sm text-destructive">
        Error: {errorText || "Tool execution failed"}
      </div>
    );
  }

  if (isToolComplete(state) && output) {
    return (
      <div className="p-3 bg-muted rounded-lg my-2">
        <pre className="text-xs overflow-auto max-h-40">
          {JSON.stringify(output, null, 2)}
        </pre>
      </div>
    );
  }

  return null;
}

// ============================================================================
// MESSAGE BUBBLE
// ============================================================================

function MessageBubble({
  message,
  renderToolPart,
  isStreaming,
}: {
  message: UIMessage;
  renderToolPart: ToolPartRenderer;
  isStreaming: boolean;
}) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "flex gap-3",
        isUser ? "justify-end items-start" : "justify-start items-start"
      )}
    >
      {/* Assistant avatar */}
      {!isUser && (
        <div className="size-8 shrink-0 mt-1 rounded-full bg-primary/10 flex items-center justify-center">
          <Sparkles className="size-4 text-primary" />
        </div>
      )}

      {/* Message content */}
      <div
        className={cn(
          "max-w-[80%] rounded-lg px-4 py-2.5",
          isUser ? "bg-primary text-primary-foreground" : "bg-muted text-foreground"
        )}
      >
        {message.parts.map((part, i) => {
          // Text parts - render with Markdown
          if (part.type === "text") {
            // Show loading indicator for empty text during streaming
            if (isStreaming && !part.text) {
              return (
                <div key={i} className="flex items-center gap-2">
                  <Loader2 className="size-4 animate-spin" />
                  <span className="text-sm text-muted-foreground">Thinking...</span>
                </div>
              );
            }
            return (
              <div key={i} className="prose prose-sm dark:prose-invert max-w-none">
                <Markdown mode={isStreaming ? "typewriter" : "static"} typewriterSpeed={50}>
                  {part.text}
                </Markdown>
              </div>
            );
          }

          // Tool parts - type is `tool-${toolName}`
          if (part.type.startsWith("tool-")) {
            const toolName = part.type.replace("tool-", "");
            // Cast to access tool-specific properties
            const toolPart = part as UIMessagePart & {
              type: `tool-${string}`;
              toolCallId: string;
              state: ToolInvocationState;
              input?: unknown;
              output?: unknown;
              errorText?: string;
            };

            const rendererProps: ToolPartRendererProps = {
              part: toolPart,
              toolName,
              state: toolPart.state,
              input: toolPart.input,
              output: toolPart.output,
              errorText: toolPart.errorText,
            };

            // Try custom renderer first, fall back to default
            const customRender = renderToolPart(rendererProps);
            if (customRender !== null) {
              return <div key={i}>{customRender}</div>;
            }
            return <div key={i}><DefaultToolPartRenderer {...rendererProps} /></div>;
          }

          // Reasoning parts (if using reasoning models)
          if (part.type === "reasoning") {
            return (
              <div key={i} className="text-xs text-muted-foreground italic border-l-2 pl-2 my-2">
                {part.text}
              </div>
            );
          }

          return null;
        })}
      </div>
    </div>
  );
}

// ============================================================================
// THINKING INDICATOR
// ============================================================================

function ThinkingIndicator() {
  return (
    <div className="flex gap-3 justify-start items-start">
      <div className="size-8 shrink-0 mt-1 rounded-full bg-primary/10 flex items-center justify-center">
        <Sparkles className="size-4 text-primary" />
      </div>
      <div className="bg-muted rounded-lg px-4 py-2.5">
        <div className="flex items-center gap-2">
          <Loader2 className="size-4 animate-spin" />
          <span className="text-sm text-muted-foreground">Thinking...</span>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export function AIChatBox({
  api = "/api/chat",
  chatId,
  userId,
  initialMessages,
  onFinish,
  renderToolPart = () => null, // Default returns null to use DefaultToolPartRenderer
  placeholder = "Type your message...",
  className,
  emptyStateMessage = "Start a conversation with AI",
  suggestedPrompts,
}: AIChatBoxProps) {
  const [input, setInput] = useState("");
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // -------------------------------------------------------------------------
  // useChat hook - the core of AI SDK integration
  // -------------------------------------------------------------------------
  const { messages, sendMessage, setMessages, status, error } = useChat({
    // Chat ID helps AI SDK track different conversations
    id: chatId,

    // Initial messages from your data layer (React Query, etc.)
    // Note: This makes it "controlled" - we sync via setMessages on changes
    messages: initialMessages,

    // Transport configuration - how messages are sent to the server
    transport: new DefaultChatTransport({
      api,
      // Customize the request body sent to your server
      prepareSendMessagesRequest({ messages, id }) {
        // Send only the latest message + metadata
        // Server should load full history from DB using chatId
        return {
          body: {
            message: messages[messages.length - 1],
            chatId: chatId || id,
            userId,
          },
        };
      },
    }),

    // Called when streaming completes
    onFinish: ({ messages: finalMessages, isError, isAbort, isDisconnect }) => {
      if (!isError && !isAbort && !isDisconnect) {
        // Notify parent to update cache/persist
        onFinish?.(finalMessages);
      }
    },
  });

  // -------------------------------------------------------------------------
  // Sync messages when chatId or initialMessages change (chat switching)
  // -------------------------------------------------------------------------
  useEffect(() => {
    setMessages(initialMessages);
  }, [chatId, initialMessages, setMessages]);

  // -------------------------------------------------------------------------
  // Derived state
  // -------------------------------------------------------------------------
  const canSend = status === "ready";
  const isStreaming = status === "streaming";
  const lastMessage = messages[messages.length - 1];
  const isWaitingForContent =
    status === "submitted" ||
    (isStreaming && lastMessage?.role === "assistant" && lastMessage?.parts.length === 0);

  // -------------------------------------------------------------------------
  // Auto-scroll on new messages
  // -------------------------------------------------------------------------
  useEffect(() => {
    const viewport = scrollAreaRef.current?.querySelector(
      "[data-radix-scroll-area-viewport]"
    ) as HTMLDivElement;
    if (viewport) {
      requestAnimationFrame(() => {
        viewport.scrollTo({ top: viewport.scrollHeight, behavior: "smooth" });
      });
    }
  }, [messages, status]);

  // -------------------------------------------------------------------------
  // Message submission
  // -------------------------------------------------------------------------
  const submitMessage = () => {
    const trimmedInput = input.trim();
    if (!trimmedInput || !canSend) return;

    // AI SDK v6 sendMessage accepts { text, files? }
    sendMessage({ text: trimmedInput });
    setInput("");
    textareaRef.current?.focus();
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    submitMessage();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submitMessage();
    }
  };

  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------
  return (
    <div className={cn("flex flex-col flex-1 min-h-0", className)}>
      {/* Messages Area */}
      <div ref={scrollAreaRef} className="flex-1 overflow-hidden">
        <ScrollArea className="h-full">
          <div className="mx-auto max-w-3xl space-y-4 p-4">
            {/* Empty state */}
            {messages.length === 0 && !isWaitingForContent ? (
              <div className="flex h-[60vh] flex-col items-center justify-center gap-6 text-muted-foreground">
                <Sparkles className="size-12 opacity-20" />
                <p className="text-center max-w-md">{emptyStateMessage}</p>
                {suggestedPrompts && suggestedPrompts.length > 0 && (
                  <div className="flex flex-wrap justify-center gap-2 max-w-lg">
                    {suggestedPrompts.map((prompt, i) => (
                      <Button
                        key={i}
                        variant="outline"
                        size="sm"
                        className="text-xs"
                        onClick={() => {
                          setInput(prompt);
                          textareaRef.current?.focus();
                        }}
                      >
                        {prompt}
                      </Button>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <>
                {/* Message list */}
                {messages.map((message, index) => {
                  const isLastAssistant =
                    index === messages.length - 1 && message.role === "assistant";
                  const hasContent = message.parts.length > 0;

                  // Skip empty assistant messages (thinking indicator shows instead)
                  if (isLastAssistant && !hasContent) return null;

                  return (
                    <MessageBubble
                      key={message.id}
                      message={message}
                      renderToolPart={renderToolPart}
                      isStreaming={isStreaming && isLastAssistant && hasContent}
                    />
                  );
                })}

                {/* Thinking indicator */}
                {isWaitingForContent && <ThinkingIndicator />}
              </>
            )}

            {/* Error display */}
            {error && (
              <div className="rounded-lg bg-destructive/10 p-4 text-destructive">
                Error: {error.message}
              </div>
            )}
          </div>
        </ScrollArea>
      </div>

      {/* Input Area */}
      <form onSubmit={handleSubmit} className="border-t bg-background/50 p-4">
        <div className="mx-auto max-w-3xl">
          <div className="flex gap-2">
            <Textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={placeholder}
              className="min-h-[44px] max-h-32 resize-none"
              rows={1}
              disabled={!canSend}
            />
            <Button
              type="submit"
              size="icon"
              disabled={!canSend || !input.trim()}
              className="shrink-0 h-[44px] w-[44px]"
            >
              {status === "submitted" ? (
                <Loader2 className="size-4 animate-spin" />
              ) : (
                <Send className="size-4" />
              )}
            </Button>
          </div>
        </div>
      </form>
    </div>
  );
}

export default AIChatBox;
