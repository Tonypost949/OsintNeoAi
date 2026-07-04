export interface DriveFile {
  id: string;
  name: string;
  mimeType: string;
  webViewLink: string;
  modifiedTime: string;
}

export async function fetchDriveFiles(accessToken: string): Promise<DriveFile[]> {
  // Fetch the 15 most recently modified files that aren't trashed
  const url = 'https://www.googleapis.com/drive/v3/files?pageSize=15&orderBy=modifiedTime desc&fields=files(id,name,mimeType,webViewLink,modifiedTime)&q=trashed=false';
  
  const response = await fetch(url, {
    headers: {
      'Authorization': `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData?.error?.message || `Failed to fetch from Google Drive (${response.status})`);
  }

  const data = await response.json();
  return data.files || [];
}
