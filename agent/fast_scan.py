import socket, ssl, time, json

def grab(ip, port, host, timeout=1.5):
    try:
        s = socket.socket()
        s.settimeout(timeout)
        s.connect((ip, port))
        if port == 80:
            req = 'GET / HTTP/1.1\r\nHost: ' + host + '\r\nUser-Agent: Mozilla/5.0\r\nConnection: close\r\n\r\n'
            s.send(req.encode())
        resp = s.recv(2048).decode('latin-1', errors='replace').split('\r\n')
        s.close()
        server = 'N/A'
        powered = ''
        for l in resp:
            if l.lower().startswith('server:'):
                server = l.split(':', 1)[1].strip()
            if l.lower().startswith('x-powered-by:'):
                powered = l.split(':', 1)[1].strip()
        status = resp[0] if resp else 'N/A'
        banner_short = status[:60]
        return {'port': port, 'status': 'OPEN', 'banner': banner_short, 'server': server, 'powered': powered}
    except:
        return {'port': port, 'status': 'CLOSED'}

def check_secret(ip, host, ep, port=443):
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        s = socket.socket()
        s.settimeout(3)
        s.connect((ip, port))
        ss = ctx.wrap_socket(s, server_hostname=host)
        req = 'GET ' + ep + ' HTTP/1.1\r\nHost: ' + host + '\r\nUser-Agent: Mozilla/5.0\r\nConnection: close\r\n\r\n'
        ss.send(req.encode())
        resp = ss.recv(1024).decode('latin-1', errors='replace')
        code = resp.split('\r\n')[0]
        ss.close()
        return ' 200 ' in code
    except:
        return False

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

ports = [21, 22, 23, 25, 80, 443, 3306, 3389, 5432, 8080, 8443, 9200, 27017, 6379, 5900]
secrets = ['/.env', '/.git/config', '/.aws/credentials', '/.aws/config', '/backup.sql', '/.config/db.yml']

summary = []
for name, ip in targets:
    print('')
    print('=== ' + name + ' (' + ip + ') ===')
    open_ports = []
    for port in ports:
        r = grab(ip, port, name)
        if r['status'] == 'OPEN':
            open_ports.append(r)
            msg = '  ' + str(port).rjust(5) + ': OPEN | ' + r['server'] + ' ' + r['powered'] + ' | ' + r['banner']
            print(msg)

    is_cf = ip.startswith('104.') or ip.startswith('172.67')
    found_secrets = []
    if not is_cf:
        for ep in secrets:
            if check_secret(ip, name, ep):
                found_secrets.append(ep)
                print('  EXPOSED: ' + ep)
            time.sleep(0.2)

    summary.append({
        'domain': name, 'ip': ip, 'cloudflare': is_cf,
        'open_port_count': len(open_ports),
        'open_ports': [p['port'] for p in open_ports],
        'exposed_secrets': found_secrets
    })
    time.sleep(0.2)

print('')
print('=' * 80)
print('SUMMARY')
print('=' * 80)
for s in sorted(summary, key=lambda x: x['open_port_count'], reverse=True):
    cf = ' [CF]' if s['cloudflare'] else ''
    sec = ''
    if s['exposed_secrets']:
        sec = ' SECRETS: ' + ','.join(s['exposed_secrets'])
    print(s['domain'].ljust(30) + str(s['open_port_count']).rjust(3) + ' ports' + cf + sec)

with open('C:/migrate opencode/OSINTNEOAI/agent/full_scan_results.json', 'w') as f:
    json.dump(summary, f, indent=2)
print('')
print('[SAVED] full_scan_results.json')
