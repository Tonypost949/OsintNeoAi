import json
import os
import re
from datetime import datetime
from collections import defaultdict

def build_calendar():
    sources = [
        'data/google_photos_evidence_ocr.json',
        'data/google_photos_single_links_ocr.json',
        'data/google_photos_album1_full_manifest.json',
        'data/google_photos_album2_manifest.json',
        'data/google_photos_album3_manifest.json'
    ]

    all_items = []
    for fname in sources:
        if os.path.exists(fname):
            with open(fname, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    if isinstance(data, list):
                        all_items.extend(data)
                except Exception as e:
                    print(f"Error reading {fname}: {e}")

    by_date = defaultdict(list)
    seen_ids = set()

    for item in all_items:
        img_url = item.get('image_url') or item.get('url') or item.get('content_url')
        item_id = item.get('id') or img_url
        if not img_url or item_id in seen_ids:
            continue
        seen_ids.add(item_id)

        ts = item.get('timestamp') or item.get('photo_timestamp') or item.get('creation_time')
        date_str = None
        time_str = "00:00:00"
        
        if ts:
            try:
                if isinstance(ts, (int, float)):
                    t_val = float(ts)
                    if t_val > 1e11:
                        t_val /= 1000.0
                    dt = datetime.fromtimestamp(t_val)
                    date_str = dt.strftime('%Y-%m-%d')
                    time_str = dt.strftime('%H:%M:%S')
                elif isinstance(ts, str):
                    if ts.isdigit():
                        t_val = float(ts)
                        if t_val > 1e11:
                            t_val /= 1000.0
                        dt = datetime.fromtimestamp(t_val)
                        date_str = dt.strftime('%Y-%m-%d')
                        time_str = dt.strftime('%H:%M:%S')
                    else:
                        date_str = ts[:10]
                        if len(ts) >= 19:
                            time_str = ts[11:19]
            except Exception:
                pass

        if not date_str or not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            date_str = 'Undated'

        # Extract OCR / analysis text
        analysis = item.get('analysis') or item.get('ocr_summary') or item.get('description') or {}
        if isinstance(analysis, dict):
            extracted_text = analysis.get('full_text') or analysis.get('summary') or analysis.get('detected_text') or ''
            entities = analysis.get('entities') or []
        elif isinstance(analysis, str):
            extracted_text = analysis
            entities = []
        else:
            extracted_text = ''
            entities = []

        cleaned_item = {
            'id': item_id,
            'image_url': img_url,
            'width': item.get('width', 1920),
            'height': item.get('height', 1080),
            'timestamp': ts,
            'date_str': date_str,
            'time_str': time_str,
            'extracted_text': extracted_text,
            'entities': entities
        }
        by_date[date_str].append(cleaned_item)

    # Sort dates
    sorted_dates = sorted([d for d in by_date.keys() if d != 'Undated'])
    if 'Undated' in by_date:
        sorted_dates.append('Undated')

    # Convert to JSON payload for HTML embedding
    calendar_payload = {
        'dates': sorted_dates,
        'by_date': by_date,
        'total_photos': len(seen_ids)
    }

    payload_json = json.dumps(calendar_payload, ensure_ascii=False)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Google Photos OSINT Public Evidence Calendar & Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{
            --bg-dark: #0f172a;
            --card-bg: #1e293b;
            --panel-bg: #0f172a;
            --accent-blue: #38bdf8;
            --accent-purple: #c084fc;
            --accent-emerald: #34d399;
            --text-light: #f8fafc;
            --text-muted: #94a3b8;
        }}

        body {{
            background-color: var(--bg-dark);
            color: var(--text-light);
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            margin: 0;
            padding: 0;
            overflow-x: hidden;
        }}

        /* Header / Nav */
        .app-header {{
            background: rgba(30, 41, 59, 0.95);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(255,255,255,0.1);
            position: sticky;
            top: 0;
            z-index: 1000;
            padding: 12px 24px;
        }}

        .nav-btn {{
            background: #334155;
            color: #fff;
            border: 1px solid rgba(255,255,255,0.15);
            transition: all 0.2s ease;
        }}
        .nav-btn:hover {{
            background: var(--accent-blue);
            color: #000;
        }}

        /* Date Grid View */
        .grid-container {{
            max-width: 1400px;
            margin: 30px auto;
            padding: 0 20px;
        }}

        .date-card {{
            background: var(--card-bg);
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.08);
            padding: 20px;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            cursor: pointer;
            position: relative;
            overflow: hidden;
        }}

        .date-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 10px 25px rgba(56, 189, 248, 0.2);
            border-color: var(--accent-blue);
        }}

        .date-badge {{
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--accent-blue);
        }}

        .photo-count {{
            background: rgba(192, 132, 252, 0.2);
            color: var(--accent-purple);
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }}

        .thumb-preview {{
            width: 100%;
            height: 140px;
            object-fit: cover;
            border-radius: 8px;
            margin-top: 12px;
            background: #090d16;
        }}

        /* Full Screen Day Dashboard View */
        .fullscreen-day-view {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: #020617;
            z-index: 2000;
            display: none;
            flex-direction: column;
        }}

        .fullscreen-day-view.active {{
            display: flex;
        }}

        .day-header {{
            background: rgba(15, 23, 42, 0.95);
            padding: 14px 28px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}

        .day-content {{
            flex: 1;
            overflow-y: auto;
            padding: 24px;
        }}

        /* Daily Summary Dashboard Banner */
        .day-summary-banner {{
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.95));
            border: 1px solid rgba(56, 189, 248, 0.25);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.4);
        }}

        .summary-stat-box {{
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 12px;
            padding: 16px;
            text-align: center;
        }}

        .summary-stat-value {{
            font-size: 1.8rem;
            font-weight: 700;
            color: var(--accent-blue);
        }}

        /* Hybrid Thumbnails Strip */
        .hybrid-thumb-strip {{
            display: flex;
            gap: 12px;
            overflow-x: auto;
            padding: 12px 4px;
            margin-bottom: 24px;
            scrollbar-width: thin;
        }}

        .hybrid-thumb-item {{
            min-width: 120px;
            max-width: 120px;
            height: 90px;
            border-radius: 8px;
            object-fit: cover;
            cursor: pointer;
            border: 2px solid transparent;
            opacity: 0.7;
            transition: all 0.2s ease;
        }}

        .hybrid-thumb-item:hover, .hybrid-thumb-item.active {{
            opacity: 1;
            border-color: var(--accent-blue);
            transform: scale(1.05);
        }}

        .photo-display-card {{
            background: var(--card-bg);
            border-radius: 16px;
            border: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 30px;
            overflow: hidden;
            box-shadow: 0 15px 35px rgba(0,0,0,0.5);
            scroll-margin-top: 80px;
        }}

        .photo-img-large {{
            width: 100%;
            max-height: 75vh;
            object-fit: contain;
            background: #000;
            display: block;
        }}

        .photo-info-panel {{
            padding: 24px;
        }}

        .ocr-text-box {{
            background: #0f172a;
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 8px;
            padding: 16px;
            font-family: monospace;
            font-size: 0.9rem;
            color: #cbd5e1;
            max-height: 220px;
            overflow-y: auto;
            white-space: pre-wrap;
        }}

        .search-bar {{
            background: #1e293b;
            border: 1px solid rgba(255,255,255,0.15);
            color: #fff;
            border-radius: 8px;
            padding: 8px 16px;
            width: 300px;
        }}

        .search-bar:focus {{
            outline: none;
            border-color: var(--accent-blue);
            box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.3);
        }}
    </style>
