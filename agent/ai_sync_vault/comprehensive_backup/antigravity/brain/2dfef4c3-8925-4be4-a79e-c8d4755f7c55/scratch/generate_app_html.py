import json
import os

repo_root = r"c:\Users\HP\OneDrive\Documents\OsintNeoAi"
json_path = os.path.join(repo_root, "modules_data.json")
html_path = os.path.join(repo_root, "capabilities_dashboard.html")

with open(json_path, 'r', encoding='utf-8') as f:
    modules_data = json.load(f)

# Filter modules to include only those with actual content or functions/classes to avoid cluttering the UI,
# but keep a comprehensive list. We'll load the full JSON into the HTML page.
# To keep the HTML file size reasonable while retaining 2200+ modules, we will include the data directly.
# Let's compress or prune empty entries if they are too repetitive, but keep the ones with functions/classes/descriptions.
pruned_data = []
for m in modules_data:
    # Always include if it has functions/classes, or has a description that isn't generic, or is in core/pipelines
    has_funcs = len(m.get("functions", [])) > 0 or len(m.get("classes", [])) > 0
    is_core = any(x in m["file"] for x in ["core/", "pipelines/", "database/"])
    if has_funcs or is_core or m["type"] in ["sql", "markdown"]:
        pruned_data.append(m)

