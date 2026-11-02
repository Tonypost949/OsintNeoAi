const panel = document.getElementById("atlas-chat");
const status = document.getElementById("chat-status");
const log = document.getElementById("chat-log");
const form = document.getElementById("chat-form");
const input = document.getElementById("chat-question");
const send = document.getElementById("chat-send");
const retry = document.getElementById("chat-check");
const history = [];
let configured = false;

function endpoint() {
  const url = new URL(window.CHAT_API_URL, window.location.href);
  if (url.protocol !== "https:" && url.origin !== window.location.origin)
    throw new Error("Set CHAT_API_URL to the deployed backend's HTTPS URL.");
  return url.href;
}
function setStatus(text, ready = false) {
  status.textContent = text;
  panel.dataset.ready = String(ready);
}
function message(role, text) {
  const article = document.createElement("article");
  article.className = "chat-message";
  const heading = document.createElement("h3");
  heading.textContent = role;
  const body = document.createElement("p");
  body.textContent = text;
  article.append(heading, body);
  log.append(article);
  return article;
}
function sourceUrl(value) {
  try {
    const url = new URL(value);
    return ["http:", "https:"].includes(url.protocol) && !url.username && !url.password ? value : null;
  } catch { return null; }
}
async function request(method, body) {
  let response;
  try {
    response = await fetch(endpoint(), {
      method, headers: body ? { "Content-Type": "application/json" } : {},
      ...(body ? { body: JSON.stringify(body) } : {}),
      signal: AbortSignal.timeout(method === "GET" ? 10000 : 60000),
      cache: "no-store", credentials: "omit",
    });
  } catch (error) {
    throw new Error(error.message?.includes("CHAT_API_URL") ? error.message :
      "Backend unavailable. Deploy api/chat.mjs, set its server-side GEMINI_API_KEY, and point CHAT_API_URL to that function.");
  }
  if (!response.headers.get("content-type")?.includes("application/json"))
    throw new Error("No chat backend at this endpoint. The static host cannot run api/chat.mjs; deploy it separately and set CHAT_API_URL.");
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `Backend request failed (HTTP ${response.status}).`);
  return data;
}
async function check() {
  retry.disabled = true;
  try {
    const data = await request("GET");
    if (data.service !== "atlas-gemini-chat" || !data.configured)
      throw new Error("The configured endpoint is not a ready atlas chat backend.");
    configured = true;
    setStatus("BACKEND CONFIGURED — Gemini will be verified when you send a question.", true);
  } catch (error) {
    configured = false;
    setStatus(`NOT LIVE — ${error.message}`);
  } finally { retry.disabled = false; }
}
retry.addEventListener("click", check);
form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const question = input.value.trim();
  if (!question || send.disabled) return;
  send.disabled = true;
  retry.disabled = true;
  if (!configured) await check();
  if (!configured) { send.disabled = false; return; }
  message("You", question);
  setStatus("Waiting for Gemini and the required atlas search…", true);
  try {
    const data = await request("POST", { message: question, history });
    if (typeof data.answer !== "string" || !data.answer.trim() || !Array.isArray(data.results))
      throw new Error("The backend returned an invalid response. No AI answer shown.");
    const article = message("Gemini", data.answer);
    const heading = document.createElement("h3");
    heading.textContent = data.results.length ? "Atlas search results · full source URLs" : "Atlas search: no matching records returned.";
    article.append(heading);
    const list = document.createElement("ul");
    for (const result of data.results) {
      const row = document.createElement("li");
      const title = document.createElement("span");
      title.textContent = result.kind === "file"
        ? `${result.repository}/${result.path} · ${result.category}`
        : `${result.id} · ${result.title} · ${result.category} · ${result.primaryTab || ""}`;
      row.append(title);
      const url = sourceUrl(result.url);
      if (url) {
        const link = document.createElement("a");
        link.href = url;
        link.textContent = url;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        row.append(document.createElement("br"), link);
      } else {
        const note = document.createElement("p");
        note.textContent = `No source URL supplied${result.sourceDoc ? ` · SOURCE_DOC: ${result.sourceDoc}` : ""}`;
        row.append(note);
      }
      list.append(row);
    }
    article.append(list);
    history.push({ role: "user", text: question }, { role: "model", text: data.answer });
    history.splice(0, Math.max(0, history.length - 6));
    input.value = "";
    setStatus("LIVE — Gemini answered after searching the atlas.", true);
  } catch (error) {
    setStatus(`CHAT UNAVAILABLE — ${error.message}`);
    // An error is status text, never a fabricated assistant message.
  } finally {
    send.disabled = false;
    retry.disabled = false;
  }
});
check();
