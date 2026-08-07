import { pgTable, text, serial, numeric, timestamp } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

export const locations = pgTable("locations", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  description: text("description").notNull(),
  longitude: numeric("longitude").notNull(),
  latitude: numeric("latitude").notNull(),
  type: text("type").notNull(), // 'well', 'anomaly', 'other'
  severity: text("severity").notNull(), // 'critical', 'high', 'warning'
  createdAt: timestamp("created_at").defaultNow(),
});

export const insertLocationSchema = createInsertSchema(locations).omit({ id: true, createdAt: true });

export type Location = typeof locations.$inferSelect;
export type InsertLocation = z.infer<typeof insertLocationSchema>;
export type LocationResponse = Location;
