import socket, time, json

def grab(ip, port, host, timeout=1):
    try:
        s = socket.socket()
        s.settimeout(timeout)
        s.connect((ip, port))
        if port == 80:
            req = 'GET / HTTP/1.1\r\nHost: ' + host + '\r\nConnection: close\r\n\r\n'
            s.send(req.encode())
        resp = s.recv(1024).decode('latin-1', errors='replace').split('\r\n')
        s.close()
        server = ''
        powered = ''
        for l in resp:
            if l.lower().startswith('server:'):
                server = l.split(':', 1)[1].strip()
            if l.lower().startswith('x-powered-by:'):
                powered = l.split(':', 1)[1].strip()
        first = resp[0] if resp else ''
        return {'port': port, 'server': server, 'powered': powered, 'first': first[:80]}
    except:
        return None

targets = [
    ('hbpd.org', '104.26.4.179'),
    ('huntingtonbeachca.gov', '104.26.15.40'),
    ('newportbeachca.gov', '104.18.10.121'),
    ('nbpd.org', '70.167.157.164'),
    ('santamonicapd.org', '45.223.97.122'),
    ('lapdonline.org', '23.1.33.17'),
    ('santaanapd.org', '198.185.159.145'),
    ('dallaspolice.net', '66.97.145.114'),
    ('cityofirvine.org', '45.223.147.193'),
    ('irvinepd.org', '104.26.7.159'),
    ('longbeach.gov', '204.108.16.117'),
    ('lbpd.org', '104.21.91.34'),
    ('anaheim.net', '89.106.200.153'),
    ('anaheimpd.org', '89.106.200.153'),
    ('santa-ana.org', '104.198.152.237'),
    ('ci.costa-mesa.ca.us', '135.84.124.41'),
    ('cityofwestminster.us', '198.243.1.145'),
    ('ci.buena-park.ca.us', '63.192.31.165'),
    ('ci.fullerton.ca.us', '135.84.124.41'),
    ('cityoftustin.org', '188.214.128.77'),
    ('cityoforange.org', '135.84.124.41'),
    ('lahabracity.com', '208.90.191.56'),
    ('columbus.gov', '52.247.170.120'),
    ('stpaul.gov', '54.165.146.83'),
]

ports = [21, 22, 25, 80, 443, 3306, 3389, 5432, 8080, 9200, 27017]

all_results = []
for name, ip in targets:
    print('--- ' + name + ' (' + ip + ') ---')
    found = []
    for port in ports:
        r = grab(ip, port, name)
        if r:
            found.append(r)
            extra = r['server'] + ' ' + r['powered']
            print('  ' + str(port).rjust(5) + ' OPEN  ' + extra.strip() + '  ' + r['first'][:50])
    if not found:
        print('  (no open ports found)')
    all_results.append({'domain': name, 'ip': ip, 'open': found})
    time.sleep(0.1)

print('')
print('========== COMPARISON TABLE ==========')
for r in all_results:
    ports_list = [str(x['port']) for x in r['open']]
    servers = set([x['server'] for x in r['open'] if x['server']])
    srv = ', '.join(servers) if servers else 'N/A'
    print(r['domain'].ljust(28) + str(len(r['open'])).rjust(3) + ' open  ' + srv[:30] + '  [' + ' '.join(ports_list) + ']')

with open('C:/migrate opencode/OSINTNEOAI/agent/full_scan_results.json', 'w') as f:
    json.dump(all_results, f, indent=2)
print('[DONE]')
