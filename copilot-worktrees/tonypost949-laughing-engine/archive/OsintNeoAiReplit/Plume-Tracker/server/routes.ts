import type { Express } from "express";
import type { Server } from "http";
import { storage } from "./storage";
import { api } from "@shared/routes";
import { z } from "zod";

async function seedDatabase() {
  const existing = await storage.getLocations();
  if (existing.length === 0) {
    await storage.createLocation({
      name: "Well No. 5403 (Chimney Effect)",
      description: "1947 Survey Location - 49x Safety Limit for Cr(VI)",
      longitude: "-118.0012",
      latitude: "33.6841",
      type: "well",
      severity: "critical",
    });
    await storage.createLocation({
      name: "Subsurface Anomaly Point A",
      description: "Vapor Intrusion identified in Case No. 20IC002 Omission",
      longitude: "-117.9892",
      latitude: "33.6765",
      type: "anomaly",
      severity: "high",
    });
  }
}

export async function registerRoutes(
  httpServer: Server,
  app: Express
): Promise<Server> {
  // Seed the database
  await seedDatabase().catch(console.error);

  app.get(api.locations.list.path, async (req, res) => {
    const locs = await storage.getLocations();
    res.json(locs);
  });

  app.post(api.locations.create.path, async (req, res) => {
    try {
      const input = api.locations.create.input.parse(req.body);
      const loc = await storage.createLocation(input);
      res.status(201).json(loc);
    } catch (err) {
      if (err instanceof z.ZodError) {
        return res.status(400).json({
          message: err.errors[0].message,
          field: err.errors[0].path.join('.'),
        });
      }
      throw err;
    }
  });

  return httpServer;
}
