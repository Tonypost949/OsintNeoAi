/**
 * Markdown Component
 *
 * A template-ready markdown renderer using Streamdown with:
 * - Shiki syntax highlighting for code blocks (via @streamdown/code)
 * - Mermaid diagram support (via @streamdown/mermaid)
 * - Line numbers on code blocks (built-in to Streamdown 2.x)
 * - Fine-grained control over each element via components prop
 * - Memoized for optimal performance during streaming
 *
 * @see https://streamdown.ai/docs - Streamdown Documentation
 * @see https://streamdown.ai/docs/configuration - Configuration Options
 * @see https://streamdown.ai/docs/code-blocks - Code Block Features
 * @see https://streamdown.ai/docs/mermaid - Mermaid Diagram Support
 * @see https://shiki.style - Shiki Syntax Highlighter
 *
 * Installation:
 * ```bash
 * pnpm add streamdown @streamdown/code @streamdown/mermaid
 * ```
 *
 * Basic Usage:
 * ```tsx
 * import { Markdown } from "@/components/Markdown";
 *
 * <Markdown>{content}</Markdown>
 * ```
 *
 * With Custom Theme:
 * ```tsx
 * <Markdown shikiTheme={["vitesse-light", "vitesse-dark"]}>
 *   {content}
 * </Markdown>
 * ```
 *
 * Override Specific Elements:
 * ```tsx
 * <Markdown
 *   components={{
 *     h1: ({ children }) => <h1 className="text-5xl text-blue-500">{children}</h1>,
 *     a: ({ href, children }) => <a href={href} className="text-pink-500">{children}</a>
 *   }}
 * >
 *   {content}
 * </Markdown>
 * ```
 *
 * Streaming Mode (for AI chat):
 * ```tsx
 * <Markdown mode="streaming" isAnimating={isStreaming}>
 *   {streamingContent}
 * </Markdown>
 * ```
 *
 * Available Shiki Themes:
 * - github-light, github-dark (default)
 * - dracula, nord, one-dark-pro, monokai
 * - catppuccin-latte, catppuccin-mocha
 * - vitesse-light, vitesse-dark
 * - tokyo-night, slack-dark, slack-ochin
 * @see https://shiki.style/themes for full list
 */

import { memo, type ReactNode, type ComponentProps } from "react";
import { Streamdown } from "streamdown";
import { code } from "@streamdown/code";
import { mermaid } from "@streamdown/mermaid";
import { cn } from "@/lib/utils";

// ============================================================================
// DEFAULT COMPONENT OVERRIDES
// Customize individual markdown elements here.
// Note: We don't override `pre` or `code` - let Streamdown/Shiki handle those
// to preserve syntax highlighting and line numbers.
// @see https://streamdown.ai/docs/configuration#components
// ============================================================================

