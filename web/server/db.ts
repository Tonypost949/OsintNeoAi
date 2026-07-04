import { eq, and, desc } from "drizzle-orm";
import { drizzle } from "drizzle-orm/mysql2";
import { InsertUser, users, analyses, entities, relationships, files, entityFileAssociations, analysisReports, googleDriveAccounts } from "../drizzle/schema";
import { ENV } from './_core/env';

let _db: ReturnType<typeof drizzle> | null = null;

// Lazily create the drizzle instance so local tooling can run without a DB.
export async function getDb() {
  if (!_db && process.env.DATABASE_URL) {
    try {
      _db = drizzle(process.env.DATABASE_URL);
    } catch (error) {
      console.warn("[Database] Failed to connect:", error);
      _db = null;
    }
  }
  return _db;
}

export async function upsertUser(user: InsertUser): Promise<void> {
  if (!user.openId) {
    throw new Error("User openId is required for upsert");
  }

  const db = await getDb();
  if (!db) {
    console.warn("[Database] Cannot upsert user: database not available");
    return;
  }

  try {
    const values: InsertUser = {
      openId: user.openId,
    };
    const updateSet: Record<string, unknown> = {};

    const textFields = ["name", "email", "loginMethod"] as const;
    type TextField = (typeof textFields)[number];

    const assignNullable = (field: TextField) => {
      const value = user[field];
      if (value === undefined) return;
      const normalized = value ?? null;
      values[field] = normalized;
      updateSet[field] = normalized;
    };

    textFields.forEach(assignNullable);

    if (user.lastSignedIn !== undefined) {
      values.lastSignedIn = user.lastSignedIn;
      updateSet.lastSignedIn = user.lastSignedIn;
    }
    if (user.role !== undefined) {
      values.role = user.role;
      updateSet.role = user.role;
    } else if (user.openId === ENV.ownerOpenId) {
      values.role = 'admin';
      updateSet.role = 'admin';
    }

    if (!values.lastSignedIn) {
      values.lastSignedIn = new Date();
    }

    if (Object.keys(updateSet).length === 0) {
      updateSet.lastSignedIn = new Date();
    }

    await db.insert(users).values(values).onDuplicateKeyUpdate({
      set: updateSet,
    });
  } catch (error) {
    console.error("[Database] Failed to upsert user:", error);
    throw error;
  }
}

export async function getUserByOpenId(openId: string) {
  const db = await getDb();
  if (!db) {
    console.warn("[Database] Cannot get user: database not available");
    return undefined;
  }

  const result = await db.select().from(users).where(eq(users.openId, openId)).limit(1);

  return result.length > 0 ? result[0] : undefined;
}

// Analysis queries
export async function createAnalysis(userId: number, title: string, description?: string) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  const result = await db.insert(analyses).values({
    userId,
    title,
    description,
    status: "processing",
  });
  
  return result;
}

export async function getAnalysisByIdAndUser(analysisId: number, userId: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  const result = await db
    .select()
    .from(analyses)
    .where(and(eq(analyses.id, analysisId), eq(analyses.userId, userId)))
    .limit(1);
  
  return result.length > 0 ? result[0] : null;
}

export async function getUserAnalyses(userId: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  return await db
    .select()
    .from(analyses)
    .where(eq(analyses.userId, userId))
    .orderBy(desc(analyses.createdAt));
}

export async function updateAnalysisStatus(analysisId: number, status: "processing" | "completed" | "failed") {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  return await db
    .update(analyses)
    .set({ status, processingCompletedAt: status !== "processing" ? new Date() : undefined })
    .where(eq(analyses.id, analysisId));
}

export async function updateAnalysisStats(analysisId: number, filesAnalyzed: number, peopleFound: number, relationshipsFound: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  return await db
    .update(analyses)
    .set({ filesAnalyzed, peopleFound, relationshipsFound })
    .where(eq(analyses.id, analysisId));
}

// File queries
export async function createFile(analysisId: number, fileName: string, fileType: string, fileSize: number, s3Key: string, s3Url: string, source: "upload" | "google_drive" = "upload", googleDriveFileId?: string) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  const result = await db.insert(files).values({
    analysisId,
    fileName,
    fileType,
    fileSize,
    s3Key,
    s3Url,
    source,
    googleDriveFileId,
    processingStatus: "pending",
  });
  
  return result;
}

export async function getAnalysisFiles(analysisId: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  return await db.select().from(files).where(eq(files.analysisId, analysisId));
}

export async function updateFileProcessingStatus(fileId: number, status: "pending" | "processing" | "completed" | "failed", errorMessage?: string) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  return await db
    .update(files)
    .set({ processingStatus: status, errorMessage })
    .where(eq(files.id, fileId));
}

// Entity queries
export async function createOrUpdateEntity(analysisId: number, name: string, normalizedName: string, type: "person" | "email" | "phone" = "person") {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  // Check if entity already exists
  const existing = await db
    .select()
    .from(entities)
    .where(and(eq(entities.analysisId, analysisId), eq(entities.normalizedName, normalizedName)))
    .limit(1);
  
  if (existing.length > 0) {
    return existing[0];
  }
  
  await db.insert(entities).values({
    analysisId,
    name,
    normalizedName,
    type,
    fileCount: 1,
  });
  
  // Return the newly created entity
  const created = await db
    .select()
    .from(entities)
    .where(and(eq(entities.analysisId, analysisId), eq(entities.normalizedName, normalizedName)))
    .limit(1);
  
  return created[0];
}

