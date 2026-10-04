import { useState, useRef, useEffect, useCallback } from "react";
import { useParams, useLocation } from "wouter";
import {
  useGetSession,
  getGetSessionQueryKey,
  useListMessages,
  getListMessagesQueryKey,
  useCreateMessage,
  useDeleteSession,
  getGetStatsQueryKey,
} from "@workspace/api-client-react";
import { Layout } from "@/components/layout";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Loader2, Send, Terminal, Trash2, ArrowLeft, Bot, Pencil } from "lucide-react";
import { useQueryClient } from "@tanstack/react-query";
import { format } from "date-fns";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { toast } from "sonner";

export default function Chat() {
  const params = useParams();
  const sessionId = parseInt(params.id || "0", 10);
  const [, setLocation] = useLocation();
  const queryClient = useQueryClient();

  const [input, setInput] = useState("");
  const [streamingContent, setStreamingContent] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  const {
    data: session,
    isLoading: isLoadingSession,
    isError: isSessionError,
  } = useGetSession(sessionId, {
    query: { enabled: !!sessionId, queryKey: getGetSessionQueryKey(sessionId) },
  });

  const { data: messages, isLoading: isLoadingMessages } = useListMessages(sessionId, {
    query: { enabled: !!sessionId, queryKey: getListMessagesQueryKey(sessionId) },
  });

  const createMessage = useCreateMessage();
  const deleteSession = useDeleteSession();

  const scrollToBottom = useCallback(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingContent, scrollToBottom]);

  const callAI = async (chatMessages: { role: string; content: string }[]) => {
    setIsStreaming(true);
    setStreamingContent("");
    abortRef.current = new AbortController();

    try {
      const res = await fetch("/api/ai/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: chatMessages,
          model: "opencode/qwen3.7-plus",
        }),
        signal: abortRef.current.signal,
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ error: "AI request failed" }));
        toast.error(err.error || "AI failed");
        setIsStreaming(false);
        return;
      }

      const reader = res.body?.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let fullText = "";

      if (!reader) {
        setIsStreaming(false);
        return;
      }

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed.startsWith("data: ")) continue;
          const data = trimmed.slice(6);
          if (data === "[DONE]") continue;

          try {
            const parsed = JSON.parse(data);
            if (parsed.content) {
              fullText += parsed.content;
              setStreamingContent(fullText);
            }
            if (parsed.done) {
              break;
            }
          } catch {
            // ignore
          }
        }
      }

      // Save assistant response
      createMessage.mutate(
        { id: sessionId, data: { role: "assistant", content: fullText } },
        {
          onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: getListMessagesQueryKey(sessionId) });
            queryClient.invalidateQueries({ queryKey: getGetStatsQueryKey() });
          },
        },
      );
    } catch (err) {
      if ((err as Error).name !== "AbortError") {
        toast.error("AI stream failed");
      }
    } finally {
      setIsStreaming(false);
      setStreamingContent("");
    }
  };

  const handleSend = () => {
    if (!input.trim() || createMessage.isPending || isStreaming) return;
    const content = input.trim();
    setInput("");

    createMessage.mutate(
      { id: sessionId, data: { role: "user", content } },
      {
        onSuccess: () => {
          queryClient.invalidateQueries({ queryKey: getListMessagesQueryKey(sessionId) });
          queryClient.invalidateQueries({ queryKey: getGetStatsQueryKey() });

          // Build message history for AI
          const history = (messages || []).map((m) => ({ role: m.role, content: m.content }));
          history.push({ role: "user", content });
          callAI(history);
        },
      },
    );
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleDelete = () => {
    deleteSession.mutate(
      { id: sessionId },
      {
        onSuccess: () => {
          toast.success("Session deleted");
          setLocation("/");
        },
        onError: () => {
          toast.error("Failed to delete session");
        },
      },
    );
  };

  if (isLoadingSession || isLoadingMessages) {
    return (
      <Layout>
        <div className="flex-1 flex items-center justify-center">
          <div className="flex flex-col items-center gap-4 text-muted-foreground">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
            <p className="font-mono text-sm">Loading session...</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (isSessionError || !session) {
    return (
      <Layout>
        <div className="flex-1 flex flex-col items-center justify-center p-6 text-center">
          <div className="w-16 h-16 rounded-full bg-destructive/10 flex items-center justify-center text-destructive mb-6">
            <Terminal className="w-8 h-8" />
          </div>
          <h2 className="text-2xl font-semibold mb-2">Session not found</h2>
          <p className="text-muted-foreground mb-6 max-w-md">
            This session may have been deleted or doesn't exist.
          </p>
          <Button onClick={() => setLocation("/")} variant="outline" className="gap-2">
            <ArrowLeft className="w-4 h-4" />
            Back to Dashboard
          </Button>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="flex flex-col h-[calc(100dvh-57px)] w-full relative">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-border/50 bg-background/95 backdrop-blur-sm z-10">
          <div className="flex items-center gap-3 min-w-0">
            <Button variant="ghost" size="icon" onClick={() => setLocation("/")} className="shrink-0 text-muted-foreground hover:text-foreground">
              <ArrowLeft className="w-4 h-4" />
            </Button>
            <div className="flex flex-col min-w-0">
              <h2 className="font-mono font-medium text-sm md:text-base leading-tight truncate">{session.title}</h2>
              <span className="text-xs text-muted-foreground font-mono">
                ID: {session.id} • {format(new Date(session.createdAt), "MMM d, HH:mm")}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-1">
            <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-foreground shrink-0">
              <Pencil className="w-4 h-4" />
            </Button>
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-destructive hover:bg-destructive/10 shrink-0">
                  <Trash2 className="w-4 h-4" />
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent className="border-border bg-card">
                <AlertDialogHeader>
                  <AlertDialogTitle className="font-mono">Delete session?</AlertDialogTitle>
                  <AlertDialogDescription>
                    This will permanently delete "{session.title}" and all its messages. This cannot be undone.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                  <AlertDialogAction onClick={handleDelete} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
                    Delete
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-5" ref={scrollRef}>
          {messages?.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-muted-foreground/60">
              <Bot className="w-12 h-12 mb-4" />
              <p className="font-mono text-sm">Ready. Ask me anything.</p>
            </div>
          ) : (
            messages?.map((msg) => {
              const isUser = msg.role === "user";
              return (
                <div
                  key={msg.id}
                  className={`flex flex-col max-w-[85%] ${isUser ? "ml-auto items-end" : "mr-auto items-start"}`}
                >
                  <div className="flex items-center gap-2 mb-1 px-1 opacity-60">
                    {isUser ? (
                      <>
                        <span className="text-[10px] font-mono text-muted-foreground">{format(new Date(msg.createdAt), "HH:mm")}</span>
                        <span className="text-xs font-mono font-bold text-primary uppercase">You</span>
                      </>
                    ) : (
                      <>
                        <Bot className="w-3 h-3 text-secondary-foreground" />
                        <span className="text-xs font-mono font-bold text-secondary-foreground uppercase">Assistant</span>
                        <span className="text-[10px] font-mono text-muted-foreground">{format(new Date(msg.createdAt), "HH:mm")}</span>
                      </>
                    )}
                  </div>
                  <div className={`
                    px-4 py-3 rounded-xl text-sm md:text-base leading-relaxed break-words whitespace-pre-wrap
                    ${isUser
                      ? "bg-primary text-primary-foreground rounded-tr-sm"
                      : "bg-secondary border border-border/50 text-secondary-foreground rounded-tl-sm font-mono text-sm"
                    }
                  `}>
                    {msg.content}
                  </div>
                </div>
              );
            })
          )}
          {isStreaming && (
            <div className="flex flex-col max-w-[85%] mr-auto items-start">
              <div className="flex items-center gap-2 mb-1 px-1 opacity-60">
                <Bot className="w-3 h-3 text-secondary-foreground" />
                <span className="text-xs font-mono font-bold text-secondary-foreground uppercase">Assistant</span>
                <span className="text-[10px] font-mono text-muted-foreground">{format(new Date(), "HH:mm")}</span>
              </div>
              <div className="px-4 py-3 rounded-xl bg-secondary border border-border/50 text-secondary-foreground rounded-tl-sm font-mono text-sm min-h-[44px]">
                {streamingContent || (
                  <span className="inline-flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: "0ms" }} />
                    <span className="w-1.5 h-1.5 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: "150ms" }} />
                    <span className="w-1.5 h-1.5 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: "300ms" }} />
                  </span>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Input */}
        <div className="p-4 bg-background border-t border-border/50 shrink-0">
          <div className="max-w-4xl mx-auto relative group">
            <div className="absolute -inset-0.5 bg-primary/20 rounded-xl blur opacity-0 group-focus-within:opacity-100 transition duration-500 pointer-events-none" />
            <div className="relative flex items-end gap-2 bg-card border border-border rounded-lg p-2 focus-within:border-primary/50 transition-colors shadow-sm">
              <Textarea
                placeholder="Ask a question..."
                className="min-h-[44px] max-h-32 resize-none border-0 focus-visible:ring-0 shadow-none bg-transparent font-mono text-sm px-2 py-3"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={createMessage.isPending || isStreaming}
              />
              <Button
                size="icon"
                onClick={handleSend}
                disabled={!input.trim() || createMessage.isPending || isStreaming}
                className="h-[44px] w-[44px] shrink-0 rounded-md bg-primary text-primary-foreground hover:bg-primary/90 transition-all active:scale-95"
              >
                <Send className="w-4 h-4 ml-0.5" />
              </Button>
            </div>
          </div>
          <div className="text-center mt-2">
            <span className="text-[10px] font-mono text-muted-foreground uppercase tracking-wider">
              {isStreaming ? "AI is responding..." : "Shift + Enter for new line"}
            </span>
          </div>
        </div>
      </div>
    </Layout>
  );
}
