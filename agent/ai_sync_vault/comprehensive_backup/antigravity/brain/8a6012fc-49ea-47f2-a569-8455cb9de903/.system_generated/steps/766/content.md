Title: Live Content

Description: Fetched live

Source: https://developers.googleblog.com/build-agentic-full-stack-apps-with-genkit/

---



<!DOCTYPE html>
<html lang="en">
  	<head>
        <meta charset="utf-8" />
        
        <title>
            
            Build agentic full-stack apps with Genkit
            
            
            - Google Developers Blog
            
        </title>
        <meta property="og:title" content="Build agentic full-stack apps with Genkit- Google Developers Blog" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        
	<meta name="description" content="Streamline your conversational AI development with the new Genkit Agents API. Discover how this open-source, full-stack framework handles message history, state persistence, streaming, and human-in-the-loop workflows out of the box for TypeScript and Go." />
  <meta content="summary_large_image" name="twitter:card"/>
  <meta content="Google for Developers Blog - News about Web, Mobile, AI and Cloud" property="twitter:title"/>
  <meta property="og:title" content="Build agentic full-stack apps with Genkit" />
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [{
      "@type": "ListItem",
      "position": 1,
      "name": "Google for Developers Blog",
      "item": "https://developers.googleblog.com/"
    },{
      "@type": "ListItem",
      "position": 2,
      "name": "Build agentic full-stack apps with Genkit",
      "item": "https://developers.googleblog.com/build-agentic-full-stack-apps-with-genkit/"
    }]
  }
  </script>
  <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "Article",
      "headline": "Build agentic full-stack apps with Genkit",
      "description": "The open-source Genkit framework has introduced the Agents API, a full-stack tool designed to simplify the complex plumbing of conversational AI by packaging message history, tool loops, and streaming into a single interface. The API supports flexible, server- or client-managed state persistence—allowing for advanced workflows like history branching, long-running detached tasks, and multi-agent coordination—while seamlessly connecting backends to frontends via a unified wire protocol. Currently available in preview for TypeScript and Go, it also integrates with the Genkit Developer UI to allow developers to easily test, debug, and inspect agent snapshots without writing client code.",
      "image": "https://storage.googleapis.com/gweb-developer-goog-blog-assets/images/Ai-1-banner.2e16d0ba.fill-800x400.png",
      "datePublished": "2026-07-01",
      "author": [
        
        
          { "@type": "Person", "name": "Chris Gill", "url": "/search/?author=Chris+Gill" }
        
        
      ]
    }
  </script>
  
  <meta content="https://storage.googleapis.com/gweb-developer-goog-blog-assets/images/Ai-1-meta.2e16d0ba.fill-1200x600.png" property="og:image"/>
  


        
        

        <!-- Google Tag Manager -->
        <script type="text/javascript" nonce="9pDkoBLhgOGzHDUP7i6Lcw==" src="https://storage.googleapis.com/gweb-developer-goog-blog-cms-assets/site/20260519-162827/js/analytics.js"></script>
        <!-- End Google Tag Manager -->

        
        <link href="//www.gstatic.com/glue/v27_1/glue.min.css" rel="stylesheet">
        <link rel="stylesheet" type="text/css" href="https://storage.googleapis.com/gweb-developer-goog-blog-cms-assets/site/20260519-162827/css/dgc_blog.css">
        <link rel="icon" href="https://storage.googleapis.com/gweb-developer-goog-blog-assets/meta/favicon.ico" type="image/x-icon">
        <link rel="apple-touch-icon" href="https://storage.googleapis.com/gweb-developer-goog-blog-assets/meta/apple-touch-icon.png">

        
				<link rel="preconnect" href="https://fonts.googleapis.com">
				<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
				<link rel="preload" href="https://fonts.googleapis.com/css2?family=Product+Sans&family=Google+Sans+Display:ital@0;1&family=Google+Sans:ital,wght@0,400;0,500;0,700;1,400;1,500;1,700&family=Google+Sans+Text:ital,wght@0,400;0,500;0,700;1,400;1,500;1,700&display=swap" as="style">
				<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Product+Sans&family=Google+Sans+Display:ital@0;1&family=Google+Sans:ital,wght@0,400;0,500;0,700;1,400;1,500;1,700&family=Google+Sans+Text:ital,wght@0,400;0,500;0,700;1,400;1,500;1,700&display=swap">
        <link href="https://fonts.googleapis.com/css2?family=Google+Sans+Code:ital,wght,MONO@0,300..800,1;1,300..800,1&amp;family=Google+Sans+Flex:opsz,wght@6..144,1..1000&amp;display=swap" rel="stylesheet" data-page-link="">
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Roboto:wght@400&display=swap">

        
        <link href="https://www.gstatic.com/glue/cookienotificationbar/cookienotificationbar.min.css" rel="stylesheet">

        
  <link
    rel="stylesheet"
    type="text/css"
    href="https://storage.googleapis.com/gweb-developer-goog-blog-cms-assets/site/20260519-162827/css/blog_detail.css"
  />
  <link type="text/css" href="https://storage.googleapis.com/gweb-developer-goog-blog-cms-assets/site/20260519-162827/css/prism.css" rel="stylesheet" />

    </head>

    <body id="main-content" class="glue-body ">
        <!-- Google Tag Manager (noscript) -->
        <noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-WVTLDSL "
        height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
        <!-- End Google Tag Manager (noscript) -->

        

				
        

<!-- HTML -->
<header class="dgc-header">
  <div class="dgc-header-inner">
    <button class="hamburger" aria-haspopup="true" aria-expanded="false" aria-label="Open Menu">
      <svg role="presentation" aria-hidden="true" class="glue-icon">
        <use href="/glue-icon/#menu"></use>
      </svg>
    </button>
    <div class="product-name-wrapper">
      <a href="https://developers.google.com/" class="site-logo-link" data-label="Site logo">
        <img src="https://storage.googleapis.com/gweb-developer-goog-blog-cms-assets/site/20260519-162827/images/g-dev.svg" class="site-logo" alt="Google for Developers">
      </a>
    </div>
    <div class="desktop-nav-wrapper">
      <div class="upper-tabs-wrapper">
        <div class="upper-tabs">
          <nav class="tabs" aria-label="Upper Tabs">
            <div class="tab">
              <a
                href="//developers.google.com/community"
                class="top-nav-title">
                Community/Events
              </a>
            </div>
            <div class="tab">
              <a
                href="//developers.google.com/solutions/catalog"
                class="top-nav-title">
                Learn
              </a>
            </div>
            <div class="tab">
              <a
                href="//developers.googleblog.com"
                class="top-nav-title">
                Blog
              </a>
            </div>
            <div class="tab">
              <a
                href="https://www.youtube.com/user/GoogleDevelopers"
                class="top-nav-title">
                YouTube
              </a>
            </div>
          </nav>
        </div>
      </div>
    </div>
  </div>
  <div class="dgc-header-search">
    <div class="search-wrapper glue-page">
      <div class="glue-grid">
        <form id="search-form"  action="/search/" method="get" class="search-content glue-grid__col glue-grid__col--span-4-sm glue-grid__col--span-9-md glue-grid__col--span-7-lg">
          <div class="search-input-wrapper">
            <svg role="presentation" aria-hidden="true" class="glue-icon search-icon">
              <use href="/glue-icon/#search"></use>
            </svg>
            <input
              type="text"
              name="query"
              
              placeholder="Search all articles..."
              aria-label="Search"
              class="search-input-field"
            />
          </div>
          <button class="glue-button glue-button--high-emphasis">
            Search
          </button>
        </form>
      </div>
    </div>
  </div>
