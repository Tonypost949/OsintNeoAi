/**
 * markers.ts
 * ==========
 * tRPC router that serves geo-marker data for the CityCyberReconMap.
 *
 * Reads the JSON cache written by agent/fetch_geodata.py.
 * Supports optional filtering by is_exposed and state.
 *
 * Routes:
 *   markers.list     → all markers (with optional filter)
 *   markers.exposed  → only exposed markers
 *   markers.refresh  → trigger cache refresh (runs fetch_geodata.py)
 */

import { z } from "zod";
import { router, publicProcedure } from "../_core/trpc";
import fs from "fs";
import path from "path";
import { execSync } from "child_process";

// ── Cache file path ──────────────────────────────────────────────────────────
const CACHE_PATH = path.resolve(
  __dirname,
  "../../client/src/data/cyber_recon_geo.json"
);

const FETCHER_SCRIPT = path.resolve(
  __dirname,
  "../../../../agent/fetch_geodata.py"
);

// ── Zod schema for a single marker ──────────────────────────────────────────
const MarkerSchema = z.object({
  domain:      z.string(),
  ip:          z.string(),
  city:        z.string(),
  state:       z.string(),
  country:     z.string().default("US"),
  lat:         z.number(),
  lng:         z.number(),
  status_code: z.number().default(0),
  is_exposed:  z.boolean().default(false),
  isp:         z.string().default(""),
  record_type: z.string().default("A"),
});

export type Marker = z.infer<typeof MarkerSchema>;

// ── Cache loader ─────────────────────────────────────────────────────────────
function loadCache(): { markers: Marker[]; generated_at: string; total: number; exposed_count: number } {
  if (!fs.existsSync(CACHE_PATH)) {
    return { markers: [], generated_at: "", total: 0, exposed_count: 0 };
  }
  try {
    const raw = JSON.parse(fs.readFileSync(CACHE_PATH, "utf-8"));
    const markers = (raw.markers ?? []).map((m: unknown) => MarkerSchema.parse(m));
    return {
      markers,
      generated_at:  raw.generated_at  ?? "",
      total:         raw.total         ?? markers.length,
      exposed_count: raw.exposed_count ?? markers.filter((m: Marker) => m.is_exposed).length,
    };
  } catch (e) {
    console.error("[markers.ts] Failed to parse cache:", e);
    return { markers: [], generated_at: "", total: 0, exposed_count: 0 };
  }
}

// ── Router definition ─────────────────────────────────────────────────────────
export const markersRouter = router({
  /** Return all markers, optionally filtered */
  list: publicProcedure
    .input(
      z.object({
        exposed_only: z.boolean().optional().default(false),
        state:        z.string().optional(),
        city:         z.string().optional(),
      })
    )
    .query(({ input }) => {
      const cache = loadCache();
      let markers = cache.markers;

      if (input.exposed_only) {
        markers = markers.filter((m) => m.is_exposed);
      }
      if (input.state) {
        markers = markers.filter((m) =>
          m.state.toLowerCase().includes(input.state!.toLowerCase())
        );
      }
      if (input.city) {
        markers = markers.filter((m) =>
          m.city.toLowerCase().includes(input.city!.toLowerCase())
        );
      }

      return {
        markers,
        generated_at:  cache.generated_at,
        total:         cache.total,
        exposed_count: cache.exposed_count,
        filtered:      markers.length,
      };
    }),

  /** Only exposed markers — shorthand for Strike view */
  exposed: publicProcedure.query(() => {
    const cache = loadCache();
    return {
      markers:       cache.markers.filter((m) => m.is_exposed),
      generated_at:  cache.generated_at,
      exposed_count: cache.exposed_count,
    };
  }),

  /** Refresh the cache by running fetch_geodata.py */
  refresh: publicProcedure
    .input(z.object({ demo: z.boolean().optional().default(true) }))
    .mutation(({ input }) => {
      try {
        const flag   = input.demo ? "--demo" : "";
        const cmd    = `python "${FETCHER_SCRIPT}" ${flag}`.trim();
        const output = execSync(cmd, { encoding: "utf-8", timeout: 60_000 });
        const cache  = loadCache();
        return { success: true, output, total: cache.total, exposed_count: cache.exposed_count };
      } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : String(e);
        return { success: false, output: msg, total: 0, exposed_count: 0 };
      }
    }),
});
