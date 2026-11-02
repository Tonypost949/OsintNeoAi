// Shared by the existing search box and the server-side search_atlas tool.
// Source of truth: assets/data.json. This module contains no catalog records.
export function recordText(record, kind, labels, categories) {
  if (kind === "entity") {
    return [
      record.id, record.type, record.name, record.primaryTab,
      (record.relatedIds || []).join(" "), record.sourceDoc, record.status,
      record.lastUpdated, record.notes, record.location,
    ].join(" ").toLowerCase();
  }
  return [
    `${labels.get(record[0]) || record[0]}/${record[1]}`,
    categories[record[2]] || "", record[6] || "",
  ].join(" ").toLowerCase();
}

export function matchesQuery(record, kind, query, labels, categories) {
  const normalized = String(query || "").trim().toLowerCase();
  return !normalized || recordText(record, kind, labels, categories).includes(normalized);
}

export function sourceLink(value) {
  // Only an explicit HTTP(S) URL in SOURCE_DOC is a link; never guess from a name.
  const text = String(value || "").trim();
  const match = text.match(/https?:\/\/[^\s<>"'`]+/i);
  if (!match) return null;
  // Full URL fields (including GitHub paths ending with punctuation) stay exact.
  const candidate = match[0] === text ? text : match[0].replace(/[),.;]+$/, "");
  try {
    const url = new URL(candidate);
    return ["http:", "https:"].includes(url.protocol) && !url.username && !url.password
      ? candidate : null;
  } catch { return null; }
}

export function searchAtlas(data, query, limit = 10) {
  const cap = Math.min(10, Math.max(1, Number(limit) || 10));
  if (typeof query !== "string" || !query.trim()) return [];
  const labels = new Map(data.repos.map((repo) =>
    [repo.name, `${repo.owner}/${repo.repositoryName}`]));
  const results = [];
  // Prefer entity matches for people/IDs; search all file records as well.
  const normalized = query.trim().toLowerCase();
  const entities = [...(data.entities || [])].sort((a, b) =>
    Number(b.id.toLowerCase() === normalized || b.name.toLowerCase() === normalized) -
    Number(a.id.toLowerCase() === normalized || a.name.toLowerCase() === normalized));
  for (const entity of entities) {
    if (!matchesQuery(entity, "entity", query, labels, data.categories)) continue;
    results.push({
      kind: "entity", id: entity.id, title: entity.name, category: entity.type,
      primaryTab: entity.primaryTab, relatedIds: entity.relatedIds,
      sourceDoc: entity.sourceDoc, url: sourceLink(entity.sourceDoc),
      status: entity.status, date: entity.lastUpdated,
      notes: entity.notes, location: entity.location,
    });
    if (results.length >= cap) return results;
  }
  for (const file of data.files) {
    if (!matchesQuery(file, "file", query, labels, data.categories)) continue;
    results.push({
      kind: "file", title: file[1], path: file[1],
      repository: labels.get(file[0]) || file[0],
      category: data.categories[file[2]], url: sourceLink(file[6]),
    });
    if (results.length >= cap) break;
  }
  return results;
}