</header>

<div class="mobile-drawer" top-level-nav>
  <nav class="nav-content" aria-label="Side menu">
    <div class="mobile-header">
      <button class="nav-close-btn nav-btn" aria-label="Close navigation">
        <svg role="presentation" aria-hidden="true" class="glue-icon">
          <use href="/glue-icon/#close"></use>
        </svg>
      </button>
      <button class="nav-back-btn nav-btn hidden" aria-label="Back to Menu">
        <svg role="presentation" aria-hidden="true" class="glue-icon">
          <use href="/glue-icon/#arrow-back"></use>
        </svg>
      </button>
      <div class="product-name-wrapper">
        <a href="https://developers.google.com/" class="site-logo-link" data-label="Site logo">
          <img src="https://storage.googleapis.com/gweb-developer-goog-blog-cms-assets/site/20260519-162827/images/g-dev.svg" class="site-logo" alt="Google for Developers">
        </a>
      </div>
    </div>
    <div class="nav-wrapper">
      <div class="mobile-nav-top">
        <ul class="nav-list">
          <li class="nav-item">
            <a href="//developers.google.com/community" class="nav-title" data-label="Tab: Community/Events">
              <span class="nav-text" tooltip="">
                Community/Events
             </span>
            </a>
          </li>
          <li class="nav-item">
            <a href="//developers.google.com/solutions/catalog" class="nav-title" data-label="Tab: Learn">
              <span class="nav-text" tooltip="">
                Learn
             </span>
            </a>
          </li>
          <li class="nav-item">
            <a href="//developers.googleblog.com" class="nav-title" data-label="Tab: Blog">
              <span class="nav-text" tooltip="">
                Blog
             </span>
            </a>
          </li>
          <li class="nav-item">
            <a href="https://www.youtube.com/user/GoogleDevelopers" class="nav-title" data-label="Tab: YouTube">
              <span class="nav-text" tooltip="">
                YouTube
             </span>
            </a>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</div>

<div class="backdrop"></div>

        
  <div class="blog-detail-container">

    
      <section class="tags-container glue-page glue-spacer-5-top">
        <div class="glue-eyebrow"></div>
      </section>
    

    <section class="heading-container glue-page  glue-spacer-1-top">
      <h1 class="glue-headline glue-headline--headline-1">Build agentic full-stack apps with Genkit</h1>
    </section>

    <section class="summary-container glue-page glue-spacer-4-top">
      <div class="date-time">
        <div class="published-date glue-font-weight-medium">JULY 1, 2026</div>
      </div>
    </section>

    <section class="glue-page glue-grid glue-spacer-1-top">

      <section class="author-container glue-grid__col glue-grid__col--span-4-sm glue-grid__col--span-10-md">
      
        
          <div class="author-obj">
            <a class="glue-font-weight-medium" href="/search/?author=Chris+Gill">Chris Gill</a>
            
              <span class="glue-font-weight-medium role">Product Manager</span>
            
            
          </div>
        

      
      </section>
      <section class="social-container glue-grid__col glue-grid__col--span-4-sm glue-grid__col--span-2-md">
        <button id="social-button" class="glue-button glue-button--low-emphasis glue-button--icon" aria-haspopup="true" aria-expanded="false">
          <svg role="presentation" aria-hidden="true" class="glue-icon">
            <use href="/glue-icon/#share"></use>
          </svg>
          <span>Share</span>
        </button>
        <ul id="social-menu" class="glue-elevation-level-1" role="menu" aria-labelledby="social-button">
          <li>
            <a href="https://www.facebook.com/sharer/sharer.php?u={url}"
                title="Share on Facebook" target="_blank" rel="noopener">
              <svg role="presentation" aria-hidden="true"
                  class="glue-icon glue-icon--social glue-icon--32px">
                <use href="/glue-icon/#post-facebook"></use>
              </svg>
              <span>Facebook</span>
            </a>
          </li>
          <li>
            <a href="https://twitter.com/intent/tweet?text={url}"
                title="Share on Twitter" target="_blank" rel="noopener">
              <svg role="presentation" aria-hidden="true"
                  class="glue-icon glue-icon--social glue-icon--32px">
                <use href="/glue-icon/#twitter-x"></use>
              </svg>
              <span>Twitter</span>
            </a>
          </li>
          <li>
            <a href="https://www.linkedin.com/shareArticle?url={url}&amp;mini=true" title="Share on LinkedIn" target="_blank" rel="noopener">
              <svg role="presentation" aria-hidden="true"
                  class="glue-icon glue-icon--social glue-icon--32px">
                <use href="/glue-icon/#post-linkedin"></use>
              </svg>
              <span>LinkedIn</span>
            </a>
          </li>
          <li>
            <a href="mailto:name@example.com?subject=Check%20out%20this%20site&body=Check%20out%20{url}" title="Send via Email">
              <svg role="presentation" aria-hidden="true"
                  class="glue-icon glue-icon--social glue-icon--32px">
                <use href="/glue-icon/#email"></use>
              </svg>
              <span>Mail</span>
            </a>
          </li>
          <li>
            <a href="#" title="Get shareable link" data-link="" data-copy-text="Copy Link" data-copied-text="Copied!">
              <svg role="presentation" aria-hidden="true"
                  class="glue-icon glue-icon--social glue-icon--32px">
                <use href="/glue-icon/#link"></use>
              </svg>
              <span></span>
            </a>
          </li>
        </ul>
      </section>
    </section>

    
    <section class="blocks-container glue-page glue-spacer-3-top">
      <div class="block">
          

<img
    class="banner-image"
    src="https://storage.googleapis.com/gweb-developer-goog-blog-assets/images/Ai-1-banner.original.png"
    alt="Agent Development Kit: Making it easy to build multi-agent applications"