export async function getAnalysisEntities(analysisId: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  return await db.select().from(entities).where(eq(entities.analysisId, analysisId));
}

export async function updateEntityFileCount(entityId: number, increment: number = 1) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  const entity = await db.select().from(entities).where(eq(entities.id, entityId)).limit(1);
  if (entity.length === 0) return;
  
  return await db
    .update(entities)
    .set({ fileCount: entity[0].fileCount + increment })
    .where(eq(entities.id, entityId));
}

// Entity-File association queries
export async function createEntityFileAssociation(entityId: number, fileId: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  // Check if association already exists
  const existing = await db
    .select()
    .from(entityFileAssociations)
    .where(and(eq(entityFileAssociations.entityId, entityId), eq(entityFileAssociations.fileId, fileId)))
    .limit(1);
  
  if (existing.length > 0) {
    // Increment occurrence count
    return await db
      .update(entityFileAssociations)
      .set({ occurrenceCount: existing[0].occurrenceCount + 1 })
      .where(and(eq(entityFileAssociations.entityId, entityId), eq(entityFileAssociations.fileId, fileId)));
  }
  
  return await db.insert(entityFileAssociations).values({
    entityId,
    fileId,
    occurrenceCount: 1,
  });
}

// Relationship queries
export async function createOrUpdateRelationship(analysisId: number, entity1Id: number, entity2Id: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  // Ensure consistent ordering (smaller ID first)
  const [minId, maxId] = entity1Id < entity2Id ? [entity1Id, entity2Id] : [entity2Id, entity1Id];
  
  // Check if relationship already exists
  const existing = await db
    .select()
    .from(relationships)
    .where(and(
      eq(relationships.analysisId, analysisId),
      eq(relationships.entity1Id, minId),
      eq(relationships.entity2Id, maxId)
    ))
    .limit(1);
  
  if (existing.length > 0) {
    // Increment co-occurrence count
    const newCount = existing[0].coOccurrenceCount + 1;
      return await db
      .update(relationships)
      .set({ 
        coOccurrenceCount: newCount,
        strength: String(Math.min(newCount * 0.5, 10)), // Calculate strength metric
        lastSeenAt: new Date()
      })
      .where(eq(relationships.id, existing[0].id));
  }
  
  return await db.insert(relationships).values({
    analysisId,
    entity1Id: minId,
    entity2Id: maxId,
    coOccurrenceCount: 1,
    strength: "0.5",
  });
}

export async function getAnalysisRelationships(analysisId: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  return await db.select().from(relationships).where(eq(relationships.analysisId, analysisId));
}

// Analysis report queries
export async function saveAnalysisReport(analysisId: number, textReport: string, csvPeopleUrl?: string, csvRelationshipsUrl?: string, networkGraphUrl?: string) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  const existing = await db
    .select()
    .from(analysisReports)
    .where(eq(analysisReports.analysisId, analysisId))
    .limit(1);
  
  if (existing.length > 0) {
    return await db
      .update(analysisReports)
      .set({ textReport, csvPeopleUrl, csvRelationshipsUrl, networkGraphUrl })
      .where(eq(analysisReports.analysisId, analysisId));
  }
  
  return await db.insert(analysisReports).values({
    analysisId,
    textReport,
    csvPeopleUrl,
    csvRelationshipsUrl,
    networkGraphUrl,
  });
}

export async function getAnalysisReport(analysisId: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  const result = await db
    .select()
    .from(analysisReports)
    .where(eq(analysisReports.analysisId, analysisId))
    .limit(1);
  
  return result.length > 0 ? result[0] : null;
}

// Google Drive account queries
export async function saveGoogleDriveAccount(userId: number, email: string, accessToken: string, refreshToken?: string, tokenExpiresAt?: Date) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  return await db.insert(googleDriveAccounts).values({
    userId,
    email,
    accessToken,
    refreshToken,
    tokenExpiresAt,
    isActive: true,
  });
}

export async function getUserGoogleDriveAccounts(userId: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  return await db
    .select()
    .from(googleDriveAccounts)
    .where(and(eq(googleDriveAccounts.userId, userId), eq(googleDriveAccounts.isActive, true)));
}

export async function getGoogleDriveAccount(accountId: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  const result = await db
    .select()
    .from(googleDriveAccounts)
    .where(eq(googleDriveAccounts.id, accountId))
    .limit(1);
  
  return result.length > 0 ? result[0] : null;
}

export async function updateGoogleDriveAccount(accountId: number, accessToken: string, refreshToken?: string, tokenExpiresAt?: Date) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  return await db
    .update(googleDriveAccounts)
    .set({ accessToken, refreshToken, tokenExpiresAt })
    .where(eq(googleDriveAccounts.id, accountId));
}

export async function deactivateGoogleDriveAccount(accountId: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  return await db
    .update(googleDriveAccounts)
    .set({ isActive: false })
    .where(eq(googleDriveAccounts.id, accountId));
}