</head>
<body>

    <!-- App Header -->
    <header class="app-header d-flex justify-content-between align-items-center">
        <div class="d-flex align-items-center gap-3">
            <i class="fa-solid fa-calendar-days text-info fs-3"></i>
            <div>
                <h4 class="mb-0 fw-bold">OSINT Google Photos Evidence Calendar & Dashboard</h4>
                <small class="text-muted"><span id="total-photos-count">0</span> Total Cataloged Photos across <span id="total-days-count">0</span> Days</small>
            </div>
        </div>
        <div class="d-flex align-items-center gap-3">
            <input type="text" id="searchInput" class="search-bar" placeholder="Search OCR text, date, or ID..." onkeyup="filterDates()">
            <button class="btn btn-outline-info btn-sm" onclick="closeFullscreen()"><i class="fa-solid fa-grid-2 me-1"></i> Grid View</button>
        </div>
    </header>

    <!-- Main Grid View -->
    <div class="grid-container" id="gridView">
        <h5 class="text-muted mb-4"><i class="fa-solid fa-clock-rotate-left me-2"></i>Select a Date to Open Daily Dashboard & Hybrid Preview</h5>
        <div class="row g-4" id="dateCardsRow">
            <!-- Dynamically populated -->
        </div>
    </div>

    <!-- Full-Screen Day Dashboard Page View -->
    <div class="fullscreen-day-view" id="fullscreenView">
        <div class="day-header">
            <div class="d-flex align-items-center gap-3">
                <button class="btn nav-btn btn-sm" onclick="closeFullscreen()"><i class="fa-solid fa-arrow-left me-1"></i> Back to Grid</button>
                <h3 class="mb-0 fw-bold text-info" id="currentDateTitle">YYYY-MM-DD</h3>
                <span class="photo-count" id="currentDateCount">0 Photos</span>
            </div>
            <div class="d-flex align-items-center gap-2">
                <button class="btn nav-btn btn-sm" id="prevDayBtn" onclick="navigateDay(-1)"><i class="fa-solid fa-chevron-left me-1"></i> Previous Day</button>
                <button class="btn nav-btn btn-sm" id="nextDayBtn" onclick="navigateDay(1)">Next Day <i class="fa-solid fa-chevron-right ms-1"></i></button>
            </div>
        </div>

        <div class="day-content" id="dayPhotosContainer">
            <!-- Dynamically populated with Daily Dashboard, Hybrid Preview Strip, and Photo Feed -->
        </div>
    </div>

    <script>
        const payload = {payload_json};
        let currentDayIndex = 0;

        function initApp() {{
            document.getElementById('total-photos-count').innerText = payload.total_photos;
            document.getElementById('total-days-count').innerText = payload.dates.length;
            renderGrid(payload.dates);

            // Keyboard navigation for full screen view
            document.addEventListener('keydown', (e) => {{
                const fs = document.getElementById('fullscreenView');
                if (fs.classList.contains('active')) {{
                    if (e.key === 'ArrowLeft') navigateDay(-1);
                    if (e.key === 'ArrowRight') navigateDay(1);
                    if (e.key === 'Escape') closeFullscreen();
                }}
            }});
        }}

        function renderGrid(datesList) {{
            const row = document.getElementById('dateCardsRow');
            row.innerHTML = '';

            datesList.forEach((dateStr) => {{
                const photos = payload.by_date[dateStr] || [];
                const firstThumb = photos.length > 0 ? photos[0].image_url : '';

                const col = document.createElement('div');
                col.className = 'col-12 col-sm-6 col-md-4 col-lg-3';
                col.innerHTML = `
                    <div class="date-card" onclick="openDayPage('${{dateStr}}')">
                        <div class="d-flex justify-content-between align-items-center">
                            <span class="date-badge">${{dateStr}}</span>
                            <span class="photo-count">${{photos.length}} photo${{photos.length > 1 ? 's' : ''}}</span>
                        </div>
                        ${{firstThumb ? `<img src="${{firstThumb}}" class="thumb-preview" loading="lazy" alt="Preview">` : '<div class="thumb-preview d-flex align-items-center justify-content-center text-muted">No Image</div>'}}
                    </div>
                `;
                row.appendChild(col);
            }});
        }}

        function openDayPage(dateStr) {{
            currentDayIndex = payload.dates.indexOf(dateStr);
            renderDayDashboardView();
            document.getElementById('fullscreenView').classList.add('active');
            window.scrollTo(0, 0);
        }}

        function closeFullscreen() {{
            document.getElementById('fullscreenView').classList.remove('active');
        }}

        function renderDayDashboardView() {{
            const dateStr = payload.dates[currentDayIndex];
            const photos = payload.by_date[dateStr] || [];

            document.getElementById('currentDateTitle').innerText = dateStr === 'Undated' ? 'Undated Photos Evidence' : `Date: ${{dateStr}}`;
            document.getElementById('currentDateCount').innerText = `${{photos.length}} Photo${{photos.length > 1 ? 's' : ''}}`;

            // Update nav buttons
            document.getElementById('prevDayBtn').disabled = currentDayIndex <= 0;
            document.getElementById('nextDayBtn').disabled = currentDayIndex >= payload.dates.length - 1;

            const container = document.getElementById('dayPhotosContainer');
            container.innerHTML = '';

            // 1. Calculate Daily Summary Statistics
            let totalWords = 0;
            const uniqueEntities = new Set();
            const timeRange = [];

            photos.forEach(p => {{
                if (p.extracted_text) {{
                    totalWords += p.extracted_text.split(/\\s+/).length;
                }}
                if (p.entities && Array.isArray(p.entities)) {{
                    p.entities.forEach(e => uniqueEntities.add(e));
                }}
                if (p.time_str && p.time_str !== '00:00:00') {{
                    timeRange.push(p.time_str);
                }}
            }});

            timeRange.sort();
            const startTime = timeRange.length > 0 ? timeRange[0] : 'N/A';
            const endTime = timeRange.length > 0 ? timeRange[timeRange.length - 1] : 'N/A';

            // 2. Build Daily Dashboard Banner
            const banner = document.createElement('div');
            banner.className = 'day-summary-banner';
            banner.innerHTML = `
                <div class="row align-items-center g-4">
                    <div class="col-lg-5">
                        <h4 class="fw-bold text-info mb-1"><i class="fa-solid fa-chart-line me-2"></i>Daily Intelligence Summary</h4>
                        <p class="text-muted mb-0" style="font-size: 0.95rem;">Comprehensive evidence overview for <strong>${{dateStr}}</strong>.</p>
                    </div>
                    <div class="col-lg-7">
                        <div class="row g-3">
                            <div class="col-4">
                                <div class="summary-stat-box">
                                    <div class="summary-stat-value">${{photos.length}}</div>
                                    <small class="text-muted">Total Photos</small>
                                </div>
                            </div>
                            <div class="col-4">
                                <div class="summary-stat-box">
                                    <div class="summary-stat-value" style="color: var(--accent-purple);">${{totalWords}}</div>
                                    <small class="text-muted">OCR Words Extracted</small>
                                </div>
                            </div>
                            <div class="col-4">
                                <div class="summary-stat-box">
                                    <div class="summary-stat-value" style="color: var(--accent-emerald);">${{uniqueEntities.size}}</div>
                                    <small class="text-muted">Extracted Entities</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            container.appendChild(banner);

            // 3. Build Hybrid Preview Thumbnails Strip
            const stripContainer = document.createElement('div');
            stripContainer.innerHTML = `<h6 class="text-muted mb-2"><i class="fa-solid fa-images me-2"></i>Hybrid Preview List (Click thumbnail to jump)</h6>`;
            const strip = document.createElement('div');
            strip.className = 'hybrid-thumb-strip';

            photos.forEach((photo, idx) => {{
                const img = document.createElement('img');
                img.src = photo.image_url;
                img.className = 'hybrid-thumb-item';
                img.title = `Photo #${{idx + 1}} (${{photo.time_str}})`;
                img.onclick = () => {{
                    const el = document.getElementById(`photo-card-${{idx}}`);
                    if (el) el.scrollIntoView({{ behavior: 'smooth' }});
                }};
                strip.appendChild(img);
            }});
            stripContainer.appendChild(strip);
            container.appendChild(stripContainer);

            // 4. Detailed Photo Cards Feed
            photos.forEach((photo, idx) => {{
                const card = document.createElement('div');
                card.className = 'photo-display-card';
                card.id = `photo-card-${{idx}}`;
                
                const ocrDisplay = photo.extracted_text ? photo.extracted_text : 'No OCR text extracted for this photo.';
                
                card.innerHTML = `
                    <div class="row g-0">
                        <div class="col-lg-8 bg-black d-flex align-items-center justify-content-center">
                            <a href="${{photo.image_url}}" target="_blank" title="Click to view full high-res original">
                                <img src="${{photo.image_url}}" class="photo-img-large" loading="lazy" alt="Photo ${{idx + 1}}">
                            </a>
                        </div>
                        <div class="col-lg-4 photo-info-panel d-flex flex-column justify-content-between">
                            <div>
                                <div class="d-flex justify-content-between align-items-center mb-3">
                                    <span class="badge bg-primary fs-6">Item #${{idx + 1}} of ${{photos.length}}</span>
                                    <small class="text-muted"><i class="fa-regular fa-clock me-1"></i>${{photo.time_str}}</small>
                                </div>
                                <h6 class="text-info fw-bold mb-2"><i class="fa-solid fa-file-lines me-2"></i>Neural OCR Analysis</h6>
                                <div class="ocr-text-box mb-3">${{escapeHtml(ocrDisplay)}}</div>
                                ${{photo.entities && photo.entities.length > 0 ? `
                                    <div class="mb-3">
                                        <small class="text-muted d-block mb-1">Detected Entities:</small>
                                        <div>${{photo.entities.map(e => `<span class="badge bg-secondary me-1 mb-1">${{escapeHtml(e)}}</span>`).join('')}}</div>
                                    </div>
                                ` : ''}}
                            </div>
                            <div class="pt-3 border-top border-secondary border-opacity-25">
                                <a href="${{photo.image_url}}" target="_blank" class="btn btn-outline-info btn-sm w-100 mb-2"><i class="fa-solid fa-up-right-from-square me-1"></i> Open Direct High-Res Image URL</a>
                                <small class="text-muted d-block text-truncate" style="font-size: 0.75rem;">ID: ${{photo.id}}</small>
                            </div>
                        </div>
                    </div>
                `;
                container.appendChild(card);
            }});

            document.getElementById('dayPhotosContainer').scrollTop = 0;
        }}

        function navigateDay(delta) {{
            const newIndex = currentDayIndex + delta;
            if (newIndex >= 0 && newIndex < payload.dates.length) {{
                currentDayIndex = newIndex;
                renderDayDashboardView();
            }}
        }}

        function filterDates() {{
            const query = document.getElementById('searchInput').value.toLowerCase().trim();
            if (!query) {{
                renderGrid(payload.dates);
                return;
            }}

            const filtered = payload.dates.filter(d => {{
                if (d.toLowerCase().includes(query)) return true;
                const photos = payload.by_date[d] || [];
                return photos.some(p => p.extracted_text.toLowerCase().includes(query) || p.id.toLowerCase().includes(query));
            }});

            renderGrid(filtered);
        }}

        function escapeHtml(text) {{
            return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
        }}

        window.onload = initApp;
    </script>
</body>
</html>
"""

    os.makedirs('public', exist_ok=True)
    with open('public/photo_calendar_app.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    with open('photo_calendar.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Successfully generated public photo calendar HTML at public/photo_calendar_app.html and photo_calendar.html with {len(sorted_dates)} dates and {len(seen_ids)} total photos!")

if __name__ == '__main__':
    build_calendar()
