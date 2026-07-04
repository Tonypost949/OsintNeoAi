# AI SDK v6 with Forge API

> **Packages**: `ai@6.x`, `@ai-sdk/react@3.x`, `@ai-sdk/openai@3.x`

## Related Documentation

| Topic | Document |
|-------|----------|
| React Query integration, chat persistence, cache updates | [`ai-sdk-react-query.md`](ai-sdk-react-query.md) |

**Useful Components:**
- [`client/src/components/AIChatBox.tsx`](../client/src/components/AIChatBox.tsx) - Pre-built chat interface
- [`client/src/hooks/useFileUpload.ts`](../client/src/hooks/useFileUpload.ts) - File upload hook for attachments

---

## AI SDK Documentation Lookup

When you need up-to-date information about the AI SDK:

1. Search the docs: `https://ai-sdk.dev/api/search-docs?q=your_query`
2. The response includes matches with links ending in `.md`
3. Fetch those `.md` URLs directly to get plain text content (e.g. `https://ai-sdk.dev/docs/agents/building-agents.md`)

Use this for current API details, examples, and usage patterns.

When no results found, read the source types directly:
- Glob `node_modules/ai/**/*.d.ts` to understand the API
- Prefer reading the actual types over web search results

The AI SDK provides a few different tools for building AI-powered applications. Here are a few patterns that are commonly used. We have examples below that you should refer to.

| Pattern | Hook | Server | Use Case |
|---------|------|--------|----------|
| `useChat` | Multi-turn chat | `createUIMessageStream` | Chatbots, assistants |
| `useCompletion` | Single prompt | `pipeTextStreamToResponse` | Stories, readings, summaries |
| `useObject` | Structured streaming | `streamObject` | Analysis, suggestions |



## Setup

```ts
import { createOpenAI } from "@ai-sdk/openai";
import { createPatchedFetch } from "./patchedFetch";

const openai = createOpenAI({
  apiKey: process.env.BUILT_IN_FORGE_API_KEY,
  baseURL: `${process.env.BUILT_IN_FORGE_API_URL}/v1`,  // Must include /v1
  fetch: createPatchedFetch(),  // Required for Forge API compatibility
});

const model = openai.chat("gemini-2.5-flash");
```

---

## Message Formats

| Format | Used By | Structure |
|--------|---------|-----------|
| **UIMessage** | Frontend, persistence, useChat | `{ id, role, parts: [...] }` |
| **ModelMessage** | LLM APIs (streamText, generateText) | `{ role, content }` |

Convert before sending to LLM:

```ts
import { convertToModelMessages } from "ai";
const modelMessages = await convertToModelMessages(uiMessages);
```

---

## UIMessage Structure

```ts
interface UIMessage {
  id: string;
  role: "user" | "assistant" | "system";
  parts: Array<
    | { type: "text"; text: string }
    | { type: "file"; url: string; mediaType: string }
    | { 
        type: `tool-${string}`;  // e.g., "tool-getWeather"
        toolCallId: string;
        state: ToolInvocationState;
        input?: unknown;   // Tool arguments (NOT `args`)
        output?: unknown;  // Tool result (NOT `result`)
        errorText?: string;
      }
  >;
}
```

---

## Rendering Markdown

Use the `Markdown` component we ship with instead of Streamdown directly - it has proper styles, syntax highlighting, and streaming support:

```tsx
import { Markdown } from "@/components/Markdown";

// For streaming AI responses
<Markdown mode="streaming" isAnimating={isStreaming}>
  {part.text}
</Markdown>

// For static content
<Markdown mode="static">{content}</Markdown>
```

---

## Image/File Handling

Upload files to storage first, then use the URL in message parts. `convertToModelMessages` handles file URLs automatically.

```ts
// 1. Upload file using the useFileUpload hook we ship with
import { useFileUpload } from "@/hooks/useFileUpload";

const { uploadFile, isUploading } = useFileUpload();
const uploadedUrl = await uploadFile(file);

// 2. Add to message parts
sendMessage({
  parts: [
    { type: "file", url: uploadedUrl, mediaType: file.type },
    { type: "text", text: "What's in this image?" },
  ],
});

// 3. Backend: convertToModelMessages handles files automatically
const modelMessages = await convertToModelMessages(messages);
// Files are converted to the format the LLM expects
```

---

## Database Schema

Store `UIMessage` objects as JSON with an explicit ordering column:

```ts
export const messages = mysqlTable("messages", {
  id: varchar("id", { length: 36 }).primaryKey(),
  chatId: varchar("chatId", { length: 36 }).notNull(),
  content: json("content").notNull(),  // Full UIMessage object
  ordering: int("ordering").notNull(), // Explicit order, not timestamp
  createdAt: timestamp("createdAt").defaultNow(),
});
```

