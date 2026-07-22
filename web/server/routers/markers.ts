import { publicProcedure, router } from "./_core/trpc";
import { z } from "zod";
import * as fs from "fs";
import * as path from "path";

const CACHE_DIR = path.join(process.cwd(), "opencode_work");
const CACHE_FILE = path.join(CACHE_DIR, "city_markers_cache.json");

function loadMarkers() {
  try {
    if (fs.existsSync(CACHE_FILE)) {
      const data = fs.readFileSync(CACHE_FILE, "utf-8");
      return JSON.parse(data);
    }
  } catch (error) {
    console.error("Failed to load markers cache:", error);
  }
  return {};
}

function getCacheStats(markers: Record<string, any>) {
  const values = Object.values(markers);
  const cities = [...new Set(values.map((m: any) => m.city || "Unknown"))];

  return {
    total: values.length,
    cities,
    last_updated: values.reduce(
      (latest: string, m: any) =>
        m.last_updated && m.last_updated > latest ? m.last_updated : latest,
      ""
    ),
  };
}

export const markersRouter = router({
  list: publicProcedure.query(() => {
    const markers = loadMarkers();
    const stats = getCacheStats(markers);
    return {
      markers: Object.values(markers),
      stats,
    };
  }),

  get: publicProcedure
    .input(z.object({ id: z.string() }))
    .query(({ input }) => {
      const markers = loadMarkers();
      return markers[input.id] || null;
    }),
});
