const fs = require('fs');
const path = require('path');

const ROOT_DIR = path.resolve(__dirname, '..');
const SKILLS_DIR = path.join(ROOT_DIR, 'skills');
const OUTPUT_DIR = path.join(ROOT_DIR, 'public', 'data');
const OUTPUT_FILE = path.join(OUTPUT_DIR, 'skills.json');

// Category classification heuristics
function categorizeSkill(name, description, content) {
  const n = name.toLowerCase();
  const desc = description.toLowerCase();
  const text = (name + ' ' + description + ' ' + content).toLowerCase();
  
  if (n.includes('osint') || n.includes('dossier') || n.includes('forensic') || desc.includes('osint') || desc.includes('forensic') || desc.includes('maltego')) {
    return 'OSINT & Intelligence';
  }
  if (n.includes('android') || n.includes('chrome') || n.includes('firebase') || n.includes('data-apps') || n.includes('notebook')) {
    return 'Web, Mobile & Apps';
  }
  if (n.includes('security') || n.includes('loss-prevention') || n.includes('attribution') || n.includes('auth')) {
    return 'Security & Governance';
  }
  if (n.includes('ml-') || n.includes('ai-ml') || n.includes('bigframes') || n.includes('gemini') || desc.includes('machine learning') || desc.includes('genai')) {
    return 'AI & Machine Learning';
  }
  if (n.startsWith('gcp-') || n.includes('dataflow') || n.includes('composer') || n.includes('airflow') || n.includes('spark') || n.includes('pipeline')) {
    return 'GCP Infrastructure & Pipelines';
  }
  if (n.includes('bigquery') || n.includes('dataform') || n.includes('dbt') || n.includes('lakehouse') || n.includes('data-autocleaning') || n.includes('data-assets')) {
    return 'BigQuery & Data Platforms';
  }
  return 'Development & Tooling';
}

// Generate tags from content
function extractTags(name, description, content) {
  const text = (name + ' ' + description + ' ' + content).toLowerCase();
  const candidates = [
    { tag: 'OSINT', match: ['osint', 'investigation', 'forensic'] },
    { tag: 'BigQuery', match: ['bigquery', 'bq'] },
    { tag: 'GCP', match: ['gcp', 'google cloud', 'gcloud'] },
    { tag: 'SQL', match: ['sql', 'sqlx', 'dbt'] },
    { tag: 'Python', match: ['python', 'pip', 'script'] },
    { tag: 'AI/LLM', match: ['gemini', 'llm', 'genai', 'ai'] },
    { tag: 'Pipelines', match: ['pipeline', 'etl', 'elt', 'orchestration', 'composer'] },
    { tag: 'Security', match: ['security', 'auth', 'prevention', 'protection'] },
    { tag: 'Data Science', match: ['machine learning', 'analytics', 'statistics', 'dataframe', 'notebook'] },
    { tag: 'Automation', match: ['automation', 'transform', 'scraper', 'cli'] },
    { tag: 'Web & API', match: ['chrome', 'extension', 'firebase', 'android', 'api', 'rest'] }
  ];

  const tags = new Set();
  candidates.forEach(c => {
    if (c.match.some(m => text.includes(m))) {
      tags.add(c.tag);
    }
  });

  return Array.from(tags);
}

// Simple YAML frontmatter parser
function parseFrontmatter(markdown) {
  const match = markdown.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/);
  if (!match) {
    return { frontmatter: {}, body: markdown };
  }

  const rawYaml = match[1];
  const body = match[2];
  const frontmatter = {};

  const lines = rawYaml.split(/\r?\n/);
  let currentKey = null;
  let currentValue = '';

  for (let line of lines) {
    const keyMatch = line.match(/^([a-zA-Z0-9_-]+):\s*(.*)$/);
    if (keyMatch) {
      if (currentKey) {
        frontmatter[currentKey] = currentValue.trim();
      }
      currentKey = keyMatch[1];
      currentValue = keyMatch[2];
    } else if (currentKey) {
      currentValue += ' ' + line.trim();
    }
  }
  if (currentKey) {
    frontmatter[currentKey] = currentValue.trim();
  }

  return { frontmatter, body };
}

// Extract quick commands from markdown
function extractCommands(body) {
  const commands = [];
  const codeBlockRegex = /```(?:powershell|bash|sh|cmd|shell|python)?\r?\n([\s\S]*?)```/g;
  let match;
  while ((match = codeBlockRegex.exec(body)) !== null) {
    const lines = match[1].trim().split(/\r?\n/);
    lines.forEach(line => {
      const trimmed = line.trim();
      if (trimmed && !trimmed.startsWith('#') && (trimmed.startsWith('python') || trimmed.startsWith('gcloud') || trimmed.startsWith('bq') || trimmed.startsWith('streamlit') || trimmed.startsWith('node') || trimmed.startsWith('android') || trimmed.startsWith('dbt') || trimmed.startsWith('dataform'))) {
        if (!commands.includes(trimmed)) {
          commands.push(trimmed);
        }
      }
    });
  }
  return commands.slice(0, 5);
}