/>  <div class="inner-block-content rich-content">
    <h2 data-block-key="38e24" id="announcing-genkit-agents:-a-full-stack-foundation-for-conversational-ai"><b>Announcing Genkit Agents: A full-stack foundation for conversational AI</b></h2><p data-block-key="evl4q"><a href="https://genkit.dev/">Genkit</a> is an open-source framework for <b>building full-stack, AI-powered and agentic applications for any platform</b> with support for TypeScript, Go, Dart, and Python. Some of the most compelling AI features are conversational, like a support assistant that remembers the ticket or a copilot that works across several turns. Each needs more than a single <code>generate()</code> call, and building one today means wiring up message history, the tool loop, streaming, persistence, and a frontend protocol by hand. That plumbing repeats on every project and has little to do with what makes your app distinct.</p><p data-block-key="5dalr">Genkit solves this with the <a href="https://genkit.dev/docs/agents/overview/"><b>Agents API</b></a>, which packages all of that behind one interface. You define an agent on the server, then drive it with the same <code>chat()</code> API whether it runs in process or behind an HTTP endpoint.</p><p data-block-key="eeggl"><b>&gt;</b> The Agents API is in <b>preview</b> today in TypeScript and Go. It can introduce breaking changes in minor version releases.</p><h3 data-block-key="l50hg" id="define-an-agent"><b>Define an agent</b></h3><p data-block-key="b9jr5">An agent needs a name and a system prompt to start. From there you add tools, state, and a session store as the feature grows.</p>
</div>  <div class="inner-block-content code-block line-numbers">
    <pre><code class="language-go">import genkitx &quot;github.com/firebase/genkit/go/genkit/exp&quot;

g := genkit.Init(ctx,
    genkit.WithPlugins(&amp;googlegenai.GoogleAI{}),
    genkit.WithExperimental(), // Enables preview features like Agents API.
)

assistant := genkitx.DefineAgent(g, &quot;assistant&quot;,
    aix.InlinePrompt{
        ai.WithModelName(&quot;googleai/gemini-flash-latest&quot;),
        ai.WithSystem(&quot;You are a helpful assistant.&quot;),
    },
)

out, err := assistant.RunText(ctx, &quot;Hello. What can you do?&quot;)
if err != nil {
    log.Fatal(err)
}

fmt.Println(out.Message.Text())</code></pre>
    <div class="language-block glue-font-weight-medium">
        Go
    </div>
    <div class="copy-code-block">
        <span class="hidden">Copied</span>
        <button class="copy-clipboard">
            <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#202124"><path d="M360-240q-33 0-56.5-23.5T280-320v-480q0-33 23.5-56.5T360-880h360q33 0 56.5 23.5T800-800v480q0 33-23.5 56.5T720-240H360Zm0-80h360v-480H360v480ZM200-80q-33 0-56.5-23.5T120-160v-560h80v560h440v80H200Zm160-240v-480 480Z"/></svg>
        </button>
    </div>
    <div class="dark-mode-block">
        <button class="dark-mode-toggle">
            <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#202124"><path d="M480-120q-150 0-255-105T120-480q0-150 105-255t255-105q14 0 27.5 1t26.5 3q-41 29-65.5 75.5T444-660q0 90 63 153t153 63q55 0 101-24.5t75-65.5q2 13 3 26.5t1 27.5q0 150-105 255T480-120Zm0-80q88 0 158-48.5T740-375q-20 5-40 8t-40 3q-123 0-209.5-86.5T364-660q0-20 3-40t8-40q-78 32-126.5 102T200-480q0 116 82 198t198 82Zm-10-270Z"/></svg>
        </button>
    </div>
    
</div>  <div class="inner-block-content rich-content">
    <p data-block-key="fp1sc">The same agent object is flexible and can handle a one-shot reply, a streamed turn, a paused tool call, and a multi-turn conversation. You do not reach for a different abstraction as the feature grows.</p><h3 data-block-key="80vjf" id="state-that-lives-where-you-want-it"><b>State that lives where you want it</b></h3><p data-block-key="6u2s3">Every conversation needs continuity between turns, and you decide who owns it.</p><p data-block-key="1ghfg">Add a <code>store</code> and the agent becomes <b>server-managed</b>. The server persists messages, custom state, and artifacts as snapshots, and clients continue by sending back a session ID. Choose this for persistent chat apps, shared devices, and any workflow where the client should not carry the whole conversation.</p>
</div>  <div class="inner-block-content code-block line-numbers">
    <pre><code class="language-go">import firebasex &quot;github.com/firebase/genkit/go/plugins/firebase/exp&quot;
import genkitx &quot;github.com/firebase/genkit/go/genkit/exp&quot;

store, err := firebasex.NewFirestoreSessionStore[WeatherState](ctx, g,
    firebasex.WithCollection(&quot;snapshots&quot;),
    firebasex.WithCheckpointInterval(10),
)
if err != nil {
    log.Fatal(err)
}

weatherAgent := genkitx.DefineAgent(g, &quot;weatherAgent&quot;,
    aix.InlinePrompt{
        ai.WithSystem(&quot;Answer weather questions. Ask for a location when one is missing.&quot;),
        ai.WithTools(getWeather),
    },
    aix.WithSessionStore(store),
)</code></pre>
    <div class="language-block glue-font-weight-medium">
        Go
    </div>
    <div class="copy-code-block">
        <span class="hidden">Copied</span>
        <button class="copy-clipboard">
            <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#202124"><path d="M360-240q-33 0-56.5-23.5T280-320v-480q0-33 23.5-56.5T360-880h360q33 0 56.5 23.5T800-800v480q0 33-23.5 56.5T720-240H360Zm0-80h360v-480H360v480ZM200-80q-33 0-56.5-23.5T120-160v-560h80v560h440v80H200Zm160-240v-480 480Z"/></svg>
        </button>
    </div>
    <div class="dark-mode-block">
        <button class="dark-mode-toggle">
            <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#202124"><path d="M480-120q-150 0-255-105T120-480q0-150 105-255t255-105q14 0 27.5 1t26.5 3q-41 29-65.5 75.5T444-660q0 90 63 153t153 63q55 0 101-24.5t75-65.5q2 13 3 26.5t1 27.5q0 150-105 255T480-120Zm0-80q88 0 158-48.5T740-375q-20 5-40 8t-40 3q-123 0-209.5-86.5T364-660q0-20 3-40t8-40q-78 32-126.5 102T200-480q0 116 82 198t198 82Zm-10-270Z"/></svg>
        </button>
    </div>
    
</div>  <div class="inner-block-content rich-content">
    <p data-block-key="fp1sc">The store you configure decides where snapshots live. For production, Firestore gives you a managed, multi-instance database that several server instances can share. Genkit also ships lighter stores for local work and lets you implement your own, which the section below covers.</p><p data-block-key="d88kk"></p><p data-block-key="6feeg">Leave the store off and the agent is client-managed: the server returns the full state and the client sends it back on the next turn. Use this when your app already owns persistence or you need stateless server deployments.</p><p data-block-key="7bedf"></p><p data-block-key="53inc">Every successful server-managed turn writes a snapshot, so you can resume the latest state by <code>sessionId</code> or branch from an exact point in history by <code>snapshotId</code>. Branching lets a user explore an alternative from any saved moment without disturbing the original thread.</p>
</div>  <div class="inner-block-content code-block line-numbers">
    <pre><code class="language-go">// Continue the latest state in a conversation.
out, err := weatherAgent.RunText(ctx, &quot;Continue where we left off.&quot;,
    aix.WithSessionID[WeatherState](&quot;user-session-123&quot;),
)

