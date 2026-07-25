import { COOKIE_NAME } from "@shared/const";
import { getSessionCookieOptions } from "./_core/cookies";
import { systemRouter } from "./_core/systemRouter";
import { publicProcedure, router, protectedProcedure } from "./_core/trpc";
import { z } from "zod";
import * as db from "./db";
import { extractEntities, findCoOccurrences } from "./extraction";
import { storagePut } from "./storage";
import { nanoid } from "nanoid";
import { googleDriveRouter } from "./routers/googleDrive";
import { markersRouter } from "./routers/markers";

export const appRouter = router({
  system: systemRouter,
  googleDrive: googleDriveRouter,
  markers: markersRouter,
  auth: router({
    me: publicProcedure.query(opts => opts.ctx.user),
    logout: publicProcedure.mutation(({ ctx }) => {
      const cookieOptions = getSessionCookieOptions(ctx.req);
      ctx.res.clearCookie(COOKIE_NAME, { ...cookieOptions, maxAge: -1 });
      return {
        success: true,
      } as const;
    }),
  }),

  // Analysis procedures
  analysis: router({
    // Create a new analysis session
    create: protectedProcedure
      .input(z.object({
        title: z.string().min(1).max(255),
        description: z.string().optional(),
      }))
      .mutation(async ({ input, ctx }) => {
        const result = await db.createAnalysis(ctx.user.id, input.title, input.description);
        return { success: true, analysisId: (result as any).insertId || 0 };
      }),

    // Get user's analysis sessions
    list: protectedProcedure
      .query(async ({ ctx }) => {
        return await db.getUserAnalyses(ctx.user.id);
      }),

    // Get specific analysis details
    get: protectedProcedure
      .input(z.object({ analysisId: z.number() }))
      .query(async ({ input, ctx }) => {
        const analysis = await db.getAnalysisByIdAndUser(input.analysisId, ctx.user.id);
        if (!analysis) throw new Error("Analysis not found");
        
        const entities = await db.getAnalysisEntities(input.analysisId);
        const relationships = await db.getAnalysisRelationships(input.analysisId);
        const report = await db.getAnalysisReport(input.analysisId);
        
        return {
          analysis,
          entities,
          relationships,
          report,
        };
      }),

    // Delete analysis
    delete: protectedProcedure
      .input(z.object({ analysisId: z.number() }))
      .mutation(async ({ input, ctx }) => {
        const analysis = await db.getAnalysisByIdAndUser(input.analysisId, ctx.user.id);
        if (!analysis) throw new Error("Analysis not found");
        
        // TODO: Implement deletion logic
        return { success: true };
      }),
  }),

  // File upload procedures
  file: router({
    // Upload file for analysis
    upload: protectedProcedure
      .input(z.object({
        analysisId: z.number(),
        fileName: z.string(),
        fileType: z.enum(["txt", "pdf", "docx", "csv", "json", "eml"]),
        fileSize: z.number(),
        fileContent: z.string(), // Base64 encoded content
      }))
      .mutation(async ({ input, ctx }) => {
        // Verify analysis belongs to user
        const analysis = await db.getAnalysisByIdAndUser(input.analysisId, ctx.user.id);
        if (!analysis) throw new Error("Analysis not found");

        try {
          // Upload to S3
          const fileKey = `analyses/${input.analysisId}/${nanoid()}/${input.fileName}`;
          const buffer = Buffer.from(input.fileContent, "base64");
          
          const { url } = await storagePut(fileKey, buffer, "application/octet-stream");

          // Create file record
          const fileResult = await db.createFile(
            input.analysisId,
            input.fileName,
            input.fileType,
            input.fileSize,
            fileKey,
            url,
            "upload"
          );

          return {
            success: true,
            fileId: (fileResult as any).insertId || 0,
            url,
          };
        } catch (error) {
          console.error("File upload error:", error);
          throw new Error("Failed to upload file");
        }
      }),

    // Get analysis files
    list: protectedProcedure
      .input(z.object({ analysisId: z.number() }))
      .query(async ({ input, ctx }) => {
        const analysis = await db.getAnalysisByIdAndUser(input.analysisId, ctx.user.id);
        if (!analysis) throw new Error("Analysis not found");
        
        return await db.getAnalysisFiles(input.analysisId);
      }),
  }),

  // Entity extraction and analysis procedures
  extraction: router({
    // Process a file and extract entities
    processFile: protectedProcedure
      .input(z.object({
        analysisId: z.number(),
        fileId: z.number(),
        fileContent: z.string(),
        fileType: z.string(),
      }))
      .mutation(async ({ input, ctx }) => {
        // Verify analysis belongs to user
        const analysis = await db.getAnalysisByIdAndUser(input.analysisId, ctx.user.id);
        if (!analysis) throw new Error("Analysis not found");

        try {
          // Update file status to processing
          await db.updateFileProcessingStatus(input.fileId, "processing");

          // Extract entities from file
          const extractionResult = extractEntities(input.fileContent);
          
          // Store entities in database
          const entityMap = new Map<string, number>();
          
          for (const entity of extractionResult.allEntities) {
            // Create or get entity
            const result = await db.createOrUpdateEntity(
              input.analysisId,
              entity.name,
              entity.normalizedName,
              entity.type
            );
            
            // Get the entity ID
            const entityId = result.id;
            if (entityId) {
              entityMap.set(entity.normalizedName, entityId);
            }
            
            // Create file association
            await db.createEntityFileAssociation(entityId, input.fileId);
          }

          // Find and store relationships (co-occurrences)
          const pairs = findCoOccurrences(extractionResult.allEntities);
          for (const [entity1, entity2] of pairs) {
            const id1 = entityMap.get(entity1.normalizedName);
            const id2 = entityMap.get(entity2.normalizedName);
            
            if (id1 && id2 && id1 !== id2) {
              await db.createOrUpdateRelationship(input.analysisId, id1, id2);
            }
          }

          // Update file status to completed
          await db.updateFileProcessingStatus(input.fileId, "completed");
          
          // Update file entity count
          // TODO: Update entity count in files table

          return {
            success: true,
            entitiesExtracted: extractionResult.allEntities.length,
            peopleFound: extractionResult.people.length,
            emailsFound: extractionResult.emails.length,
            phonesFound: extractionResult.phones.length,
          };
        } catch (error) {
          console.error("File processing error:", error);
          await db.updateFileProcessingStatus(input.fileId, "failed", String(error));
          throw new Error("Failed to process file");
        }
      }),

    // Get entities for analysis
    getEntities: protectedProcedure
      .input(z.object({ analysisId: z.number() }))
      .query(async ({ input, ctx }) => {
        const analysis = await db.getAnalysisByIdAndUser(input.analysisId, ctx.user.id);
        if (!analysis) throw new Error("Analysis not found");
        
        return await db.getAnalysisEntities(input.analysisId);
      }),

    // Get relationships for analysis
    getRelationships: protectedProcedure
      .input(z.object({ analysisId: z.number() }))
      .query(async ({ input, ctx }) => {
        const analysis = await db.getAnalysisByIdAndUser(input.analysisId, ctx.user.id);
        if (!analysis) throw new Error("Analysis not found");
        
        return await db.getAnalysisRelationships(input.analysisId);
      }),
  }),

  // Report generation procedures
  report: router({
    // Generate and save analysis report
    generate: protectedProcedure
      .input(z.object({ analysisId: z.number() }))
      .mutation(async ({ input, ctx }) => {
        const analysis = await db.getAnalysisByIdAndUser(input.analysisId, ctx.user.id);
        if (!analysis) throw new Error("Analysis not found");

        try {
          // Get all data for report
          const entities = await db.getAnalysisEntities(input.analysisId);
          const relationships = await db.getAnalysisRelationships(input.analysisId);
          const files = await db.getAnalysisFiles(input.analysisId);

          // Generate text report
          const textReport = generateTextReport(analysis, entities, relationships);

          // Generate CSV exports
          const csvPeople = generatePeopleCSV(entities, relationships);
          const csvRelationships = generateRelationshipsCSV(relationships);

          // Upload CSVs to S3
          const csvPeopleKey = `analyses/${input.analysisId}/people-${nanoid()}.csv`;
          const csvRelationshipsKey = `analyses/${input.analysisId}/relationships-${nanoid()}.csv`;

          const { url: csvPeopleUrl } = await storagePut(csvPeopleKey, csvPeople, "text/csv");
          const { url: csvRelationshipsUrl } = await storagePut(csvRelationshipsKey, csvRelationships, "text/csv");

          // Save report to database
          await db.saveAnalysisReport(
            input.analysisId,
            textReport,
            csvPeopleUrl,
            csvRelationshipsUrl
          );

          return {
            success: true,
            textReport,
            csvPeopleUrl,
            csvRelationshipsUrl,
          };
        } catch (error) {
          console.error("Report generation error:", error);
          throw new Error("Failed to generate report");
        }
      }),

    // Get saved report
    get: protectedProcedure
      .input(z.object({ analysisId: z.number() }))
      .query(async ({ input, ctx }) => {
        const analysis = await db.getAnalysisByIdAndUser(input.analysisId, ctx.user.id);
        if (!analysis) throw new Error("Analysis not found");
        
        return await db.getAnalysisReport(input.analysisId);
      }),
  }),
});