// Recursively list files in directory
function listFilesRecursively(dir, basePath = '') {
  let results = [];
  if (!fs.existsSync(dir)) return results;

  const list = fs.readdirSync(dir, { withFileTypes: true });
  for (let file of list) {
    const fullPath = path.join(dir, file.name);
    const relPath = path.join(basePath, file.name).replace(/\\/g, '/');
    if (file.isDirectory()) {
      results = results.concat(listFilesRecursively(fullPath, relPath));
    } else {
      const stats = fs.statSync(fullPath);
      results.push({
        name: file.name,
        path: relPath,
        sizeBytes: stats.size,
        extension: path.extname(file.name).toLowerCase()
      });
    }
  }
  return results;
}

function processSkills() {
  console.log(`[extract-skills] Scanning skills from: ${SKILLS_DIR}`);

  if (!fs.existsSync(SKILLS_DIR)) {
    console.error(`[extract-skills] Error: Directory not found: ${SKILLS_DIR}`);
    process.exit(1);
  }

  const skillDirs = fs.readdirSync(SKILLS_DIR, { withFileTypes: true })
    .filter(dirent => dirent.isDirectory())
    .map(dirent => dirent.name);

  const skillsData = [];
  let totalScriptsCount = 0;
  let totalReferencesCount = 0;

  for (let dirName of skillDirs) {
    const skillPath = path.join(SKILLS_DIR, dirName);
    const skillMdPath = path.join(skillPath, 'SKILL.md');

    let rawMarkdown = '';
    let frontmatter = {};
    let body = '';

    if (fs.existsSync(skillMdPath)) {
      rawMarkdown = fs.readFileSync(skillMdPath, 'utf8');
      const parsed = parseFrontmatter(rawMarkdown);
      frontmatter = parsed.frontmatter;
      body = parsed.body;
    } else {
      body = `# ${dirName}\nNo SKILL.md found.`;
    }

    const name = frontmatter.name || dirName;
    const description = frontmatter.description || 'Comprehensive workflow automation and execution guidance.';
    const category = categorizeSkill(name, description, rawMarkdown);
    const tags = extractTags(name, description, rawMarkdown);
    const commands = extractCommands(body);

    // List bundled assets
    const scriptsDir = path.join(skillPath, 'scripts');
    const referencesDir = path.join(skillPath, 'references');
    const resourcesDir = path.join(skillPath, 'resources');
    const examplesDir = path.join(skillPath, 'examples');

    const scripts = listFilesRecursively(scriptsDir, 'scripts');
    const references = listFilesRecursively(referencesDir, 'references');
    const resources = listFilesRecursively(resourcesDir, 'resources');
    const examples = listFilesRecursively(examplesDir, 'examples');

    const allAssets = listFilesRecursively(skillPath, '');

    totalScriptsCount += scripts.length;
    totalReferencesCount += references.length;

    // Calculate line count and headings
    const linesCount = rawMarkdown.split(/\r?\n/).length;
    const headings = (body.match(/^#{1,3}\s+(.+)$/gm) || []).map(h => h.replace(/^#{1,3}\s+/, '').trim());

    skillsData.push({
      id: dirName,
      name,
      slug: dirName,
      description,
      category,
      tags,
      quickCommands: commands,
      headings: headings.slice(0, 8),
      lineCount: linesCount,
      assetsSummary: {
        totalFiles: allAssets.length,
        scriptsCount: scripts.length,
        referencesCount: references.length,
        resourcesCount: resources.length,
        examplesCount: examples.length
      },
      scripts,
      references,
      resources,
      examples,
      rawMarkdown,
      body,
      updatedAt: new Date().toISOString()
    });
  }

  // Sort alphabetically by name
  skillsData.sort((a, b) => a.name.localeCompare(b.name));

  // Meta statistics
  const categories = {};
  skillsData.forEach(s => {
    categories[s.category] = (categories[s.category] || 0) + 1;
  });

  const outputPayload = {
    version: '1.0.0',
    generatedAt: new Date().toISOString(),
    totalSkills: skillsData.length,
    totalScripts: totalScriptsCount,
    totalReferences: totalReferencesCount,
    categories,
    skills: skillsData
  };

  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(outputPayload, null, 2), 'utf8');
  console.log(`[extract-skills] Successfully generated: ${OUTPUT_FILE}`);
  console.log(`[extract-skills] Total Skills: ${skillsData.length} | Scripts: ${totalScriptsCount} | References: ${totalReferencesCount}`);
}

processSkills();