// Or branch from a specific saved point.
branch, err := weatherAgent.RunText(ctx, &quot;Revise this plan for a smaller budget.&quot;,
    aix.WithSnapshotID[WeatherState](approvedPlanSnapshotID),
)</code></pre>
    <div class="language-block glue-font-weight-medium">
        Go
    </div>
    <div class="copy-code-block">
        <span class="hidden">Copied</span>
        <button class="copy-clipboard">
            <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#202124"><path d="M360-240q-33 0-56.5-23.5T280-320v-480q0-33 23.5-56.5T360-880h360q33 0 56.5 23.5T800-800v480q0 33-23.5 56.5T720-240H360Zm0-80h360v-480H360v480ZM200-80q-33 0-56.5-23.5T120-160v-560h80v560h440v80H200Zm160-240v-480 480Z"/></svg>
        </button>
    </div>
    <div class="dark-mode-block">
        <button class="dark-mode-toggle">
            <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#202124"><path d="M480-120q-150 0-255-105T120-480q0-150 105-255t255-105q14 0 27.5 1t26.5 3q-41 29-65.5 75.5T444-660q0 90 63 153t153 63q55 0 101-24.5t75-65.5q2 13 3 26.5t1 27.5q0 150-105 255T480-120Zm0-80q88 0 158-48.5T740-375q-20 5-40 8t-40 3q-123 0-209.5-86.5T364-660q0-20 3-40t8-40q-78 32-126.5 102T200-480q0 116 82 198t198 82Zm-10-270Z"/></svg>
        </button>
    </div>
    
</div>  <div class="inner-block-content rich-content">
    <p data-block-key="fp1sc">Alongside message history, an agent carries two more kinds of state. <b>Custom state</b> is your typed application data, the compact control and UI values that drive the next turn, such as workflow status, a task list, or selected entities. <b>Artifacts</b> are generated outputs the user may inspect, download, or version on their own, such as a report, a patch, or an itinerary. A tool updates either one through the active session, and Genkit streams the changes to the client as they happen.</p><h2 data-block-key="669xw" id="serve-it-over-http"><b>Serve it over HTTP</b></h2><p data-block-key="67bho">Every agent is already a servable action, so putting one behind an HTTP endpoint is a few lines. The route helpers return descriptors you mount on a standard http.ServeMux, and they wire up the turn endpoint plus the snapshot and abort companions for you.</p>
</div>  <div class="inner-block-content code-block line-numbers">
    <pre><code class="language-go">import genkitx &quot;github.com/firebase/genkit/go/genkit/exp&quot;

mux := http.NewServeMux()
for _, route := range genkitx.AllAgentRoutes(g) {
    mux.HandleFunc(route.Pattern(), route.Handler())
}

log.Fatal(http.ListenAndServe(&quot;:8080&quot;, mux))</code></pre>
    <div class="language-block glue-font-weight-medium">
        Go
    </div>
    <div class="copy-code-block">
        <span class="hidden">Copied</span>
        <button class="copy-clipboard">
            <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#202124"><path d="M360-240q-33 0-56.5-23.5T280-320v-480q0-33 23.5-56.5T360-880h360q33 0 56.5 23.5T800-800v480q0 33-23.5 56.5T720-240H360Zm0-80h360v-480H360v480ZM200-80q-33 0-56.5-23.5T120-160v-560h80v560h440v80H200Zm160-240v-480 480Z"/></svg>
        </button>
    </div>
    <div class="dark-mode-block">
        <button class="dark-mode-toggle">
            <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#202124"><path d="M480-120q-150 0-255-105T120-480q0-150 105-255t255-105q14 0 27.5 1t26.5 3q-41 29-65.5 75.5T444-660q0 90 63 153t153 63q55 0 101-24.5t75-65.5q2 13 3 26.5t1 27.5q0 150-105 255T480-120Zm0-80q88 0 158-48.5T740-375q-20 5-40 8t-40 3q-123 0-209.5-86.5T364-660q0-20 3-40t8-40q-78 32-126.5 102T200-480q0 116 82 198t198 82Zm-10-270Z"/></svg>
        </button>
    </div>
    
</div>  <div class="inner-block-content rich-content">
    <p data-block-key="fp1sc">That same wire protocol is what the client below speaks, so a JavaScript or Go backend serves any client identically.</p><h2 data-block-key="i8ql7" id="a-rich-client-for-full-stack-integration"><b>A rich client for full-stack integration</b></h2><p data-block-key="arp9m">The piece that ties your server and client together is the remote agent. <code>remoteAgent()</code> returns a handle with the <b>same</b> <b><code>chat()</code></b><b> interface</b> as a local agent, so the code that drives an agent in your backend tests is the code that drives it from the browser. There is no separate request and response protocol to design, and no streaming format to invent.</p><p data-block-key="5p1fr">We are launching a JavaScript client, so a web frontend can talk to the same agent endpoint. The following is an example of how to connect to a remote agent from a TypeScript frontend.</p>
</div>  <div class="inner-block-content code-block line-numbers">
    <pre><code class="language-javascript">import { remoteAgent } from &#x27;genkit/beta/client&#x27;;

const agent = remoteAgent&lt;WeatherState&gt;({
  url: &#x27;http://localhost:8080/api/weatherAgent&#x27;,
});

