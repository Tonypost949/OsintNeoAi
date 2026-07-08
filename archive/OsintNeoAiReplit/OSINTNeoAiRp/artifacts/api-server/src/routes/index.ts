import { Router, type IRouter } from "express";
import healthRouter from "./health";
import sessionsRouter from "./sessions";
import messagesRouter from "./messages";
import aiRouter from "./ai";

const router: IRouter = Router();

router.use(healthRouter);
router.use(sessionsRouter);
router.use(messagesRouter);
router.use(aiRouter);

export default router;
