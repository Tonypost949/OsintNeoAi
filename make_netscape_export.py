import json
import html

with open('C:/OsintNeoAi/scraped_system_bookmarks.json', 'r', encoding='utf-8') as f:
    bookmarks = json.load(f)

lines = [
    '<!DOCTYPE NETSCAPE-Bookmark-file-1>',
    '<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">',
    '<TITLE>Bookmarks</TITLE>',
    '<H1>Bookmarks</H1>',
    '<DL><p>',
    '    <DT><H3 ADD_DATE="1726850000" LAST_MODIFIED="1726850000">OsintNeoAi Master Harvested Bookmarks</H3>',
    '    <DL><p>'
]

for b in bookmarks:
    u = html.escape(b.get('url', ''))
    t = html.escape(b.get('title', b.get('name', 'Bookmark')))
    if u:
        lines.append(f'        <DT><A HREF="{u}" ADD_DATE="1726850000">{t}</A>')

lines.append('    </DL><p>')
lines.append('</DL><p>')

with open('C:/OsintNeoAi/bookmarks_master_backup.html', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print("Netscape Export generated successfully at C:/OsintNeoAi/bookmarks_master_backup.html")
