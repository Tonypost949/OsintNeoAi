import { Router, type IRouter } from "express";
import { eq, and, asc } from "drizzle-orm";
import { db, messagesTable, sessionsTable } from "@workspace/db";
import { requireAuth } from "../middlewares/auth";
import type { AuthenticatedRequest } from "../middlewares/auth";
import {
  ListMessagesParams,
  ListMessagesResponse,
  CreateMessageParams,
  CreateMessageBody,
  CreateMessageResponse,
} from "@workspace/api-zod";

const router: IRouter = Router();

router.get("/sessions/:id/messages", requireAuth, async (req, res): Promise<void> => {
  const userId = (req as AuthenticatedRequest).userId;
  const params = ListMessagesParams.safeParse(req.params);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }

  const [session] = await db
    .select()
    .from(sessionsTable)
    .where(and(eq(sessionsTable.id, params.data.id), eq(sessionsTable.userId, userId)));

  if (!session) {
    res.status(404).json({ error: "Session not found" });
    return;
  }

  const rows = await db
    .select()
    .from(messagesTable)
    .where(eq(messagesTable.sessionId, params.data.id))
    .orderBy(asc(messagesTable.createdAt));

  res.json(ListMessagesResponse.parse(rows));
});

router.post("/sessions/:id/messages", requireAuth, async (req, res): Promise<void> => {
  const userId = (req as AuthenticatedRequest).userId;
  const params = CreateMessageParams.safeParse(req.params);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }

  const parsed = CreateMessageBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: parsed.error.message });
    return;
  }

  const [session] = await db
    .select()
    .from(sessionsTable)
    .where(and(eq(sessionsTable.id, params.data.id), eq(sessionsTable.userId, userId)));

  if (!session) {
    res.status(404).json({ error: "Session not found" });
    return;
  }

  const [message] = await db
    .insert(messagesTable)
    .values({
      sessionId: params.data.id,
      userId,
      role: parsed.data.role,
      content: parsed.data.content,
    })
    .returning();

  res.status(201).json(CreateMessageResponse.parse(message));
});

export default router;