// Helper functions for report generation
function generateTextReport(analysis: any, entities: any[], relationships: any[]): string {
  const lines: string[] = [];
  
  lines.push("=".repeat(80));
  lines.push("OSINT ANALYSIS REPORT");
  lines.push(`Generated: ${new Date().toISOString()}`);
  lines.push("=".repeat(80));
  lines.push("");
  
  // Summary statistics
  lines.push("SUMMARY STATISTICS");
  lines.push("-".repeat(40));
  lines.push(`Analysis: ${analysis.title}`);
  lines.push(`Total People Identified: ${entities.filter((e: any) => e.type === "person").length}`);
  lines.push(`Total Emails: ${entities.filter((e: any) => e.type === "email").length}`);
  lines.push(`Total Phones: ${entities.filter((e: any) => e.type === "phone").length}`);
  lines.push(`Total Relationships: ${relationships.length}`);
  lines.push("");
  
  // Top connected individuals
  lines.push("TOP CONNECTED INDIVIDUALS");
  lines.push("-".repeat(40));
  
  const sortedEntities = entities
    .filter((e: any) => e.type === "person")
    .sort((a: any, b: any) => b.connectionCount - a.connectionCount)
    .slice(0, 20);
  
  sortedEntities.forEach((entity: any, index: number) => {
    lines.push(`${index + 1}. ${entity.name}`);
    lines.push(`   Files: ${entity.fileCount}`);
    lines.push(`   Connections: ${entity.connectionCount}`);
    if (entity.emails && entity.emails.length > 0) {
      lines.push(`   Emails: ${entity.emails.join(", ")}`);
    }
    if (entity.phones && entity.phones.length > 0) {
      lines.push(`   Phones: ${entity.phones.join(", ")}`);
    }
    lines.push("");
  });
  
  return lines.join("\n");
}

function generatePeopleCSV(entities: any[], relationships: any[]): string {
  const lines: string[] = [];
  
  // Header
  lines.push("Name,Type,File_Count,Connection_Count,Emails,Phones");
  
  // Data rows
  entities.forEach((entity: any) => {
    const emails = entity.emails ? entity.emails.join(";") : "";
    const phones = entity.phones ? entity.phones.join(";") : "";
    lines.push(`"${entity.name}","${entity.type}",${entity.fileCount},${entity.connectionCount},"${emails}","${phones}"`);
  });
  
  return lines.join("\n");
}

function generateRelationshipsCSV(relationships: any[]): string {
  const lines: string[] = [];
  
  // Header
  lines.push("Entity1_ID,Entity2_ID,Co_Occurrence_Count,Strength");
  
  // Data rows
  relationships.forEach((rel: any) => {
    lines.push(`${rel.entity1Id},${rel.entity2Id},${rel.coOccurrenceCount},${rel.strength}`);
  });
  
  return lines.join("\n");
}

export type AppRouter = typeof appRouter;
