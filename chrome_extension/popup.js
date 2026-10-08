document.getElementById('captureBtn').addEventListener('click', async () => {
    const statusDiv = document.getElementById('status');
    statusDiv.style.display = 'block';
    statusDiv.style.color = '#38bdf8';
    statusDiv.innerText = "Scraping page & hashing...";

    let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => { return document.body.innerText.substring(0, 5000); }
    }, async (results) => {
        if (!results || !results[0] || !results[0].result) {
            statusDiv.style.color = '#ef4444';
            statusDiv.innerText = "Error: Could not extract text from active tab.";
            return;
        }

        const rawText = `SOURCE URL: ${tab.url}\n\nCONTENT:\n${results[0].result}`;

        // Attempt Cloud Run production endpoint first, fallback to local host
        const endpoints = [
            'http://localhost:10001/api/genesis/ingest',
            'https://api.osintneoai.me/api/genesis/ingest'
        ];

        let success = false;

        for (const ep of endpoints) {
            try {
                const res = await fetch(ep, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        raw_text: rawText,
                        source: "Chrome_Extension_Capture_Node",
                        client_metadata: { url: tab.url, title: tab.title }
                    })
                });

                if (res.ok) {
                    const data = await res.json();
                    statusDiv.style.color = '#22c55e';
                    statusDiv.innerText = `LOCKED: ${data.receipt_hash}\nTarget: ${data.target_entity}`;
                    success = true;
                    break;
                }
            } catch (err) {
                console.warn(`Endpoint ${ep} failed:`, err);
            }
        }

        if (!success) {
            statusDiv.style.color = '#ef4444';
            statusDiv.innerText = "API Connection Failed. Ensure local server or Cloud Run is active.";
        }
    });
});
