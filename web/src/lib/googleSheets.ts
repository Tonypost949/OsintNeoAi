export interface SheetData {
  title: string;
  rows: string[][];
  sheetId: string;
}

export async function fetchGoogleSheet(spreadsheetId: string, accessToken: string): Promise<SheetData> {
  const url = `https://sheets.googleapis.com/v4/spreadsheets/${spreadsheetId}?includeGridData=true`;
  const response = await fetch(url, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData?.error?.message || `Failed to fetch from Google Sheets (${response.status})`);
  }

  const data = await response.json();
  const title = data.properties?.title || 'Untitled Sheet';
  
  let rows: string[][] = [];
  if (data.sheets && data.sheets.length > 0) {
    const firstSheet = data.sheets[0];
    if (firstSheet.data && firstSheet.data.length > 0) {
      const rowData = firstSheet.data[0].rowData;
      if (rowData) {
        rows = rowData.map((row: any) => {
          if (!row.values) return [];
          return row.values.map((cell: any) => cell.formattedValue || '');
        });
      }
    }
  }

  return { title, rows, sheetId: spreadsheetId };
}

// Utility to parse the URL or ID entered by user
export function extractSheetId(input: string): string {
  const trimmed = input.trim();
  if (!trimmed) return '';

  const match = trimmed.match(/\/d\/([a-zA-Z0-9-_]+)/);
  if (match && match[1]) {
    return match[1];
  }

  return trimmed;
}
