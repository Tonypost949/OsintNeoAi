import { Router, type IRouter } from "express";
import { eq, and, sql, desc } from "drizzle-orm";
import { db, sessionsTable, messagesTable } from "@workspace/db";
import { requireAuth } from "../middlewares/auth";
import type { AuthenticatedRequest } from "../middlewares/auth";
import {
  CreateSessionBody,
  GetSessionParams,
  UpdateSessionParams,
  UpdateSessionBody,
  DeleteSessionParams,
  GetSessionResponse,
  ListSessionsResponse,
  CreateSessionResponse,
  UpdateSessionResponse,
  GetStatsResponse,
} from "@workspace/api-zod";

const router: IRouter = Router();

router.get("/sessions", requireAuth, async (req, res): Promise<void> => {
  const userId = (req as AuthenticatedRequest).userId;
  const rows = await db
    .select({
      id: sessionsTable.id,
      title: sessionsTable.title,
      createdAt: sessionsTable.createdAt,
      messageCount: sql<number>`cast(count(${messagesTable.id}) as int)`,
    })
    .from(sessionsTable)
    .leftJoin(messagesTable, eq(messagesTable.sessionId, sessionsTable.id))
    .where(eq(sessionsTable.userId, userId))
    .groupBy(sessionsTable.id)
    .orderBy(desc(sessionsTable.createdAt));

  res.json(ListSessionsResponse.parse(rows));
});

router.post("/sessions", requireAuth, async (req, res): Promise<void> => {
  const userId = (req as AuthenticatedRequest).userId;
  const parsed = CreateSessionBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: parsed.error.message });
    return;
  }

  const [session] = await db
    .insert(sessionsTable)
    .values({ userId, title: parsed.data.title })
    .returning();

  res.status(201).json(
    CreateSessionResponse.parse({ ...session, messageCount: 0 })
  );
});

router.get("/sessions/:id", requireAuth, async (req, res): Promise<void> => {
  const userId = (req as AuthenticatedRequest).userId;
  const params = GetSessionParams.safeParse(req.params);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }

  const [row] = await db
    .select({
      id: sessionsTable.id,
      title: sessionsTable.title,
      createdAt: sessionsTable.createdAt,
      messageCount: sql<number>`cast(count(${messagesTable.id}) as int)`,
    })
    .from(sessionsTable)
    .leftJoin(messagesTable, eq(messagesTable.sessionId, sessionsTable.id))
    .where(and(eq(sessionsTable.id, params.data.id), eq(sessionsTable.userId, userId)))
    .groupBy(sessionsTable.id);

  if (!row) {
    res.status(404).json({ error: "Session not found" });
    return;
  }

  res.json(GetSessionResponse.parse(row));
});

router.patch("/sessions/:id", requireAuth, async (req, res): Promise<void> => {
  const userId = (req as AuthenticatedRequest).userId;
  const params = UpdateSessionParams.safeParse(req.params);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }

  const parsed = UpdateSessionBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: parsed.error.message });
    return;
  }

  const [updated] = await db
    .update(sessionsTable)
    .set({ title: parsed.data.title })
    .where(and(eq(sessionsTable.id, params.data.id), eq(sessionsTable.userId, userId)))
    .returning();

  if (!updated) {
    res.status(404).json({ error: "Session not found" });
    return;
  }

  const [row] = await db
    .select({
      id: sessionsTable.id,
      title: sessionsTable.title,
      createdAt: sessionsTable.createdAt,
      messageCount: sql<number>`cast(count(${messagesTable.id}) as int)`,
    })
    .from(sessionsTable)
    .leftJoin(messagesTable, eq(messagesTable.sessionId, sessionsTable.id))
    .where(and(eq(sessionsTable.id, params.data.id), eq(sessionsTable.userId, userId)))
    .groupBy(sessionsTable.id);

  res.json(UpdateSessionResponse.parse(row));
});

router.delete("/sessions/:id", requireAuth, async (req, res): Promise<void> => {
  const userId = (req as AuthenticatedRequest).userId;
  const params = DeleteSessionParams.safeParse(req.params);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }

  const [deleted] = await db
    .delete(sessionsTable)
    .where(and(eq(sessionsTable.id, params.data.id), eq(sessionsTable.userId, userId)))
    .returning();

  if (!deleted) {
    res.status(404).json({ error: "Session not found" });
    return;
  }

  res.sendStatus(204);
});

router.get("/stats", requireAuth, async (req, res): Promise<void> => {
  const userId = (req as AuthenticatedRequest).userId;
  const [[{ totalSessions }], [{ totalMessages }], recentRows] =
    await Promise.all([
      db
        .select({ totalSessions: sql<number>`cast(count(*) as int)` })
        .from(sessionsTable)
        .where(eq(sessionsTable.userId, userId)),
      db
        .select({ totalMessages: sql<number>`cast(count(*) as int)` })
        .from(messagesTable)
        .where(eq(messagesTable.userId, userId)),
      db
        .select({
          id: sessionsTable.id,
          title: sessionsTable.title,
          createdAt: sessionsTable.createdAt,
          messageCount: sql<number>`cast(count(${messagesTable.id}) as int)`,
        })
        .from(sessionsTable)
        .leftJoin(messagesTable, eq(messagesTable.sessionId, sessionsTable.id))
        .where(eq(sessionsTable.userId, userId))
        .groupBy(sessionsTable.id)
        .orderBy(desc(sessionsTable.createdAt))
        .limit(5),
    ]);

  res.json(
    GetStatsResponse.parse({
      totalSessions,
      totalMessages,
      recentSessions: recentRows,
    })
  );
});

export default router;
