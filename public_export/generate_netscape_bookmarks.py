import json
import html

with open('C:/OsintNeoAi/scraped_system_bookmarks.json', 'r', encoding='utf-8') as f:
    bookmarks = json.load(f)

# Build Netscape HTML Format
netscape_html = """<!DOCTYPE NETSCAPE-Bookmark-file-1>
<!-- This is an automatically generated file.
     It will read and import cleanly into Chrome, Edge, and Firefox. -->
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks</H1>
<DL><p>
    <DT><H3 ADD_DATE="1726850000" LAST_MODIFIED="1726850000">OsintNeoAi Master Harvested Bookmarks (9,976 Links)</H3>
    <DL><p>
"""

for b in bookmarks:
    u = html.escape(b.get('url', ''))
    t = html.escape(b.get('title', b.get('name', 'Bookmark')))
    if u:
        netscape_html += f'        <DT><A HREF="{u}" ADD_DATE="1726850000">{t}</A>\n'

netscape_html += """    </DL><p>
</DL><p>
"""

with open('C:/OsintNeoAi/bookmarks_master_backup.html', 'w', encoding='utf-8') as f:
    f.write(netscape_html)

print("Netscape HTML Master Bookmark Export created at C:/OsintNeoAi/bookmarks_master_backup.html")