print(f"Pruned dataset size for UI: {len(pruned_data)} elements (down from {len(modules_data)})")

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OsintNeoAi Capabilities & Functions Explorer</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #0d0f14;
            --card-bg: rgba(22, 28, 41, 0.45);
            --card-border: rgba(255, 255, 255, 0.08);
            --text-primary: #f3f4f6;
            --text-secondary: #9ca3af;
            --accent-glow: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
            --accent-blue: #3b82f6;
            --accent-purple: #8b5cf6;
            --accent-cyan: #06b6d4;
            --accent-green: #10b981;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            background-color: var(--bg-color);
            color: var(--text-primary);
            font-family: 'Outfit', sans-serif;
            min-height: 100vh;
            overflow-x: hidden;
            background-image: 
                radial-gradient(at 10% 20%, rgba(59, 130, 246, 0.15) 0px, transparent 50%),
                radial-gradient(at 90% 80%, rgba(139, 92, 246, 0.15) 0px, transparent 50%);
            background-attachment: fixed;
        }}

        header {{
            padding: 4rem 2rem 2rem 2rem;
            text-align: center;
            max-width: 1200px;
            margin: 0 auto;
            position: relative;
        }}

        h1 {{
            font-size: 3.5rem;
            font-weight: 700;
            background: linear-gradient(to right, #3b82f6, #8b5cf6, #06b6d4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
            letter-spacing: -0.05em;
        }}

        .subtitle {{
            font-size: 1.2rem;
            color: var(--text-secondary);
            max-width: 600px;
            margin: 0 auto 3rem auto;
            font-weight: 300;
        }}

        /* Search & Filters */
        .controls-container {{
            max-width: 1200px;
            margin: 0 auto 3rem auto;
            padding: 0 2rem;
        }}

        .search-box {{
            width: 100%;
            padding: 1.2rem 2rem;
            font-size: 1.1rem;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            color: var(--text-primary);
            font-family: inherit;
            backdrop-filter: blur(12px);
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            outline: none;
        }}

        .search-box:focus {{
            border-color: var(--accent-blue);
            box-shadow: 0 0 15px rgba(59, 130, 246, 0.25);
        }}

        .filters {{
            display: flex;
            gap: 1rem;
            margin-top: 1.5rem;
            flex-wrap: wrap;
            justify-content: center;
        }}

        .filter-btn {{
            padding: 0.6rem 1.5rem;
            border-radius: 50px;
            border: 1px solid var(--card-border);
            background: rgba(22, 28, 41, 0.4);
            color: var(--text-secondary);
            font-family: inherit;
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }}

        .filter-btn.active, .filter-btn:hover {{
            background: var(--accent-glow);
            color: white;
            border-color: transparent;
            box-shadow: 0 4px 15px rgba(139, 92, 246, 0.2);
        }}

        /* Main Grid */
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
            gap: 2rem;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem 5rem 2rem;
        }}

        /* Cards */
        .card {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 20px;
            padding: 2rem;
            backdrop-filter: blur(16px);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}

        .card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
            opacity: 0;
            transition: opacity 0.4s ease;
            z-index: 0;
        }}

        .card:hover {{
            transform: translateY(-8px);
            border-color: rgba(139, 92, 246, 0.3);
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4);
        }}

        .card:hover::before {{
            opacity: 1;
        }}

        .card-header {{
            position: relative;
            z-index: 1;
            margin-bottom: 1.5rem;
        }}

        .file-badge {{
            display: inline-block;
            padding: 0.3rem 0.8rem;
            border-radius: 8px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 1rem;
        }}

        .badge-py {{ background: rgba(59, 130, 246, 0.15); color: #60a5fa; }}
        .badge-sql {{ background: rgba(6, 182, 212, 0.15); color: #22d3ee; }}
        .badge-md {{ background: rgba(16, 185, 129, 0.15); color: #34d399; }}

        .file-path {{
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--text-primary);
            word-break: break-all;
            line-height: 1.4;
        }}

        .card-body {{
            position: relative;
            z-index: 1;
            flex-grow: 1;
        }}

        .module-desc {{
            color: var(--text-secondary);
            font-size: 0.95rem;
            line-height: 1.6;
            margin-bottom: 1.5rem;
            font-weight: 300;
        }}

        .expander {{
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            padding-top: 1rem;
            margin-top: 1rem;
        }}

        .expander-title {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: var(--text-primary);
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
            user-select: none;
            padding: 0.5rem 0;
        }}

        .expander-content {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease-out;
        }}

        .expander.open .expander-content {{
            max-height: 400px;
            overflow-y: auto;
        }}

        .func-item {{
            padding: 0.6rem 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.03);
            font-size: 0.85rem;
        }}

        .func-name {{
            font-family: monospace;
            color: #f472b6;
            font-weight: 600;
        }}

        .func-args {{
            color: var(--text-secondary);
        }}

        .func-desc {{
            color: #9ca3af;
            margin-top: 0.2rem;
            font-size: 0.8rem;
            font-weight: 300;
        }}

        .stat-badge {{
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            background: rgba(255, 255, 255, 0.03);
            padding: 0.3rem 0.6rem;
            border-radius: 6px;
            font-size: 0.8rem;
            color: var(--text-secondary);
            margin-right: 0.5rem;
            margin-top: 0.5rem;
        }}

        /* Pagination & Stats */
        .stats-summary {{
            text-align: center;
            margin-bottom: 2rem;
            font-size: 0.95rem;
            color: var(--text-secondary);
        }}

        .stats-val {{
            color: var(--accent-blue);
            font-weight: 600;
        }}
    </style>
</head>
<body>

    <header>
        <h1>OsintNeoAi Capabilities Explorer</h1>
        <p class="subtitle">Unified inventory of all intelligence-gathering engines, modules, database utilities, and forensic workflows.</p>
        
        <div class="stats-summary">
            Loaded <span class="stats-val" id="count-display">0</span> components out of <span class="stats-val">{len(pruned_data)}</span> registered modules.
        </div>
    </header>

    <div class="controls-container">
        <input type="text" id="search-input" class="search-box" placeholder="Search functions, file paths, and workflow classes (e.g. 'setup_kb', 'anomaly', 'weaver')...">
        
        <div class="filters">
            <button class="filter-btn active" onclick="filterType('all')">All Files</button>
            <button class="filter-btn" onclick="filterType('python')">Python Connectors & Scripts</button>
            <button class="filter-btn" onclick="filterType('sql')">BigQuery DDL & Queries</button>
            <button class="filter-btn" onclick="filterType('markdown')">OSINT Intel Briefings</button>
        </div>
    </div>

    <main class="grid" id="cards-grid">
        <!-- Rendered dynamically -->
    </main>

    <script>
        const rawData = {json.dumps(pruned_data)};
        let activeTypeFilter = 'all';

        function renderCards(filterText = '') {{
            const grid = document.getElementById('cards-grid');
            grid.innerHTML = '';
            
            let filtered = rawData.filter(m => {{
                // Type Filter
                if (activeTypeFilter !== 'all' && m.type !== activeTypeFilter) return false;
                
                // Search Text Filter
                if (filterText) {{
                    const query = filterText.toLowerCase();
                    const pathMatch = m.file.toLowerCase().includes(query);
                    const descMatch = m.description.toLowerCase().includes(query);
                    
                    const funcMatch = m.functions.some(f => 
                        f.name.toLowerCase().includes(query) || 
                        f.docstring.toLowerCase().includes(query)
                    );
                    
                    const classMatch = m.classes && m.classes.some(c => 
                        c.name.toLowerCase().includes(query) || 
                        c.docstring.toLowerCase().includes(query)
                    );
                    
                    return pathMatch || descMatch || funcMatch || classMatch;
                }}
                return true;
            }});

            document.getElementById('count-display').innerText = filtered.length;

            filtered.forEach(m => {{
                const card = document.createElement('div');
                card.className = 'card';
                
                let badgeClass = 'badge-py';
                let typeLabel = 'Python Module';
                if (m.type === 'sql') {{
                    badgeClass = 'badge-sql';
                    typeLabel = 'SQL Query';
                }} else if (m.type === 'markdown') {{
                    badgeClass = 'badge-md';
                    typeLabel = 'OSINT Brief';
                }}

                let functionsList = '';
                if (m.functions && m.functions.length > 0) {{
                    functionsList = `
                        <div class="expander">
                            <div class="expander-title" onclick="toggleExpander(this)">
                                <span>Functions (${{m.functions.length}})</span>
                                <span>▼</span>
                            </div>
                            <div class="expander-content">
                                ${{m.functions.map(f => `
                                    <div class="func-item">
                                        <div class="func-name">${{f.name}}<span class="func-args">(${{f.arguments.join(', ')}})</span></div>
                                        <div class="func-desc">${{f.docstring}}</div>
                                    </div>
                                `).join('')}}
                            </div>
                        </div>
                    `;
                }}

                let classesList = '';
                if (m.classes && m.classes.length > 0) {{
                    classesList = `
                        <div class="expander">
                            <div class="expander-title" onclick="toggleExpander(this)">
                                <span>Classes (${{m.classes.length}})</span>
                                <span>▼</span>
                            </div>
                            <div class="expander-content">
                                ${{m.classes.map(c => `
                                    <div class="func-item">
                                        <div class="func-name" style="color: #a78bfa;">class ${{c.name}}</div>
                                        <div class="func-desc">${{c.docstring}}</div>
                                    </div>
                                `).join('')}}
                            </div>
                        </div>
                    `;
                }}

                card.innerHTML = `
                    <div class="card-header">
                        <span class="file-badge ${{badgeClass}}">${{typeLabel}}</span>
                        <div class="file-path">${{m.file}}</div>
                    </div>
                    <div class="card-body">
                        <p class="module-desc">${{m.description}}</p>
                        ${{classesList}}
                        ${{functionsList}}
                    </div>
                `;
                grid.appendChild(card);
            }});
        }}

        function toggleExpander(el) {{
            const expander = el.parentElement;
            expander.classList.toggle('open');
            const arrow = el.querySelector('span:last-child');
            arrow.innerText = expander.classList.contains('open') ? '▲' : '▼';
        }}

        function filterType(type) {{
            activeTypeFilter = type;
            document.querySelectorAll('.filter-btn').forEach(btn => {{
                btn.classList.remove('active');
            }});
            event.target.classList.add('active');
            renderCards(document.getElementById('search-input').value);
        }}

        document.getElementById('search-input').addEventListener('input', (e) => {{
            renderCards(e.target.value);
        }});

        // Initial Render
        renderCards();
    </script>
</body>
</html>
"""

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Generated dashboard HTML app at {html_path}")