Use `ordering` instead of `createdAt` because MySQL timestamp precision can cause collisions when messages are saved in rapid succession.

---

## Server Streaming Endpoint

Use Express for streaming (tRPC doesn't handle SSE well). Always prefer streaming over non-streaming calls for better UX.

```ts
import { Router } from "express";
import {
  streamText, convertToModelMessages, pipeUIMessageStreamToResponse,
  createUIMessageStream, generateId, stepCountIs,
} from "ai";

const router = Router();

router.post("/", async (req, res) => {
  const { message, chatId } = req.body;

  // appendMessage handles chat creation and ordering internally
  await appendMessage({ chatId, message });
  const previousMessages = await loadChat(chatId);

  const stream = createUIMessageStream({
    execute: async ({ writer }) => {
      writer.write({ type: "start", messageId: generateId() });

      const modelMessages = await convertToModelMessages(previousMessages);

      const result = streamText({
        model: openai.chat("gemini-2.5-flash"),
        system: "You are a helpful assistant.",
        messages: modelMessages,
        tools,
        stopWhen: stepCountIs(5),
      });

      result.consumeStream();
      writer.merge(result.toUIMessageStream({ sendStart: false }));
    },
    onFinish: async ({ messages }) => {
      const finalMessage = messages[messages.length - 1];
      if (finalMessage?.role === "assistant") {
        await appendMessage({ chatId, message: finalMessage });
      }
    },
  });

  pipeUIMessageStreamToResponse({ response: res, stream });
});
```

---

## Tool Definition

Use `inputSchema` (not `parameters`):

```ts
import { tool } from "ai";
import { z } from "zod/v4";

export const tools = {
  getWeather: tool({
    description: "Get current weather for a location",
    inputSchema: z.object({
      city: z.string().describe("City name"),
    }),
    execute: async ({ city }) => {
      const data = await fetchWeatherAPI(city);
      return { city, temperature: data.temp, condition: data.condition };
    },
  }),
};
```

---

## Tool States

| State | Meaning | UI |
|-------|---------|-----|
| `input-streaming` | Arguments being streamed | Loading |
| `input-available` | Arguments ready, executing | Loading |
| `output-available` | Completed successfully | Render `output` |
| `output-error` | Failed | Show `errorText` |

Output is in `output` property (not `result`):

```tsx
if (state === "input-streaming" || state === "input-available") {
  return <Spinner />;
}
if (state === "output-error") {
  return <ErrorCard message={errorText} />;
}
if (state === "output-available") {
  return <DataCard data={output} />;
}
```

---

## Loading States

Two distinct phases:

| Phase | Condition | Meaning |
|-------|-----------|---------|
| 1 | `status === "submitted"` | Request sent, waiting for server |
| 2 | `status === "streaming"` with empty parts | Stream started, content arriving |

```tsx
const isWaiting = status === "submitted";

// Phase 1: Show after all messages
{isWaiting && <ThinkingIndicator />}

// Phase 2: Handle in MessageBubble for empty text parts
if (part.type === "text" && !part.text && isStreaming) {
  return <ThinkingIndicator />;
}
```

---

## Simple Streaming Text (`useCompletion`)

For single-prompt streaming text generation (not multi-turn chat) - ideal for stories, tarot readings, summaries, or any long-form text without conversation history.

### Server

```ts
import { Router } from "express";
import { streamText } from "ai";

const router = Router();

router.post("/", async (req, res) => {
  const { prompt, context } = req.body;

  const result = streamText({
    model: openai.chat("gemini-2.5-flash"),
    system: "You are a mystical tarot reader...",
    messages: [{ role: "user", content: prompt }],
    onFinish: async ({ text }) => {
      // Optionally save to database
      await saveToDb(context.id, text);
    },
  });

  result.pipeTextStreamToResponse(res);
});
```

### Client

```tsx
import { useCompletion } from "@ai-sdk/react";

function TarotReading({ readingId }) {
  const { completion, isLoading, complete } = useCompletion({
    api: "/api/interpretation",
    streamProtocol: "text",  // Required for pipeTextStreamToResponse!
  });

  const generateReading = async () => {
    await complete("", { body: { readingId } });
  };

  return (
    <div>
      <Button onClick={generateReading} disabled={isLoading}>
        Reveal Your Reading
      </Button>
      <div className="prose">{completion}</div>
    </div>
  );
}
```

**Key points:**
- `streamProtocol: "text"` is required when using `pipeTextStreamToResponse`
- Pass extra data via `body` in the `complete()` call
- `completion` updates in real-time as text streams in

---

## Streaming Structured Output (`useObject`)

For streaming structured JSON that builds up progressively - ideal for analysis, suggestions, or any structured data where you want to show partial results.

### Server

```ts
import { Router } from "express";
import { streamObject } from "ai";
import { z } from "zod/v4";

const router = Router();

const suggestionsSchema = z.object({
  category: z.enum(["love", "career", "personal-growth", "finances"]),
  mood: z.enum(["contemplative", "anxious", "hopeful", "uncertain"]),
  themes: z.array(z.string()).describe("2-4 key themes identified"),
  relatedQuestions: z.array(z.string()).describe("3-5 follow-up questions"),
  insight: z.string().describe("A brief mystical insight"),
});

router.post("/", async (req, res) => {
  const { question } = req.body;

  const result = streamObject({
    model: openai.chat("gemini-2.5-flash"),
    schema: suggestionsSchema,
    prompt: `Analyze this question: "${question}"`,
  });

  result.pipeTextStreamToResponse(res);
});
```

### Client

```tsx
import { experimental_useObject as useObject } from "@ai-sdk/react";
import { z } from "zod/v4";

// Schema must match server exactly
const suggestionsSchema = z.object({
  category: z.enum(["love", "career", "personal-growth", "finances"]),
  mood: z.enum(["contemplative", "anxious", "hopeful", "uncertain"]),
  themes: z.array(z.string()),
  relatedQuestions: z.array(z.string()),
  insight: z.string(),
});

function QuestionAnalyzer() {
  const [question, setQuestion] = useState("");
  const { object, submit, isLoading } = useObject({
    api: "/api/streaming-suggestions",
    schema: suggestionsSchema,
  });

  return (
    <div>
      <textarea value={question} onChange={(e) => setQuestion(e.target.value)} />
      <Button onClick={() => submit({ question })} disabled={isLoading}>
        Analyze
      </Button>

      {/* Renders progressively as data streams in */}
      {object && (
        <div>
          <Badge>{object.category}</Badge>
          <Badge>{object.mood}</Badge>
          
          {/* Arrays stream item by item */}
          <div className="flex gap-2">
            {object.themes?.map((t) => <Badge key={t}>{t}</Badge>)}
          </div>
          
          {/* Strings stream character by character */}
          <p>{object.insight}</p>
          
          <ul>
            {object.relatedQuestions?.map((q) => <li key={q}>{q}</li>)}
          </ul>
        </div>
      )}
    </div>
  );
}
```

**Key points:**
- Schema must be defined on both client and server
- Arrays stream item by item (each item appears as it's generated)
- Strings stream character by character
- Use optional chaining (`object?.field`) since object builds up progressively


---

## v6 Migration

| v5 | v6 |
|----|-----|
| `tool({ parameters })` | `tool({ inputSchema })` |
| Tool `result` property | Tool `output` property |
| States: `partial-call`, `call`, `result` | States: `input-streaming`, `input-available`, `output-available` |
| `maxToolRoundtrips` | `stopWhen: stepCountIs(n)` |
| `result.toAIStream()` | `result.toUIMessageStream()` |
| `pipeDataStreamToResponse()` | `pipeUIMessageStreamToResponse()` |

---

## Patched Fetch

Forge API returns `"type": ""` in streaming tool_calls. AI SDK expects no `type` field:

```ts
// server/_core/patchedFetch.ts
export function createPatchedFetch(): typeof fetch {
  return async (input, init) => {
    const response = await fetch(input, init);
    if (!response.body) return response;

    const contentType = response.headers.get("content-type") || "";
    if (!contentType.includes("text/event-stream")) return response;

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    const encoder = new TextEncoder();

    const stream = new ReadableStream({
      async pull(controller) {
        const { done, value } = await reader.read();
        if (done) { controller.close(); return; }

        let text = decoder.decode(value, { stream: true });
        text = text.replace(/"type"\s*:\s*(""|null)\s*,?\s*/g, "");
        controller.enqueue(encoder.encode(text));
      },
    });

    return new Response(stream, {
      status: response.status,
      statusText: response.statusText,
      headers: response.headers,
    });
  };
}
```

---

## Import Reference

```ts
// From 'ai'
import {
  streamText, generateText, generateObject,
  convertToModelMessages, createUIMessageStream,
  pipeUIMessageStreamToResponse, generateId,
  stepCountIs, tool, UIMessage,
} from "ai";

// From '@ai-sdk/openai'
import { createOpenAI } from "@ai-sdk/openai";

// From '@ai-sdk/react'
import { useChat } from "@ai-sdk/react";

// Transport
import { DefaultChatTransport } from "ai";
```
