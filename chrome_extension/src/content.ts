/**
 * OSINTNeoAi - Universal DOM Ripper
 * 
 * Injected into active tabs to bypass captchas and extract raw evidence
 * from wildly varied municipal, court, and unclaimed property sites.
 */

// Listen for messages from the background script (triggered by hotkey)
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "RIP_OSINT_EVIDENCE") {
        try {
            const evidence = extractUniversalEvidence();
            sendResponse({ success: true, data: evidence });
        } catch (error: any) {
            sendResponse({ success: false, error: error.toString() });
        }
    }
    return true; // Keep message channel open for async
});

function extractUniversalEvidence() {
    // 1. Rip all visible human-readable text (bypasses weird HTML structures)
    const rawText = document.body.innerText;

    // 2. Rip all tabular data (Crucial for unclaimed property / tax sites)
    const tables = Array.from(document.querySelectorAll("table")).map(table => table.outerHTML);

    // 3. Hunt for Video / Closed Caption transcripts universally
    const tracks = Array.from(document.querySelectorAll("track")).map(t => t.src);
    
    // Check network/source code hints for hidden VTTs (like Granicus)
    const pageSource = document.documentElement.innerHTML;
    const vttMatches = pageSource.match(/(https?:\/\/[^\s"']+\.(?:vtt|srt))/gi) || [];
    const uniqueCaptions = [...new Set([...tracks, ...vttMatches])];

    // 4. Hunt for PDFs and Documents (For Azure OCR)
    const links = Array.from(document.querySelectorAll("a"));
    const documentLinks = links
        .map(a => a.href)
        .filter(href => href.toLowerCase().endsWith('.pdf') || href.toLowerCase().endsWith('.docx'));

    // 5. Build the universal payload
    return {
        url: window.location.href,
        title: document.title,
        timestamp: new Date().toISOString(),
        raw_text_dump: rawText.substring(0, 50000), // Cap at 50k chars to send to LLM
        html_tables: tables,
        video_transcripts: uniqueCaptions,
        ocr_targets: [...new Set(documentLinks)]
    };
}
