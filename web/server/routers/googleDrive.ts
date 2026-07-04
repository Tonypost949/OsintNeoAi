import { protectedProcedure, router } from "../_core/trpc";
import { z } from "zod";
import * as db from "../db";
import * as googleDrive from "../googleDrive";

export const googleDriveRouter = router({
  // Get authorization URL
  getAuthUrl: protectedProcedure.query(({ ctx }) => {
    // In production, these would come from environment variables
    const clientId = process.env.GOOGLE_DRIVE_CLIENT_ID || "";
    const clientSecret = process.env.GOOGLE_DRIVE_CLIENT_SECRET || "";
    const redirectUrl = process.env.GOOGLE_DRIVE_REDIRECT_URL || "http://localhost:3000/auth/google/callback";

    const oauth2Client = googleDrive.createOAuth2Client(clientId, clientSecret, redirectUrl);
    const authUrl = googleDrive.getAuthorizationUrl(oauth2Client);

    return { authUrl };
  }),

  // Exchange code for tokens and save account
  connectAccount: protectedProcedure
    .input(z.object({
      code: z.string(),
      email: z.string().email(),
    }))
    .mutation(async ({ input, ctx }) => {
      try {
        const clientId = process.env.GOOGLE_DRIVE_CLIENT_ID || "";
        const clientSecret = process.env.GOOGLE_DRIVE_CLIENT_SECRET || "";
        const redirectUrl = process.env.GOOGLE_DRIVE_REDIRECT_URL || "http://localhost:3000/auth/google/callback";

        const oauth2Client = googleDrive.createOAuth2Client(clientId, clientSecret, redirectUrl);
        const tokens = await googleDrive.getTokensFromCode(oauth2Client, input.code);

        // Save account to database
        await db.saveGoogleDriveAccount(
          ctx.user.id,
          input.email,
          tokens.access_token,
          tokens.refresh_token,
          tokens.expiry_date ? new Date(tokens.expiry_date) : undefined
        );

        return { success: true, message: "Google Drive account connected" };
      } catch (error) {
        console.error("Error connecting Google Drive account:", error);
        throw new Error("Failed to connect Google Drive account");
      }
    }),

  // List connected accounts
  listAccounts: protectedProcedure.query(async ({ ctx }) => {
    return await db.getUserGoogleDriveAccounts(ctx.user.id);
  }),

  // Disconnect account
  disconnectAccount: protectedProcedure
    .input(z.object({ accountId: z.number() }))
    .mutation(async ({ input, ctx }) => {
      try {
        await db.deactivateGoogleDriveAccount(input.accountId);
        return { success: true };
      } catch (error) {
        throw new Error("Failed to disconnect account");
      }
    }),

  // Scan Drive and add files to analysis
  scanAndAddFiles: protectedProcedure
    .input(z.object({
      accountId: z.number(),
      analysisId: z.number(),
      maxFiles: z.number().default(200),
    }))
    .mutation(async ({ input, ctx }) => {
      try {
        // Verify analysis belongs to user
        const analysis = await db.getAnalysisByIdAndUser(input.analysisId, ctx.user.id);
        if (!analysis) throw new Error("Analysis not found");

        // Scan Drive and add files
        const result = await googleDrive.scanDriveAndAddFiles(
          ctx.user.id,
          input.accountId,
          input.analysisId,
          input.maxFiles
        );

        return result;
      } catch (error) {
        console.error("Error scanning Drive:", error);
        throw new Error("Failed to scan Google Drive");
      }
    }),

  // List files from Drive (preview)
  listFiles: protectedProcedure
    .input(z.object({
      accountId: z.number(),
      maxFiles: z.number().default(50),
    }))
    .query(async ({ input, ctx }) => {
      try {
        const account = await db.getGoogleDriveAccount(input.accountId);
        if (!account) throw new Error("Account not found");

        const files = await googleDrive.listDriveFiles(account.accessToken, input.maxFiles);
        return files;
      } catch (error) {
        console.error("Error listing Drive files:", error);
        throw new Error("Failed to list files");
      }
    }),
});
