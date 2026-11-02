// Serves the atlas index (assets/data.json) from the Skywork-published site.
// The browser asks this deployment for assets/data.json; vercel.json rewrites
// that path here because Vercel's external-rewrite proxy cannot fetch the
// Skywork file (it gets a gate page), while a function fetch works.
let cache;
export default async function handler(req, res) {
  try {
    if (!cache) {
      const r = await fetch("https://web-1025bwvi1vdt.skywork.website/assets/data.json");
      if (!r.ok) throw new Error("index fetch HTTP " + r.status);
      cache = Buffer.from(await r.arrayBuffer());
    }
    res.statusCode = 200;
    res.setHeader("Content-Type", "application/json; charset=utf-8");
    res.setHeader("Cache-Control", "public, max-age=0, s-maxage=600, stale-while-revalidate=60");
    res.end(cache);
  } catch (e) {
    cache = undefined;
    res.statusCode = 502;
    res.setHeader("Content-Type", "application/json");
    res.end(JSON.stringify({ error: "atlas index unavailable" }));
  }
}