const components = {
  // Headings - using tracking-tight for Vercel-style typography
  h1: ({ children }: { children?: ReactNode }) => (
    <h1 className="text-3xl font-semibold tracking-tight mt-8 mb-4 first:mt-0">
      {children}
    </h1>
  ),
  h2: ({ children }: { children?: ReactNode }) => (
    <h2 className="text-2xl font-semibold tracking-tight mt-8 mb-3 first:mt-0">
      {children}
    </h2>
  ),
  h3: ({ children }: { children?: ReactNode }) => (
    <h3 className="text-xl font-semibold tracking-tight mt-6 mb-3 first:mt-0">
      {children}
    </h3>
  ),
  h4: ({ children }: { children?: ReactNode }) => (
    <h4 className="text-lg font-semibold mt-6 mb-2 first:mt-0">{children}</h4>
  ),

  // Text elements
  p: ({ children }: { children?: ReactNode }) => (
    <p className="mb-4 leading-7 last:mb-0">{children}</p>
  ),
  a: ({ href, children }: { href?: string; children?: ReactNode }) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="underline underline-offset-4 decoration-muted-foreground/50 hover:decoration-foreground transition-colors"
    >
      {children}
    </a>
  ),
  strong: ({ children }: { children?: ReactNode }) => (
    <strong className="font-semibold">{children}</strong>
  ),
  em: ({ children }: { children?: ReactNode }) => (
    <em className="italic">{children}</em>
  ),

  // Lists
  ul: ({ children }: { children?: ReactNode }) => (
    <ul className="list-disc pl-6 mb-4 space-y-2">{children}</ul>
  ),
  ol: ({ children }: { children?: ReactNode }) => (
    <ol className="list-decimal pl-6 mb-4 space-y-2">{children}</ol>
  ),
  li: ({ children }: { children?: ReactNode }) => (
    <li className="leading-7">{children}</li>
  ),

  // Block elements
  blockquote: ({ children }: { children?: ReactNode }) => (
    <blockquote className="border-l-2 border-muted-foreground/30 pl-4 italic text-muted-foreground my-4">
      {children}
    </blockquote>
  ),
  hr: () => <hr className="border-border my-8" />,

  // Tables - with responsive wrapper
  table: ({ children }: { children?: ReactNode }) => (
    <div className="overflow-x-auto my-4">
      <table className="w-full border-collapse text-sm">{children}</table>
    </div>
  ),
  thead: ({ children }: { children?: ReactNode }) => <thead>{children}</thead>,
  tbody: ({ children }: { children?: ReactNode }) => <tbody>{children}</tbody>,
  tr: ({ children }: { children?: ReactNode }) => (
    <tr className="border-b border-border">{children}</tr>
  ),
  th: ({ children }: { children?: ReactNode }) => (
    <th className="border border-border bg-muted px-4 py-2 text-left font-semibold">
      {children}
    </th>
  ),
  td: ({ children }: { children?: ReactNode }) => (
    <td className="border border-border px-4 py-2">{children}</td>
  ),

  // Media
  img: ({ src, alt }: { src?: string; alt?: string }) => (
    <img src={src} alt={alt || ""} className="max-w-full h-auto rounded-lg my-4" />
  ),
};

// ============================================================================
// MARKDOWN COMPONENT
// ============================================================================

type MarkdownProps = Omit<ComponentProps<typeof Streamdown>, "components" | "plugins"> & {
  /** Override specific element renderers */
  components?: Partial<typeof components>;
  /** Enable/disable code syntax highlighting (default: true) */
  enableCode?: boolean;
  /** Enable/disable mermaid diagrams (default: true) */
  enableMermaid?: boolean;
};

/**
 * Markdown - A production-ready markdown renderer
 *
 * Features:
 * - Syntax highlighting with 200+ languages via Shiki
 * - Line numbers on code blocks
 * - Mermaid diagrams with interactive controls
 * - Copy/download buttons on code blocks and diagrams
 * - Streaming support for AI chat applications
 * - Memoized for performance
 *
 * @example
 * // Basic usage
 * <Markdown>{markdownContent}</Markdown>
 *
 * @example
 * // Streaming mode for AI chat
 * <Markdown mode="streaming" isAnimating={isLoading}>
 *   {streamingResponse}
 * </Markdown>
 */
export const Markdown = memo(function Markdown({
  className,
  children,
  components: customComponents,
  shikiTheme = ["github-light", "github-dark"],
  controls = true,
  enableCode = true,
  enableMermaid = true,
  ...props
}: MarkdownProps) {
  // Build plugins object based on what's enabled
  // @see https://streamdown.ai/docs/code-blocks
  // @see https://streamdown.ai/docs/mermaid
  const plugins: Record<string, unknown> = {};
  if (enableCode) plugins.code = code;
  if (enableMermaid) plugins.mermaid = mermaid;

  return (
    <Streamdown
      className={cn("text-foreground leading-relaxed", className)}
      components={{ ...components, ...customComponents }}
      plugins={plugins}
      shikiTheme={shikiTheme}
      controls={controls}
      {...props}
    >
      {children}
    </Streamdown>
  );
});

// Export individual components for custom composition
export { components as markdownComponents };
export default Markdown;