const chat = agent.chat();
const res = await chat.send(&#x27;Weather in Tokyo?&#x27;);

console.log(res.text);</code></pre>
    <div class="language-block glue-font-weight-medium">
        JavaScript
    </div>
    <div class="copy-code-block">
        <span class="hidden">Copied</span>
        <button class="copy-clipboard">
            <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#202124"><path d="M360-240q-33 0-56.5-23.5T280-320v-480q0-33 23.5-56.5T360-880h360q33 0 56.5 23.5T800-800v480q0 33-23.5 56.5T720-240H360Zm0-80h360v-480H360v480ZM200-80q-33 0-56.5-23.5T120-160v-560h80v560h440v80H200Zm160-240v-480 480Z"/></svg>
        </button>
    </div>
    <div class="dark-mode-block">
        <button class="dark-mode-toggle">
            <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#202124"><path d="M480-120q-150 0-255-105T120-480q0-150 105-255t255-105q14 0 27.5 1t26.5 3q-41 29-65.5 75.5T444-660q0 90 63 153t153 63q55 0 101-24.5t75-65.5q2 13 3 26.5t1 27.5q0 150-105 255T480-120Zm0-80q88 0 158-48.5T740-375q-20 5-40 8t-40 3q-123 0-209.5-86.5T364-660q0-20 3-40t8-40q-78 32-126.5 102T200-480q0 116 82 198t198 82Zm-10-270Z"/></svg>
        </button>
    </div>
    
</div>  <div class="inner-block-content rich-content">
    <p data-block-key="fp1sc">The client speaks one wire protocol over the agent route, so it works the same against a JavaScript or a Go backend. It resolves dynamic auth headers per request, applies streamed state patches, and continues the next turn with a session ID, a snapshot ID, or client-managed state, whichever your agent uses.</p><p data-block-key="17sme">Streaming is built into the same interface. <code>sendStream()</code> gives you a chunk stream and a final response, and each chunk can carry text, custom state, or an artifact as it is produced.</p>
</div>  <div class="inner-block-content code-block line-numbers">
    <pre><code class="language-javascript">const turn = agent.chat().sendStream(&#x27;Write a long report.&#x27;);

for await (const chunk of turn.stream) {
  if (chunk.text) process.stdout.write(chunk.text);
  if (chunk.custom) updateStatus(chunk.custom);
  if (chunk.artifact) renderArtifact(chunk.artifact);
}

const res = await turn.response;</code></pre>
    <div class="language-block glue-font-weight-medium">
        JavaScript
    </div>
    <div class="copy-code-block">
        <span class="hidden">Copied</span>
        <button class="copy-clipboard">
            <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#202124"><path d="M360-240q-33 0-56.5-23.5T280-320v-480q0-33 23.5-56.5T360-880h360q33 0 56.5 23.5T800-800v480q0 33-23.5 56.5T720-240H360Zm0-80h360v-480H360v480ZM200-80q-33 0-56.5-23.5T120-160v-560h80v560h440v80H200Zm160-240v-480 480Z"/></svg>
        </button>
    </div>
    <div class="dark-mode-block">
        <button class="dark-mode-toggle">
            <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#202124"><path d="M480-120q-150 0-255-105T120-480q0-150 105-255t255-105q14 0 27.5 1t26.5 3q-41 29-65.5 75.5T444-660q0 90 63 153t153 63q55 0 101-24.5t75-65.5q2 13 3 26.5t1 27.5q0 150-105 255T480-120Zm0-80q88 0 158-48.5T740-375q-20 5-40 8t-40 3q-123 0-209.5-86.5T364-660q0-20 3-40t8-40q-78 32-126.5 102T200-480q0 116 82 198t198 82Zm-10-270Z"/></svg>
        </button>
    </div>
    
</div>  <div class="inner-block-content rich-content">
    <p data-block-key="fp1sc">If you already have apps that use the <a href="https://ai-sdk.dev/docs/ai-sdk-ui">Vercel AI SDK UI</a> library, the <code>@genkit-ai/vercel-ai</code> package provides an adapter for its <code>useChat</code> hook. The <code>GenkitChatTransport</code> adapter connects <code>useChat</code> to your Genkit agent, so you can assemble the interface from Vercel&#x27;s <a href="https://elements.ai-sdk.dev/">AI Elements</a> components while getting all the benefits of Genkit on the backend.</p><h2 data-block-key="9ser5" id="human-approval-built-in">Human approval, built in</h2><p data-block-key="98mpd">A tool can pause an agent and hand control back to the user. The model decides outside input is needed, the tool interrupts, and the client approves, rejects, or supplies the missing value before the turn continues. This is how you put a human in the loop before a payment, a deployment, or any action you do not want to run automatically.</p>
</div>  <div class="inner-block-content code-block line-numbers">
    <pre><code class="language-go">import genkitx &quot;github.com/firebase/genkit/go/genkit/exp&quot;
import &quot;github.com/firebase/genkit/go/ai/exp/tool&quot;

runShell := genkitx.DefineInterruptibleTool(g, &quot;run_shell&quot;,
    &quot;Run a shell command after a safety check.&quot;,
    func(ctx context.Context, input ShellInput, confirm *Confirmation) (ShellOutput, error) {
        if isRisky(input.Command) {
            if confirm == nil {
                return ShellOutput{}, tool.Interrupt(ShellInterrupt{
                    Command: input.Command,
                    Reason:  &quot;The command can modify files.&quot;,
                })
            } else if !confirm.Approved {
                return ShellOutput{}, errors.New(&quot;user rejected shell command execution&quot;)
            }
        }

        return execute(input.Command)
    },
)</code></pre>
    <div class="language-block glue-font-weight-medium">
        Go
    </div>
    <div class="copy-code-block">
        <span class="hidden">Copied</span>
        <button class="copy-clipboard">
            <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#202124"><path d="M360-240q-33 0-56.5-23.5T280-320v-480q0-33 23.5-56.5T360-880h360q33 0 56.5 23.5T800-800v480q0 33-23.5 56.5T720-240H360Zm0-80h360v-480H360v480ZM200-80q-33 0-56.5-23.5T120-160v-560h80v560h440v80H200Zm160-240v-480 480Z"/></svg>
        </button>
    </div>
    <div class="dark-mode-block">
        <button class="dark-mode-toggle">
            <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#202124"><path d="M480-120q-150 0-255-105T120-480q0-150 105-255t255-105q14 0 27.5 1t26.5 3q-41 29-65.5 75.5T444-660q0 90 63 153t153 63q55 0 101-24.5t75-65.5q2 13 3 26.5t1 27.5q0 150-105 255T480-120Zm0-80q88 0 158-48.5T740-375q-20 5-40 8t-40 3q-123 0-209.5-86.5T364-660q0-20 3-40t8-40q-78 32-126.5 102T200-480q0 116 82 198t198 82Zm-10-270Z"/></svg>
        </button>
    </div>
    
</div>  <div class="inner-block-content rich-content">
    <p data-block-key="fp1sc">The turn finishes with an <code>interrupted</code> reason and the paused request on the response. The client resumes once the user answers, and the runtime validates the resume payload against session history so a tool cannot be tricked into running with forged input.</p><h2 data-block-key="g3oge" id="work-that-outlives-the-request"><b>Work that outlives the request</b></h2><p data-block-key="907et">Some turns take longer than a user wants to wait. With server-managed state, a client can detach a turn, close the tab, and reconnect later by snapshot ID. The agent keeps working on the server, writing progress to a pending snapshot that another session can poll, wait on, or abort.</p>
</div>  <div class="inner-block-content code-block line-numbers">
    <pre><code class="language-javascript">const chat = reportAgent.chat({ sessionId: &#x27;report-123&#x27; });
const task = await chat.detach(&#x27;Write the quarterly market report.&#x27;);

// Persist this so any client can reconnect to the work later.
savePendingSnapshot(task.snapshotId);

for await (const snapshot of task.poll({ intervalMs: 1000 })) {
  renderStatus(snapshot.status);
  if (snapshot.status === &#x27;completed&#x27;) renderMessages(snapshot.state.messages);
}</code></pre>
    <div class="language-block glue-font-weight-medium">
        JavaScript
    </div>
    <div class="copy-code-block">
        <span class="hidden">Copied</span>
        <button class="copy-clipboard">
            <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#202124"><path d="M360-240q-33 0-56.5-23.5T280-320v-480q0-33 23.5-56.5T360-880h360q33 0 56.5 23.5T800-800v480q0 33-23.5 56.5T720-240H360Zm0-80h360v-480H360v480ZM200-80q-33 0-56.5-23.5T120-160v-560h80v560h440v80H200Zm160-240v-480 480Z"/></svg>
        </button>
    </div>
    <div class="dark-mode-block">
        <button class="dark-mode-toggle">
            <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#202124"><path d="M480-120q-150 0-255-105T120-480q0-150 105-255t255-105q14 0 27.5 1t26.5 3q-41 29-65.5 75.5T444-660q0 90 63 153t153 63q55 0 101-24.5t75-65.5q2 13 3 26.5t1 27.5q0 150-105 255T480-120Zm0-80q88 0 158-48.5T740-375q-20 5-40 8t-40 3q-123 0-209.5-86.5T364-660q0-20 3-40t8-40q-78 32-126.5 102T200-480q0 116 82 198t198 82Zm-10-270Z"/></svg>
        </button>
    </div>
    
</div>  <div class="inner-block-content rich-content">
    <p data-block-key="fp1sc">This makes long research jobs, multi-step planning, and tool-heavy workflows practical without holding a connection open or building a separate job queue.</p><h2 data-block-key="gua52" id="coordinate-specialists"><b>Coordinate specialists</b></h2><p data-block-key="7nqtd">When one prompt cannot do everything well, you can split work across specialized agents and let an orchestrator combine their results. The <code>Agents</code> middleware injects a delegation tool for each sub-agent, so the orchestrator model can route parts of a request to the right specialist. Subagents with Genkit give you full control and the ability to implement your own orchestration.</p>
</div>  <div class="inner-block-content code-block line-numbers">
    <pre><code class="language-go">import middlewarex &quot;github.com/firebase/genkit/go/plugins/middleware/exp&quot;

coordinator := genkit.DefineAgent(g, &quot;coordinator&quot;,
    aix.InlinePrompt{
        ai.WithSystem(&quot;Delegate to specialists, inspect their results, then answer the user.&quot;),
        ai.WithUse(
            &amp;middlewarex.Agents{
                Agents:           []aix.AgentRef{researcher.Ref(), coder.Ref()},
                MaxDelegations:   5,
                ArtifactStrategy: middlewarex.ArtifactStrategySession,
            },
            &amp;middlewarex.Artifacts{Readonly: true},
        ),
    },
)</code></pre>
    <div class="language-block glue-font-weight-medium">
        Go
    </div>
    <div class="copy-code-block">
        <span class="hidden">Copied</span>
        <button class="copy-clipboard">
            <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#202124"><path d="M360-240q-33 0-56.5-23.5T280-320v-480q0-33 23.5-56.5T360-880h360q33 0 56.5 23.5T800-800v480q0 33-23.5 56.5T720-240H360Zm0-80h360v-480H360v480ZM200-80q-33 0-56.5-23.5T120-160v-560h80v560h440v80H200Zm160-240v-480 480Z"/></svg>
        </button>
    </div>
    <div class="dark-mode-block">
        <button class="dark-mode-toggle">
            <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#202124"><path d="M480-120q-150 0-255-105T120-480q0-150 105-255t255-105q14 0 27.5 1t26.5 3q-41 29-65.5 75.5T444-660q0 90 63 153t153 63q55 0 101-24.5t75-65.5q2 13 3 26.5t1 27.5q0 150-105 255T480-120Zm0-80q88 0 158-48.5T740-375q-20 5-40 8t-40 3q-123 0-209.5-86.5T364-660q0-20 3-40t8-40q-78 32-126.5 102T200-480q0 116 82 198t198 82Zm-10-270Z"/></svg>
        </button>
    </div>
    
</div>  <div class="inner-block-content rich-content">
    <p data-block-key="fp1sc">Delegation shows up as ordinary tool activity in the orchestrator&#x27;s stream, and specialist artifacts can merge into the parent session so the final answer can build on what each specialist produced.</p><h3 data-block-key="2s6su" id="when-to-reach-for-adk-instead"><b>When to reach for ADK instead</b></h3><p data-block-key="dlc98">Genkit agents are an application primitive, built to live inside a full-stack, user-facing app. Consider the <a href="https://google.github.io/adk-docs/">Agent Development Kit (ADK)</a> instead when:</p><p data-block-key="7irld"></p><ul><li data-block-key="8f6fs"><b>Multi-agent orchestration is the whole system, not just one feature.</b> ADK is purpose-built for complex agent topologies, where Genkit&#x27;s delegation middleware is deliberately lighter and not built into the core of the agent abstraction.</li><li data-block-key="c303v"><b>You want a managed runtime, not just a library.</b> ADK pairs with Agent Runtime on the Gemini Enterprise Agent Platform for hosting, scaling, and managed sessions.</li></ul><p data-block-key="9gr64"></p><h2 data-block-key="8m01d" id="choose-your-persistence"><b>Choose your persistence</b></h2><p data-block-key="5u9b1">Server-managed agents store snapshots through a session store, and Genkit ships several so you can match the store to where you are running:</p><p data-block-key="efrs"></p><ul><li data-block-key="2a9ng"><b>In-memory</b> for tests, demos, and single-process experiments.</li><li data-block-key="3abu4"><b>File</b> for local development and single-host apps that need snapshots to survive a restart.</li><li data-block-key="bk680"><b>Firestore</b> for production apps on Google Cloud or Firebase that want a managed, multi-instance database with no store code to write.</li><li data-block-key="a72gr"><b>Custom</b> when you need to use your own database, authorization, or have specific retention policies. You can implement your own persistence layer using the `store` interface.</li></ul><p data-block-key="eknjb"></p><h2 data-block-key="oxbxq" id="test-and-explore-in-the-developer-ui"><b>Test and explore in the Developer UI</b></h2><p data-block-key="5l0fh">Agents are first-class in the Genkit <a href="https://genkit.dev/docs/devtools/">Developer UI</a>. The new <b>Agent Runner</b> lets you start a conversation, send turns, watch streamed output and state updates, drive tool interrupts, and inspect snapshots, all without writing a client. It is the fastest way to exercise an agent while you are building it and to reproduce a conversation when you are debugging one.</p><p data-block-key="c4880"></p><h2 data-block-key="jvkcf" id="get-started"><b>Get started</b></h2><p data-block-key="ce95a">The Agents API turns the repeated plumbing of conversational, full-stack AI into something you configure rather than rebuild. Define an agent on the server, give it a store when you want persistence, and drive it from your frontend with the same chat() interface through remoteAgent().</p><p data-block-key="2a6hd">Head to the <a href="https://genkit.dev/docs/agents/overview/">Full-stack agents documentation</a> to dive in, or <a href="https://genkit.dev/docs/get-started/">get started with Genkit</a> if you are new to the framework. The API is in Beta, so we want your feedback: <a href="https://github.com/genkit-ai/genkit/issues">file an issue</a> with what you build and what you would change.</p><p data-block-key="931ao">Happy coding! 🚀</p>
</div> 
      </div>
    </section>
    

    <section class="navigation-container glue-page glue-spacer-6-top">
      <div class="posted-in-section">
        <div class="posted-in-section__heading">
          <span class="glue-caption">
            posted in:
          </span>
        </div>
        <div class="posted-in-section__tags">
          <ul>
              
                  <li>
                      <a href="/search/?technology_categories=AI" class="glue-caption">AI</a>
                  </li>
              
                  <li>
                      <a href="/search/?content_type_categories=Announcements" class="glue-caption">Announcements</a>
                  </li>
              
                  <li>
                      <a href="/search/?content_type_categories=Learn" class="glue-caption">Learn</a>
                  </li>
              
              
                  <li>
                      <a href="/search/?tag=Influence" class="glue-caption">Influence</a>
                  </li>
              
          </ul>
      </div>
      </div>
      <div class="buttons-section">
        <div class="buttons-section__left">
          <a href="" class="glue-button--icon glue-elevation-level-1 disabled" aria-label="Previous">
            <svg role="presentation" aria-hidden="true" class="glue-icon">
              <use href="/glue-icon/#chevron-left"></use>
            </svg>
          </a>
          <span class="caption disabled">Previous</span>
        </div>
        <div class="buttons-section__right">
          <span class="caption ">Next</span>
          <a href="/announcing-adk-go-20/" class="glue-button--icon glue-elevation-level-1 "  aria-label="Next">
            <svg role="presentation" aria-hidden="true" class="glue-icon">
              <use href="/glue-icon/#chevron-right"></use>
            </svg>
          </a>
        </div>
      </div>
    </section>

    
    <section class="related-posts-container glue-page glue-spacer-6-top glue-spacer-3-bottom">
      <span class="glue-headline glue-headline--headline-3">Related Posts</span>
      <div class="related-posts-container__carousel glue-page glue-spacer-5-top">
        <div class="glue-carousel glue-carousel--cards glue-carousel-related-posts" aria-label="Related Posts">
          <!-- Previous -->
          <button class="glue-carousel__button glue-carousel__button--prev"
              aria-label="Go to the previous slide">
            <svg role="presentation" aria-hidden="true" class="glue-icon glue-icon--32px">
              <use href="/glue-icon/#chevron-left"></use>
            </svg>
          </button>
          <!-- Next -->
          <button class="glue-carousel__button glue-carousel__button--next"
              aria-label="Go to the next slide">
            <svg role="presentation" aria-hidden="true" class="glue-icon glue-icon--32px">
              <use href="/glue-icon/#chevron-right"></use>
            </svg>
          </button>
          <!-- List -->
          <div class="glue-carousel__viewport">
            <div class="glue-carousel__list">
              
                <a class="glue-card glue-carousel__item" href="/ml-development-in-vs-code-with-google-cloud-power-workbench-extension-now-available/">
                  <div aria-label="ML Development in VS Code with Google Cloud Power: Workbench Extension Now Available" class="glue-card__inner">
                    <picture class="glue-card__asset">
                      <img alt="ML Development in VS Code with Google Cloud Power: Workbench Extension Now Available" src="https://storage.googleapis.com/gweb-developer-goog-blog-assets/images/VS_code_blogpost_banner.2e16d0ba.fill-800x400.jpg">
                    </picture>
                    <div class="glue-card__content">
                      <div class="glue-card__tags glue-spacer-2-top">
                        
                            
                            
                            <span class="glue-label">AI</span>
                            
                            <span class="glue-label">Cloud</span>
                            
                            
                            <span class="glue-label">Tutorials</span>
                            
                            <span class="glue-label">Announcements</span>
                            
                        
                      </div>
                      <p class="glue-headline glue-headline--headline-5">ML Development in VS Code with Google Cloud Power: Workbench Extension Now Available</p>
                      <div class="glue-card__cta-custom glue-spacer-3-top">
                        <span class="glue-cta">JULY 1, 2026</span>
                        <svg aria-hidden="true" class="glue-icon glue-icon--24px" role="presentation">
                          <use href="/glue-icon/#arrow-forward"></use>
                        </svg>
                      </div>
                    </div>
                  </div>
                </a>
              
                <a class="glue-card glue-carousel__item" href="/we-terminated-a-tpu-mid-training-and-it-recovered-in-seconds-introduction-to-elastic-training-with-maxtext/">
                  <div aria-label="We terminated a TPU mid-training and it recovered in seconds:  Introduction to elastic training with MaxText" class="glue-card__inner">
                    <picture class="glue-card__asset">
                      <img alt="We terminated a TPU mid-training and it recovered in seconds:  Introduction to elastic training with MaxText" src="https://storage.googleapis.com/gweb-developer-goog-blog-assets/images/Cloud-1-banner.2e16d0ba.fill-800x400.png">
                    </picture>
                    <div class="glue-card__content">
                      <div class="glue-card__tags glue-spacer-2-top">
                        
                            
                            
                            <span class="glue-label">AI</span>
                            
                            <span class="glue-label">Cloud</span>
                            
                            
                            <span class="glue-label">Tutorials</span>
                            
                            <span class="glue-label">Announcements</span>
                            
                        
                      </div>
                      <p class="glue-headline glue-headline--headline-5">We terminated a TPU mid-training and it recovered in seconds:  Introduction to elastic training with MaxText</p>
                      <div class="glue-card__cta-custom glue-spacer-3-top">
                        <span class="glue-cta">JULY 6, 2026</span>
                        <svg aria-hidden="true" class="glue-icon glue-icon--24px" role="presentation">
                          <use href="/glue-icon/#arrow-forward"></use>
                        </svg>
                      </div>
                    </div>
                  </div>
                </a>
              
                <a class="glue-card glue-carousel__item" href="/why-we-built-adk-20/">
                  <div aria-label="Why we built ADK 2.0" class="glue-card__inner">
                    <picture class="glue-card__asset">
                      <img alt="Why we built ADK 2.0" src="https://storage.googleapis.com/gweb-developer-goog-blog-assets/images/gfd-why-adk2-banner.2e16d0ba.fill-800x400.png">
                    </picture>
                    <div class="glue-card__content">
                      <div class="glue-card__tags glue-spacer-2-top">
                        
                            
                            
                            <span class="glue-label">AI</span>
                            
                            <span class="glue-label">Cloud</span>
                            
                            
                            <span class="glue-label">How-To Guides</span>
                            
                            <span class="glue-label">Best Practices</span>
                            
                        
                      </div>
                      <p class="glue-headline glue-headline--headline-5">Why we built ADK 2.0</p>
                      <div class="glue-card__cta-custom glue-spacer-3-top">
                        <span class="glue-cta">JULY 1, 2026</span>
                        <svg aria-hidden="true" class="glue-icon glue-icon--24px" role="presentation">
                          <use href="/glue-icon/#arrow-forward"></use>
                        </svg>
                      </div>
                    </div>
                  </div>
                </a>
              
            </div>
          </div>
          <!-- Navigation dots -->
          <div class="glue-carousel__navigation" aria-label="Choose a page"
               data-glue-carousel-navigation-label="Selected tab $glue_carousel_page_number$ of $glue_carousel_page_total$">
          </div>
        </div>
      </div>
    </section>
    
  </div>


				
				

<div class="footer-linkboxes__wrapper">
  <nav class="footer-linkboxes" aria-label="Footer links">
    <ul class="footer-linkboxes__list">
      <li class="footer-linkbox">
        <span class="footer-linkbox-heading">
          Connect
        </span>
        <ul class="footer-linkbox-list">
          
            <li class="footer-linkbox-list__item">
              <a href="//googledevelopers.blogspot.com" class="footer-linkbox-list__link">
                Blog
              </a>
            </li>
          
            <li class="footer-linkbox-list__item">
              <a href="https://goo.gle/3FReQXN" class="footer-linkbox-list__link">
                Bluesky
              </a>
            </li>
          
            <li class="footer-linkbox-list__item">
              <a href="https://goo.gle/googlefordevs" class="footer-linkbox-list__link">
                Instagram
              </a>
            </li>
          
            <li class="footer-linkbox-list__item">
              <a href="https://goo.gle/gdevs-li" class="footer-linkbox-list__link">
                LinkedIn
              </a>
            </li>
          
            <li class="footer-linkbox-list__item">
              <a href="https://goo.gle/gdevs-tw" class="footer-linkbox-list__link">
                X (Twitter)
              </a>
            </li>
          
            <li class="footer-linkbox-list__item">
              <a href="https://goo.gle/developers" class="footer-linkbox-list__link">
                YouTube
              </a>
            </li>
          
        </ul>
      </li>
      <li class="footer-linkbox">
        <span class="footer-linkbox-heading">
          Programs
        </span>
        <ul class="footer-linkbox-list">
          
            <li class="footer-linkbox-list__item">
              <a href="//developers.google.com/program" class="footer-linkbox-list__link">
                Google Developer Program
              </a>
            </li>
          
            <li class="footer-linkbox-list__item">
              <a href="//developers.google.com/community/gdg" class="footer-linkbox-list__link">
                Google Developer Groups
              </a>
            </li>
          
            <li class="footer-linkbox-list__item">
              <a href="//developers.google.com/community/experts" class="footer-linkbox-list__link">
                Google Developer Experts
              </a>
            </li>
          
            <li class="footer-linkbox-list__item">
              <a href="//developers.google.com/community/accelerators" class="footer-linkbox-list__link">
                Accelerators
              </a>
            </li>
          
            <li class="footer-linkbox-list__item">
              <a href="//www.womentechmakers.com" class="footer-linkbox-list__link">
                Women Techmakers
              </a>
            </li>
          
            <li class="footer-linkbox-list__item">
              <a href="//developers.google.com/community/nvidia" class="footer-linkbox-list__link">
                Google Cloud &amp; NVIDIA
              </a>
            </li>
          
        </ul>
      </li>
      <li class="footer-linkbox">
        <span class="footer-linkbox-heading">
          Developer consoles
        </span>
        <ul class="footer-linkbox-list">
          
            <li class="footer-linkbox-list__item">
              <a href="//console.developers.google.com" class="footer-linkbox-list__link">
                Google API Console
              </a>
            </li>
          
            <li class="footer-linkbox-list__item">
              <a href="//console.cloud.google.com" class="footer-linkbox-list__link">
                Google Cloud Platform Console
              </a>
            </li>
          
            <li class="footer-linkbox-list__item">
              <a href="//play.google.com/apps/publish" class="footer-linkbox-list__link">
                Google Play Console
              </a>
            </li>
          
            <li class="footer-linkbox-list__item">
              <a href="//console.firebase.google.com" class="footer-linkbox-list__link">
                Firebase Console
              </a>
            </li>
          
            <li class="footer-linkbox-list__item">
              <a href="//console.actions.google.com" class="footer-linkbox-list__link">
                Actions on Google Console
              </a>
            </li>
          
            <li class="footer-linkbox-list__item">
              <a href="//cast.google.com/publish" class="footer-linkbox-list__link">
                Cast SDK Developer Console
              </a>
            </li>
          
            <li class="footer-linkbox-list__item">
              <a href="//chrome.google.com/webstore/developer/dashboard" class="footer-linkbox-list__link">
                Chrome Web Store Dashboard
              </a>
            </li>
          
            <li class="footer-linkbox-list__item">
              <a href="//console.home.google.com/" class="footer-linkbox-list__link">
                Google Home Developer Console
              </a>
            </li>
          
        </ul>
      </li>
    </ul>
  </nav>
</div>
<div class="footer-utility__wrapper">
  <div>
    <nav class="footer-sites" aria-label="Other Google Developers websites">
      <a href="https://developers.google.com/" class="site-logo-link" data-label="Site logo">
        <img src="https://storage.googleapis.com/gweb-developer-goog-blog-cms-assets/site/20260519-162827/images/g-dev.svg" class="site-logo" alt="Google for Developers">
      </a>
      <ul class="footer-sites-list">
        <li class="footer-sites-item">
          <a href="//developer.android.com" class="footer-sites-link">
            Android
          </a>
        </li>
        <li class="footer-sites-item">
          <a href="//developer.chrome.com/home" class="footer-sites-link">
            Chrome
          </a>
        </li>
        <li class="footer-sites-item">
          <a href="//firebase.google.com" class="footer-sites-link">
            Firebase
          </a>
        </li>
        <li class="footer-sites-item">
          <a href="//cloud.google.com" class="footer-sites-link">
            Google Cloud Platform
          </a>
        </li>
        <li class="footer-sites-item">
          <a href="//developers.google.com/products" class="footer-sites-link">
            All products
          </a>
        </li>
        <li class="footer-sites-item">
          <button aria-hidden="true" class="glue-cookie-notification-bar-control footer-sites-link">
            Manage cookies
          </button>
        </li>
      </ul>
    </nav>
    <nav class="footer-utility-links">
      <ul class="footer-utility-list">
        <li class="footer-utility-item">
          <a href="//developers.google.com/terms/site-terms" class="footer-utility-link">
            Terms
          </a>
        </li>
        <li class="footer-utility-item">
          <a href="//policies.google.com/privacy" class="footer-utility-link">
            Privacy
          </a>
        </li>
      </ul>
    </nav>
  </div>
</div>


        
				

        
        <script nonce="9pDkoBLhgOGzHDUP7i6Lcw==" src="https://www.youtube.com/player_api"></script>
        <script nonce="9pDkoBLhgOGzHDUP7i6Lcw==" src="//www.gstatic.com/glue/v27_1/glue.min.js"></script>
        <script nonce="9pDkoBLhgOGzHDUP7i6Lcw==" type="text/javascript" src="https://storage.googleapis.com/gweb-developer-goog-blog-cms-assets/site/20260519-162827/js/dgc_blog.js"></script>

        <script nonce="9pDkoBLhgOGzHDUP7i6Lcw==" src="https://www.gstatic.com/glue/cookienotificationbar/cookienotificationbar.min.js"
            data-glue-cookie-notification-bar-category="2A"
            data-glue-cookie-notification-bar-site-id="developers.googleblog.com"></script>

        
  <script src="https://storage.googleapis.com/gweb-developer-goog-blog-cms-assets/site/20260519-162827/js/blog_detail.js" nonce="9pDkoBLhgOGzHDUP7i6Lcw=="></script>
  <script src="https://storage.googleapis.com/gweb-developer-goog-blog-cms-assets/site/20260519-162827/js/prism.js" nonce="9pDkoBLhgOGzHDUP7i6Lcw=="></script>

    </body>
</html>


