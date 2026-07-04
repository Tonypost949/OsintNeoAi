import { int, mysqlEnum, mysqlTable, text, timestamp, varchar, json, decimal, boolean } from "drizzle-orm/mysql-core";

/**
 * Core user table backing auth flow.
 * Extend this file with additional tables as your product grows.
 * Columns use camelCase to match both database fields and generated types.
 */
export const users = mysqlTable("users", {
  /**
   * Surrogate primary key. Auto-incremented numeric value managed by the database.
   * Use this for relations between tables.
   */
  id: int("id").autoincrement().primaryKey(),
  /** Manus OAuth identifier (openId) returned from the OAuth callback. Unique per user. */
  openId: varchar("openId", { length: 64 }).notNull().unique(),
  name: text("name"),
  email: varchar("email", { length: 320 }),
  loginMethod: varchar("loginMethod", { length: 64 }),
  role: mysqlEnum("role", ["user", "admin"]).default("user").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  lastSignedIn: timestamp("lastSignedIn").defaultNow().notNull(),
});

export type User = typeof users.$inferSelect;
export type InsertUser = typeof users.$inferInsert;

/**
 * Analysis sessions - represents a complete OSINT analysis run
 */
export const analyses = mysqlTable("analyses", {
  id: int("id").autoincrement().primaryKey(),
  userId: int("userId").notNull(),
  title: varchar("title", { length: 255 }).notNull(),
  description: text("description"),
  status: mysqlEnum("status", ["processing", "completed", "failed"]).default("processing").notNull(),
  filesAnalyzed: int("filesAnalyzed").default(0).notNull(),
  peopleFound: int("peopleFound").default(0).notNull(),
  relationshipsFound: int("relationshipsFound").default(0).notNull(),
  processingStartedAt: timestamp("processingStartedAt").defaultNow().notNull(),
  processingCompletedAt: timestamp("processingCompletedAt"),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

export type Analysis = typeof analyses.$inferSelect;
export type InsertAnalysis = typeof analyses.$inferInsert;

/**
 * Files uploaded or scanned from Google Drive
 */
export const files = mysqlTable("files", {
  id: int("id").autoincrement().primaryKey(),
  analysisId: int("analysisId").notNull(),
  fileName: varchar("fileName", { length: 512 }).notNull(),
  fileType: varchar("fileType", { length: 50 }).notNull(), // txt, pdf, docx, csv, json, eml
  fileSize: int("fileSize").notNull(),
  s3Key: varchar("s3Key", { length: 512 }).notNull(),
  s3Url: text("s3Url").notNull(),
  source: mysqlEnum("source", ["upload", "google_drive"]).default("upload").notNull(),
  googleDriveFileId: varchar("googleDriveFileId", { length: 255 }),
  entitiesExtracted: int("entitiesExtracted").default(0).notNull(),
  processingStatus: mysqlEnum("processingStatus", ["pending", "processing", "completed", "failed"]).default("pending").notNull(),
  errorMessage: text("errorMessage"),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

export type File = typeof files.$inferSelect;
export type InsertFile = typeof files.$inferInsert;

/**
 * Extracted entities (people) from documents
 */
export const entities = mysqlTable("entities", {
  id: int("id").autoincrement().primaryKey(),
  analysisId: int("analysisId").notNull(),
  name: varchar("name", { length: 255 }).notNull(),
  type: mysqlEnum("type", ["person", "email", "phone"]).default("person").notNull(),
  normalizedName: varchar("normalizedName", { length: 255 }).notNull(), // for deduplication
  fileCount: int("fileCount").default(1).notNull(),
  connectionCount: int("connectionCount").default(0).notNull(),
  emails: json("emails").$type<string[]>(), // array of associated emails
  phones: json("phones").$type<string[]>(), // array of associated phones
  firstSeenAt: timestamp("firstSeenAt").defaultNow().notNull(),
  lastSeenAt: timestamp("lastSeenAt").defaultNow().notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

export type Entity = typeof entities.$inferSelect;
export type InsertEntity = typeof entities.$inferInsert;

/**
 * Entity-File associations tracking which files contain which entities
 */
export const entityFileAssociations = mysqlTable("entityFileAssociations", {
  id: int("id").autoincrement().primaryKey(),
  entityId: int("entityId").notNull(),
  fileId: int("fileId").notNull(),
  occurrenceCount: int("occurrenceCount").default(1).notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export type EntityFileAssociation = typeof entityFileAssociations.$inferSelect;
export type InsertEntityFileAssociation = typeof entityFileAssociations.$inferInsert;

/**
 * Relationships between entities (co-occurrences)
 */
export const relationships = mysqlTable("relationships", {
  id: int("id").autoincrement().primaryKey(),
  analysisId: int("analysisId").notNull(),
  entity1Id: int("entity1Id").notNull(),
  entity2Id: int("entity2Id").notNull(),
  coOccurrenceCount: int("coOccurrenceCount").default(1).notNull(),
  strength: decimal("strength", { precision: 5, scale: 2 }).default("1.0"), // calculated strength metric
  firstSeenAt: timestamp("firstSeenAt").defaultNow().notNull(),
  lastSeenAt: timestamp("lastSeenAt").defaultNow().notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

export type Relationship = typeof relationships.$inferSelect;
export type InsertRelationship = typeof relationships.$inferInsert;

/**
 * Google Drive accounts connected by users
 */
export const googleDriveAccounts = mysqlTable("googleDriveAccounts", {
  id: int("id").autoincrement().primaryKey(),
  userId: int("userId").notNull(),
  email: varchar("email", { length: 320 }).notNull(),
  accessToken: text("accessToken").notNull(),
  refreshToken: text("refreshToken"),
  tokenExpiresAt: timestamp("tokenExpiresAt"),
  isActive: boolean("isActive").default(true).notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

export type GoogleDriveAccount = typeof googleDriveAccounts.$inferSelect;
export type InsertGoogleDriveAccount = typeof googleDriveAccounts.$inferInsert;

/**
 * Analysis reports (cached text reports for quick retrieval)
 */
export const analysisReports = mysqlTable("analysisReports", {
  id: int("id").autoincrement().primaryKey(),
  analysisId: int("analysisId").notNull().unique(),
  textReport: text("textReport").notNull(),
  csvPeopleUrl: varchar("csvPeopleUrl", { length: 512 }),
  csvRelationshipsUrl: varchar("csvRelationshipsUrl", { length: 512 }),
  networkGraphUrl: varchar("networkGraphUrl", { length: 512 }),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

export type AnalysisReport = typeof analysisReports.$inferSelect;
export type InsertAnalysisReport = typeof analysisReports.$inferInsert;
