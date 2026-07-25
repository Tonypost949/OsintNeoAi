/**
 * Google Drive integration utilities
 * Handles OAuth authentication and file scanning
 */

import { google } from "googleapis";
import * as db from "./db";

const SCOPES = ["https://www.googleapis.com/auth/drive.readonly"];
const SUPPORTED_MIME_TYPES = [
  "text/plain",
  "application/pdf",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "text/csv",
  "application/json",
  "message/rfc822",
];

export interface GoogleDriveFile {
  id: string;
  name: string;
  mimeType: string;
  size?: string | number | null;
  modifiedTime?: string | null;
}

/**
 * Create OAuth2 client for Google Drive API
 */
export function createOAuth2Client(clientId: string, clientSecret: string, redirectUrl: string) {
  return new google.auth.OAuth2(clientId, clientSecret, redirectUrl);
}

/**
 * Get authorization URL for user to grant access
 */
export function getAuthorizationUrl(oauth2Client: any): string {
  return oauth2Client.generateAuthUrl({
    access_type: "offline",
    scope: SCOPES,
  });
}

/**
 * Exchange authorization code for tokens
 */
export async function getTokensFromCode(oauth2Client: any, code: string): Promise<any> {
  const { tokens } = await oauth2Client.getToken(code);
  return tokens;
}

/**
 * List files from Google Drive
 */
export async function listDriveFiles(
  accessToken: string,
  pageSize: number = 100
): Promise<GoogleDriveFile[]> {
  try {
    const auth = new google.auth.OAuth2();
    auth.setCredentials({ access_token: accessToken });

    const drive = google.drive({ version: "v3", auth });

    const query = SUPPORTED_MIME_TYPES.map((mime) => `mimeType='${mime}'`).join(" or ");

    const response = await drive.files.list({
      q: query,
      spaces: "drive",
      fields: "files(id, name, mimeType, size, modifiedTime)",
      pageSize,
    });

    return ((response.data.files || []) as any[]).map((file) => ({
      id: file.id,
      name: file.name,
      mimeType: file.mimeType,
      size: file.size ? (typeof file.size === 'string' ? parseInt(file.size) : file.size) : 0,
      modifiedTime: file.modifiedTime,
    }));
  } catch (error) {
    console.error("Error listing Drive files:", error);
    throw error;
  }
}

/**
 * Download file content from Google Drive
 */
export async function downloadDriveFile(accessToken: string, fileId: string): Promise<Buffer> {
  try {
    const auth = new google.auth.OAuth2();
    auth.setCredentials({ access_token: accessToken });

    const drive = google.drive({ version: "v3", auth });

    const response = await drive.files.get(
      { fileId, alt: "media" },
      { responseType: "stream" }
    );

    return new Promise((resolve, reject) => {
      const chunks: Buffer[] = [];
      response.data.on("data", (chunk: Buffer) => {
        chunks.push(chunk);
      });
      response.data.on("end", () => {
        resolve(Buffer.concat(chunks));
      });
      response.data.on("error", reject);
    });
  } catch (error) {
    console.error("Error downloading Drive file:", error);
    throw error;
  }
}

/**
 * Get MIME type extension mapping
 */
export function getMimeTypeExtension(mimeType: string): string {
  const mimeMap: Record<string, string> = {
    "text/plain": "txt",
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "text/csv": "csv",
    "application/json": "json",
    "message/rfc822": "eml",
  };

  return mimeMap[mimeType] || "txt";
}

/**
 * Scan Google Drive and add files to analysis
 */
export async function scanDriveAndAddFiles(
  userId: number,
  accountId: number,
  analysisId: number,
  maxFiles: number = 200
): Promise<{ filesAdded: number; errors: string[] }> {
  try {
    const account = await db.getGoogleDriveAccount(accountId);
    if (!account) {
      throw new Error("Google Drive account not found");
    }

    // List files from Drive
    const driveFiles = await listDriveFiles(account.accessToken, maxFiles);

    let filesAdded = 0;
    const errors: string[] = [];

    // Add each file to analysis
    for (const driveFile of driveFiles) {
      try {
        // Download file content
        const fileContent = await downloadDriveFile(account.accessToken, driveFile.id);

        // Get file extension
        const extension = getMimeTypeExtension(driveFile.mimeType);

        // Create file record in database
        const fileSize = typeof driveFile.size === 'string' ? parseInt(driveFile.size) : (driveFile.size || 0);
        const fileResult = await db.createFile(
          analysisId,
          driveFile.name,
          extension as any,
          fileSize,
          `drive/${driveFile.id}`,
          "", // URL will be empty for Drive files
          "google_drive",
          driveFile.id
        );

        filesAdded++;
      } catch (error) {
        errors.push(`Failed to add ${driveFile.name}: ${String(error)}`);
      }
    }

    return { filesAdded, errors };
  } catch (error) {
    console.error("Error scanning Google Drive:", error);
    throw error;
  }
}
