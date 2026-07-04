export interface EmailMessage {
  id: string;
  snippet: string;
  subject: string;
  from: string;
  date: string;
}

export async function fetchRecentEmails(accessToken: string): Promise<EmailMessage[]> {
  const listUrl = 'https://gmail.googleapis.com/gmail/v1/users/me/messages?maxResults=15&q=-in:chats';
  const listResponse = await fetch(listUrl, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!listResponse.ok) {
    const errorData = await listResponse.json().catch(() => ({}));
    throw new Error(errorData?.error?.message || `Failed to fetch from Gmail (${listResponse.status})`);
  }

  const listData = await listResponse.json();
  const messages = listData.messages || [];

  const emails: EmailMessage[] = [];

  for (const msg of messages) {
    const msgUrl = `https://gmail.googleapis.com/gmail/v1/users/me/messages/${msg.id}?format=metadata&metadataHeaders=Subject&metadataHeaders=From&metadataHeaders=Date`;
    const msgResponse = await fetch(msgUrl, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });

    if (msgResponse.ok) {
      const msgData = await msgResponse.json();
      const headers = msgData.payload?.headers || [];
      
      let subject = 'No Subject';
      let from = 'Unknown Sender';
      let date = '';

      headers.forEach((h: any) => {
        if (h.name.toLowerCase() === 'subject') subject = h.value;
        if (h.name.toLowerCase() === 'from') from = h.value;
        if (h.name.toLowerCase() === 'date') date = h.value;
      });

      emails.push({
        id: msg.id,
        snippet: msgData.snippet || '',
        subject,
        from,
        date
      });
    }
  }

  return emails;
}
