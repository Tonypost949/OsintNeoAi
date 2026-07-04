# AI SDK v6 + React Query Integration

> **TL;DR**: Split into two components - a parent that manages React Query state and a child that manages `useChat`. Pass `initialMessages` down and `onFinish` up. Use `setData` for optimistic cache updates.

---

## Query Configuration

Chat messages can have a longer `staleTime` since we manually update the cache via `setData` on finish:

```tsx
const messagesQuery = trpc.chat.loadMessages.useQuery(
  { chatId },
  { staleTime: Infinity } // Only refetch when we explicitly invalidate
);
```

---

## Component Architecture

Split your chat into two components to keep concerns separate:

1. **ChatPage** (parent) - Manages React Query, chat switching, URL state
2. **ChatView** (child) - Manages `useChat`, renders messages, handles input

```tsx
// ChatPage.tsx - Parent manages data layer
function ChatPage() {
  const params = useParams<{ id: string }>();
  const trpcUtils = trpc.useUtils();
  const [chatId, setChatId] = useState(() => params.id || nanoid());

  const messagesQuery = trpc.chat.loadMessages.useQuery({ chatId });

  const switchChat = useCallback((newChatId: string) => {
    setChatId(newChatId);
    window.history.replaceState(null, "", `/chat/${newChatId}`);
  }, []);

  const handleFinish = useCallback((finalMessages: UIMessage[]) => {
    trpcUtils.chat.loadMessages.setData({ chatId }, finalMessages);
  }, [chatId, trpcUtils]);

  if (messagesQuery.isLoading) return <LoadingSpinner />;

  return (
    <div className="flex h-screen">
      <ChatSidebar 
        currentChatId={chatId} 
        onSelectChat={switchChat}
        onPrefetch={(id) => trpcUtils.chat.loadMessages.prefetch({ chatId: id })}
      />
      <ChatView
        chatId={chatId}
        initialMessages={messagesQuery.data ?? []}
        onFinish={handleFinish}
      />
    </div>
  );
}
```

```tsx
// ChatView.tsx - Child manages useChat
import { toast } from "sonner";

interface ChatViewProps {
  chatId: string;
  initialMessages: UIMessage[];
  onFinish: (messages: UIMessage[]) => void;
}

function ChatView({ chatId, initialMessages, onFinish }: ChatViewProps) {
  const { messages, sendMessage, setMessages, status } = useChat({
    id: chatId,
    messages: initialMessages,
    transport: new DefaultChatTransport({
      api: "/api/chat",
      prepareSendMessagesRequest({ messages, id }) {
        return {
          body: {
            message: messages[messages.length - 1],
            chatId: chatId || id,
          },
        };
      },
    }),
    onFinish: ({ messages: finalMessages, isError }) => {
      if (!isError) {
        onFinish(finalMessages);
      }
    },
    onError: (error) => {
      toast.error("Failed to send message", {
        description: error.message,
      });
    },
  });

  // Sync messages when switching chats
  useEffect(() => {
    setMessages(initialMessages);
  }, [chatId, initialMessages, setMessages]);

  const handleSend = (text: string) => {
    const parts: UIMessagePart[] = [{ type: "text", text }];
    sendMessage({ parts });
  };

  return (
    <div className="flex-1 flex flex-col">
      <MessageList messages={messages} status={status} />
      <ChatInput onSend={handleSend} disabled={status !== "ready"} />
    </div>
  );
}
```

---

## Parts-Based sendMessage

Always use the `parts` array format for extensibility:

```ts
// Text message
sendMessage({
  parts: [{ type: "text", text: userInput }],
});

// With file attachment (use useFileUpload hook for uploads)
sendMessage({
  parts: [
    { type: "file", url: uploadedUrl, mediaType: "image/png" },
    { type: "text", text: "What's in this image?" },
  ],
});
```

---

## Prefetch on Hover

Prefetch chat messages when hovering over sidebar links for instant switching:

```tsx
function ChatLink({ chat, onSelect, onPrefetch }) {
  return (
    <button
      onMouseEnter={() => onPrefetch(chat.id)}
      onClick={() => onSelect(chat.id)}
    >
      {chat.title}
    </button>
  );
}

// In parent
<ChatSidebar
  onPrefetch={(id) => trpcUtils.chat.loadMessages.prefetch({ chatId: id })}
/>
```

---

## Chat Switching

Use local state + `replaceState` to avoid full page reloads:

```tsx
const [chatId, setChatId] = useState(() => params.id || nanoid());

const switchChat = useCallback((newChatId: string) => {
  setChatId(newChatId);
  window.history.replaceState(null, "", `/chat/${newChatId}`);
}, []);
```

This triggers React Query to fetch new messages → `initialMessages` updates → `setMessages` sync loads them into `useChat`.

---

## AIChatBox Component

The template includes `AIChatBox` (`client/src/components/AIChatBox.tsx`) which implements the ChatView pattern:

```tsx
<AIChatBox
  chatId={chatId}
  initialMessages={messagesQuery.data ?? []}
  onFinish={(messages) => {
    trpcUtils.chat.loadMessages.setData({ chatId }, messages);
  }}
  renderToolPart={({ toolName, state, output }) => {
    // Custom tool rendering
  }}
/>
```

Exports:
- `ToolInvocationState` — Derived from `UIToolInvocation<any>["state"]`
- `ToolPartRendererProps` — Props for custom tool renderers
- `isToolLoading()`, `isToolError()`, `isToolComplete()` — State helpers
