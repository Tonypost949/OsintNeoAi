#!/usr/bin/env python3
"""
OsintNeoAI Local Bridge v2 - Full OSINT + Local AI
Comprehensive OSINT toolkit with Ollama integration
"""

import json
import requests
import subprocess
import socket
import ssl
import hashlib
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
import concurrent.futures

try:
    import whois
except:
    whois = None

try:
    import dns.resolver
    import dns.reversename
except:
    dns = None

try:
    from shodan import Shodan
except:
    Shodan = None

try:
    import httpx
except:
    httpx = None

try:
    from bs4 import BeautifulSoup
except:
    BeautifulSoup = None

OLLAMA_URL = "http://localhost:11434"
MODEL = "qwen2.5-coder-1.5b"

# ============================================================
# OLLAMA INTEGRATION
# ============================================================

def check_ollama():
    """Check if Ollama is running"""
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        return r.status_code == 200
    except:
        return False

def query_ollama(prompt, system="You are an OSINT assistant. Analyze data and provide actionable intelligence. Be concise."):
    """Query local Ollama model"""
    r = requests.post(f"{OLLAMA_URL}/api/generate", json={
        "model": MODEL,
        "prompt": prompt,
        "system": system,
        "stream": False
    }, timeout=120)
    return r.json().get("response", "")

def analyze_with_ai(data, question="Analyze this OSINT data for security concerns and actionable intelligence"):
    """Use local AI to analyze OSINT results"""
    prompt = f"OSINT Data:\n{json.dumps(data, indent=2)[:2000]}\n\nQuestion: {question}"
    return query_ollama(prompt)

# ============================================================
# DNS OSINT
# ============================================================

def dns_full(domain):
    """Full DNS enumeration"""
    results = {"domain": domain, "records": {}}
    
    record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA', 'CNAME', 'SRV']
    
    for rtype in record_types:
        try:
            answers = dns.resolver.resolve(domain, rtype)
            results["records"][rtype] = [str(r) for r in answers]
        except:
            pass
    
    return results

def subdomain_enum(domain):
    """Basic subdomain enumeration via DNS"""
    common_subdomains = [
        'www', 'mail', 'ftp', 'smtp', 'pop', 'ns1', 'ns2', 'ns3',
        'webmail', 'cpanel', 'direct', 'gateway', 'vpn', 'api',
        'dev', 'staging', 'test', 'admin', 'portal', 'remote',
        'blog', 'shop', 'store', 'cdn', 'media', 'static',
        'app', 'mobile', 'beta', 'demo', 'sandbox', 'git'
    ]
    
    found = []
    for sub in common_subdomains:
        try:
            full = f"{sub}.{domain}"
            dns.resolver.resolve(full, 'A')
            found.append(full)
        except:
            pass
    
    return {"domain": domain, "subdomains_found": found}

# ============================================================
# IP/ASN OSINT
# ============================================================

def reverse_dns(ip):
    """Reverse DNS lookup"""
    try:
        hostname = socket.gethostbyaddr(ip)
        return {"ip": ip, "hostname": hostname[0], "aliases": hostname[1]}
    except:
        return {"ip": ip, "hostname": "N/A"}

def ip_info(ip):
    """Get IP info from public APIs"""
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=10)
        return r.json()
    except:
        return {"ip": ip, "error": "lookup failed"}

def asn_lookup(ip):
    """ASN lookup"""
    try:
        r = requests.get(f"https://ipinfo.io/{ip}/json", timeout=10)
        return r.json()
    except:
        return {"ip": ip, "error": "lookup failed"}

# ============================================================
# PORT SCANNING
# ============================================================

def scan_port(host, port, timeout=1):
    """Scan a single port"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            result = s.connect_ex((host, port))
            return result == 0
    except:
        return False

def port_scan(host, ports=None):
    """Quick port scan with banner grabbing"""
    if ports is None:
        ports = [21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 
                 445, 993, 995, 1433, 1521, 3306, 3389, 5432, 5900, 
                 6379, 8080, 8443, 8888, 9090, 27017]
    
    results = {"host": host, "open_ports": [], "banners": {}}
    
    for port in ports:
        if scan_port(host, port):
            results["open_ports"].append(port)
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(2)
                    s.connect((host, port))
                    s.send(b"HEAD / HTTP/1.0\r\nHost: %b\r\n\r\n" % host.encode())
                    banner = s.recv(1024).decode('utf-8', errors='ignore').strip()[:200]
                    results["banners"][port] = banner
            except:
                pass
    
    return results

def full_port_scan(host, timeout=0.5):
    """Scan common ports 1-1024 and known services"""
    results = {"host": host, "open_ports": []}
    
    common_ports = list(range(1, 1024)) + [3306, 3389, 5432, 5900, 6379, 8080, 8443, 8888, 27017]
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = {executor.submit(scan_port, host, port, timeout): port for port in common_ports}
        for future in concurrent.futures.as_completed(futures):
            port = futures[future]
            if future.result():
                results["open_ports"].append(port)
    
    results["open_ports"].sort()
    return results

# ============================================================
# WHOIS OSINT
# ============================================================

def whois_domain(domain):
    """Domain WHOIS lookup"""
    if not whois:
        return {"error": "python-whois not installed"}
    
    try:
        w = whois.whois(domain)
        return {
            "domain": domain,
            "registrar": w.registrar,
            "creation_date": str(w.creation_date),
            "expiration_date": str(w.expiration_date),
            "name_servers": w.name_servers,
            "registrant": w.org,
            "country": w.country,
            "emails": w.emails
        }
    except Exception as e:
        return {"domain": domain, "error": str(e)}

def whois_ip(ip):
    """IP WHOIS lookup"""
    try:
        r = requests.get(f"https://rdap.arin.net/registry/ip/{ip}", timeout=10)
        data = r.json()
        return {
            "ip": ip,
            "name": data.get("name"),
            "handle": data.get("handle"),
            "start": data.get("startAddress"),
            "end": data.get("endAddress"),
            "country": data.get("country"),
            "orgName": data.get("entities", [{}])[0].get("vcardArray", [])[1][0][3] if data.get("entities") else None
        }
    except:
        return {"ip": ip, "error": "lookup failed"}

# ============================================================
# HTTP/WEB OSINT
# ============================================================

def http_headers(url):
    """Fetch and analyze HTTP headers"""
    if not url.startswith(('http://', 'https://')):
        url = f"https://{url}"
    
    try:
        with httpx.Client(verify=False, follow_redirects=True, timeout=10) as client:
            r = client.get(url)
            
            headers = dict(r.headers)
            
            result = {
                "url": url,
                "status": r.status_code,
                "headers": headers,
                "server": headers.get("server", "unknown"),
                "technologies": [],
                "security_headers": {
                    "strict-transport-security": headers.get("strict-transport-security") is not None,
                    "x-frame-options": headers.get("x-frame-options") is not None,
                    "x-content-type-options": headers.get("x-content-type-options") is not None,
                    "content-security-policy": headers.get("content-security-policy") is not None,
                    "x-xss-protection": headers.get("x-xss-protection") is not None,
                }
            }
            
            # Technology detection from headers
            server = headers.get("server", "").lower()
            if "apache" in server: result["technologies"].append("Apache")
            if "nginx" in server: result["technologies"].append("Nginx")
            if "cloudflare" in server: result["technologies"].append("Cloudflare")
            if "iis" in server: result["technologies"].append("IIS")
            
            powered_by = headers.get("x-powered-by", "").lower()
            if "php" in powered_by: result["technologies"].append("PHP")
            if "asp" in powered_by: result["technologies"].append("ASP.NET")
            if "express" in powered_by: result["technologies"].append("Express.js")
            
            # Check cookies
            cookies = dict(r.cookies)
            result["cookies"] = list(cookies.keys())
            
            return result
    except Exception as e:
        return {"url": url, "error": str(e)}

def technology_fingerprint(url):
    """Detect technologies from HTML"""
    if not url.startswith(('http://', 'https://')):
        url = f"https://{url}"
    
    try:
        with httpx.Client(verify=False, follow_redirects=True, timeout=10) as client:
            r = client.get(url)
            soup = BeautifulSoup(r.text, 'html.parser') if BeautifulSoup else None
            
            result = {"url": url, "technologies": [], "meta": {}}
            
            if soup:
                # Meta tags
                for meta in soup.find_all('meta'):
                    name = meta.get('name', meta.get('property', '')).lower()
                    content = meta.get('content', '')
                    if name and content:
                        result["meta"][name] = content[:100]
                
                # Generator
                gen = soup.find('meta', attrs={'name': 'generator'})
                if gen:
                    result["technologies"].append(f"CMS: {gen.get('content')}")
                
                # Scripts
                scripts = [s.get('src', '') for s in soup.find_all('script') if s.get('src')]
                tech_keywords = {
                    'jquery': 'jQuery', 'bootstrap': 'Bootstrap', 'react': 'React',
                    'angular': 'Angular', 'vue': 'Vue.js', 'next': 'Next.js',
                    'nuxt': 'Nuxt.js', 'gatsby': 'Gatsby', 'wordpress': 'WordPress',
                    'drupal': 'Drupal', 'joomla': 'Joomla', 'shopify': 'Shopify',
                    'wix': 'Wix', 'squarespace': 'Squarespace'
                }
                
                for script in scripts:
                    script_lower = script.lower()
                    for key, name in tech_keywords.items():
                        if key in script_lower and name not in result["technologies"]:
                            result["technologies"].append(name)
                
                # Links
                links = [l.get('href', '') for l in soup.find_all('link')]
                for link in links:
                    link_lower = link.lower()
                    for key, name in tech_keywords.items():
                        if key in link_lower and name not in result["technologies"]:
                            result["technologies"].append(name)
            
            return result
    except Exception as e:
        return {"url": url, "error": str(e)}

# ============================================================
# CERTIFICATE OSINT
# ============================================================

def cert_transparency(domain):
    """Query certificate transparency logs"""
    try:
        r = requests.get(f"https://crt.sh/?q=%25.{domain}&output=json", timeout=15)
        entries = r.json()
        
        certs = []
        seen = set()
        for entry in entries[:50]:  # Limit to 50
            name = entry.get('name_value', '')
            if name not in seen:
                seen.add(name)
                certs.append({
                    "name": name,
                    "issuer": entry.get('issuer_name', ''),
                    "not_before": entry.get('not_before', ''),
                    "not_after": entry.get('not_after', '')
                })
        
        return {"domain": domain, "certificates": certs[:20], "total": len(seen)}
    except Exception as e:
        return {"domain": domain, "error": str(e)}

def ssl_check(host, port=443):
    """Check SSL certificate details"""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                return {
                    "host": host,
                    "subject": dict(x[0] for x in cert.get('subject', [])),
                    "issuer": dict(x[0] for x in cert.get('issuer', [])),
                    "serial": cert.get('serialNumber'),
                    "notBefore": cert.get('notBefore'),
                    "notAfter": cert.get('notAfter'),
                    "san": [x[1] for x in cert.get('subjectAltName', [])]
                }
    except Exception as e:
        return {"host": host, "error": str(e)}

# ============================================================
# EMAIL OSINT
# ============================================================

def email_check(email):
    """Basic email validation and OSINT"""
    import re
    
    result = {"email": email, "valid_format": False, "checks": {}}
    
    # Format validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    result["valid_format"] = bool(re.match(pattern, email))
    
    if result["valid_format"]:
        domain = email.split('@')[1]
        
        # MX check
        if dns:
            try:
                answers = dns.resolver.resolve(domain, 'MX')
                result["checks"]["mx_exists"] = True
                result["mx_servers"] = [str(r.exchange) for r in answers]
            except:
                result["checks"]["mx_exists"] = False
        
        # Common email patterns
        local = email.split('@')[0]
        result["checks"]["has_numbers"] = any(c.isdigit() for c in local)
        result["checks"]["length"] = len(local)
        
        # Disposable email check
        disposable_domains = ['tempmail.com', 'throwaway.email', 'guerrillamail.com', 
                            'mailinator.com', 'yopmail.com', '10minutemail.com']
        result["checks"]["is_disposable"] = domain.lower() in disposable_domains
    
    return result

def email_harvest(domain):
    """Check for email patterns on a domain"""
    result = {"domain": domain, "common_patterns": []}
    
    common_names = ['admin', 'info', 'support', 'contact', 'sales', 'hr', 'marketing']
    common_tlds = ['@' + domain]
    
    for name in common_names:
        result["common_patterns"].append(f"{name}@{domain}")
    
    return result

# ============================================================
# USERNAME OSINT
# ============================================================

def username_check(username):
    """Check username availability across platforms"""
    platforms = {
        "GitHub": f"https://github.com/{username}",
        "Twitter": f"https://twitter.com/{username}",
        "Instagram": f"https://www.instagram.com/{username}/",
        "LinkedIn": f"https://www.linkedin.com/in/{username}",
        "Reddit": f"https://www.reddit.com/user/{username}",
        "Medium": f"https://medium.com/@{username}",
        "Dev.to": f"https://dev.to/{username}",
        "Keybase": f"https://keybase.io/{username}",
        "HackerNews": f"https://news.ycombinator.com/user?id={username}",
        "Patreon": f"https://www.patreon.com/{username}",
        "YouTube": f"https://www.youtube.com/@{username}",
        "TikTok": f"https://www.tiktok.com/@{username}",
        "Pinterest": f"https://www.pinterest.com/{username}",
        "Twitch": f"https://www.twitch.tv/{username}",
        "Steam": f"https://steamcommunity.com/id/{username}"
    }
    
    results = {"username": username, "platforms": {}}
    
    for platform, url in platforms.items():
        try:
            r = httpx.get(url, follow_redirects=False, timeout=5) if httpx else None
            status = r.status_code if r else "N/A"
            results["platforms"][platform] = {
                "url": url,
                "status": status,
                "exists": status == 200 if isinstance(status, int) else None
            }
        except:
            results["platforms"][platform] = {"url": url, "status": "error"}
    
    return results

# ============================================================
# BREACH/CREDENTIAL OSINT
# ============================================================

def paste_check(email):
    """Check Have I Been Pwned pastes (requires API key for full)"""
    try:
        headers = {"user-agent": "OsintNeoAI-Local"}
        r = requests.get(
            f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}?truncateResponse=false",
            headers=headers, timeout=10
        )
        if r.status_code == 200:
            return {"email": email, "breached": True, "breaches": r.json()}
        elif r.status_code == 404:
            return {"email": email, "breached": False}
        else:
            return {"email": email, "error": f"Status {r.status_code}"}
    except:
        return {"email": email, "error": "API unavailable (get free API key at haveibeenpwned.com)"}

# ============================================================
# SHODAN OSINT
# ============================================================

def shodan_lookup(ip, api_key=None):
    """Shodan lookup for IP"""
    if not api_key:
        # Try unauthenticated first
        try:
            r = requests.get(f"https://internetdb.shodan.io/{ip}", timeout=10)
            data = r.json()
            return {
                "ip": ip,
                "ports": data.get("ports", []),
                "hostnames": data.get("hostnames", []),
                "domains": data.get("domains", []),
                "vulns": data.get("vulns", []),
                "cpes": data.get("cpes", [])
            }
        except:
            return {"ip": ip, "error": "Shodan lookup failed"}
    
    try:
        api = Shodan(api_key)
        host = api.host(ip)
        return {
            "ip": ip,
            "ports": host.get("ports", []),
            "hostnames": host.get("hostnames", []),
            "org": host.get("org"),
            "os": host.get("os"),
            "vulns": host.get("vulns", []),
            "data": [{"port": s.get("port"), "product": s.get("product"), "banner": s.get("data", "")[:200]} for s in host.get("data", [])]
        }
    except:
        return {"ip": ip, "error": "Shodan lookup failed"}

# ============================================================
# OSINT COMMANDS
# ============================================================

def recon(domain):
    """Full reconnaissance on a domain"""
    print(f"\n[*] Starting recon on {domain}...")
    
    results = {"domain": domain, "timestamp": datetime.now().isoformat()}
    
    print("[*] DNS enumeration...")
    results["dns"] = dns_full(domain)
    
    print("[*] Subdomain enumeration...")
    results["subdomains"] = subdomain_enum(domain)
    
    print("[*] WHOIS lookup...")
    results["whois"] = whois_domain(domain)
    
    print("[*] SSL certificate check...")
    results["ssl"] = ssl_check(domain)
    
    print("[*] Certificate transparency...")
    results["certs"] = cert_transparency(domain)
    
    print("[*] HTTP headers analysis...")
    results["http"] = http_headers(domain)
    
    print("[*] Technology fingerprint...")
    results["tech"] = technology_fingerprint(domain)
    
    # Port scan on primary IP
    if results["dns"].get("records", {}).get("A"):
        primary_ip = results["dns"]["records"]["A"][0]
        print(f"[*] Port scan on {primary_ip}...")
        results["ports"] = port_scan(primary_ip)
        
        print("[*] IP information...")
        results["ip_info"] = ip_info(primary_ip)
        
        print("[*] Shodan lookup...")
        results["shodan"] = shodan_lookup(primary_ip)
        
        print("[*] Reverse DNS...")
        results["rDNS"] = reverse_dns(primary_ip)
    
    print("[+] Recon complete!")
    return results

def full_recon(domain):
    """Full reconnaissance with deep scans"""
    results = recon(domain)
    
    # Deep port scan
    if results["dns"].get("records", {}).get("A"):
        primary_ip = results["dns"]["records"]["A"][0]
        print(f"[*] Deep port scan on {primary_ip} (this may take a while)...")
        results["deep_ports"] = full_port_scan(primary_ip, timeout=0.3)
    
    return results

# ============================================================
# WIFI OSINT
# ============================================================

def wifi_networks_local():
    """Scan local WiFi networks (Windows netsh)"""
    try:
        result = subprocess.run(
            ['netsh', 'wlan', 'show', 'networks', 'mode=bssid'],
            capture_output=True, text=True, timeout=10
        )
        networks = []
        current = {}
        for line in result.stdout.split('\n'):
            line = line.strip()
            if 'SSID' in line and 'BSSID' not in line:
                if current:
                    networks.append(current)
                current = {"ssid": line.split(':', 1)[-1].strip()}
            elif 'Signal' in line:
                current["signal"] = line.split(':', 1)[-1].strip()
            elif 'Authentication' in line:
                current["auth"] = line.split(':', 1)[-1].strip()
            elif 'Encryption' in line:
                current["encryption"] = line.split(':', 1)[-1].strip()
            elif 'BSSID' in line:
                current["bssid"] = line.split(':', 1)[-1].strip()
            elif 'Channel' in line:
                current["channel"] = line.split(':', 1)[-1].strip()
        if current:
            networks.append(current)
        return {"networks": networks, "count": len(networks)}
    except Exception as e:
        return {"error": str(e)}

def wifi_profiles():
    """List saved WiFi profiles"""
    try:
        result = subprocess.run(
            ['netsh', 'wlan', 'show', 'profiles'],
            capture_output=True, text=True, timeout=10
        )
        profiles = []
        for line in result.stdout.split('\n'):
            if 'All User Profile' in line or 'Profile' in line:
                name = line.split(':', 1)[-1].strip()
                if name and name != '':
                    profiles.append(name)
        return {"saved_profiles": profiles, "count": len(profiles)}
    except Exception as e:
        return {"error": str(e)}

def wifi_profile_detail(profile_name):
    """Get saved WiFi profile password (requires admin)"""
    try:
        result = subprocess.run(
            ['netsh', 'wlan', 'show', 'profile', f'name={profile_name}', 'key=clear'],
            capture_output=True, text=True, timeout=10
        )
        password = None
        for line in result.stdout.split('\n'):
            if 'Key Content' in line:
                password = line.split(':', 1)[-1].strip()
        return {"profile": profile_name, "password": password or "requires admin"}
    except Exception as e:
        return {"error": str(e)}

def wigle_wifi_search(ssid=None, lat=None, lon=None, distance=1000):
    """Query WiGLE.net for WiFi network info (free API, registration required for full)"""
    try:
        if ssid:
            r = requests.get(
                f"https://api.wigle.net/api/v2/network/search?ssid={ssid}",
                timeout=10
            )
        elif lat and lon:
            r = requests.get(
                f"https://api.wigle.net/api/v2/network/search?latrange1={lat-0.01}&latrange2={lat+0.01}&longrange1={lon-0.01}&longrange2={lon+0.01}",
                timeout=10
            )
        else:
            return {"error": "Provide ssid or lat/lon"}
        
        if r.status_code == 200:
            data = r.json()
            return {
                "total_results": data.get("totalResults", 0),
                "results": data.get("results", [])[:20]
            }
        else:
            return {"error": f"WiGLE API returned {r.status_code}"}
    except Exception as e:
        return {"error": str(e)}

# ============================================================
# BLUETOOTH OSINT
# ============================================================

def bluetooth_scan():
    """Scan for Bluetooth devices (Windows)"""
    try:
        result = subprocess.run(
            ['powershell', '-Command', 'Get-PnpDevice -Class Bluetooth | Select-Object -Property Name,Status,InstanceId | ConvertTo-Json'],
            capture_output=True, text=True, timeout=15
        )
        devices = json.loads(result.stdout) if result.stdout.strip() else []
        if isinstance(devices, dict):
            devices = [devices]
        return {"bluetooth_devices": devices, "count": len(devices)}
    except Exception as e:
        return {"error": str(e)}

def bluetooth_lookup_mac(mac):
    """Look up Bluetooth MAC vendor"""
    try:
        mac_clean = mac.replace(':', '').replace('-', '').upper()[:6]
        r = requests.get(f"https://api.macvendors.com/{mac_clean}", timeout=5)
        return {"mac": mac, "vendor": r.text.strip() if r.status_code == 200 else "unknown"}
    except:
        return {"mac": mac, "vendor": "lookup failed"}

def bluetooth_le_scan():
    """Query Bluetooth LE device databases"""
    # Public BT LE tracking databases
    try:
        r = requests.get(
            "https://raw.githubusercontent.com/nickoala/bluetooth-le-db/main/known_devices.json",
            timeout=10
        )
        if r.status_code == 200:
            return {"known_devices": r.json(), "note": "Community-maintained BT LE database"}
    except:
        pass
    return {"note": "No public BT LE database available locally"}

# ============================================================
# MOBILE OSINT
# ============================================================

def phone_lookup(number):
    """Phone number OSINT"""
    import re
    
    # Clean number
    cleaned = re.sub(r'[^0-9+]', '', number)
    
    result = {"number": number, "cleaned": cleaned}
    
    # Basic validation
    if cleaned.startswith('+'):
        result["international"] = True
        result["country_code"] = re.match(r'^\+(\d{1,3})', cleaned).group(1)
    elif len(cleaned) == 10:
        result["international"] = False
        result["formatted"] = f"+1{cleaned}"
    
    # NumVerify (free tier, 100 req/month)
    try:
        r = requests.get(
            f"http://apilayer.net/api/validate?access_key=demo&number={cleaned}",
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            result["valid"] = data.get("valid")
            result["line_type"] = data.get("line_type")
            result["carrier"] = data.get("carrier")
            result["location"] = data.get("location")
    except:
        pass
    
    return result

def imei_check(imei):
    """IMEI validation and lookup"""
    # Luhn algorithm check
    def luhn(n):
        digits = [int(d) for d in str(n)]
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        total = sum(odd_digits)
        for d in even_digits:
            total += sum(divmod(d * 2, 10))
        return total % 10 == 0
    
    result = {
        "imei": imei,
        "valid_luhn": luhn(imei),
        "type": "unknown"
    }
    
    # TAC (first 8 digits) identification
    tac = imei[:8]
    try:
        r = requests.get(f"https://json.imeidata.net/plain/{tac}", timeout=5)
        if r.status_code == 200:
            data = r.json()
            result["manufacturer"] = data.get("manufacturer")
            result["model"] = data.get("model")
            result["type"] = data.get("type")
    except:
        pass
    
    return result

def sms_lookup(service, number):
    """Check SMS verification services"""
    services = {
        "freephonenum": f"https://freephonenum.com/numbers/{number}",
        "receive-sms": f"https://receive-sms-free.info/numbers/{number}",
        "smsreceivefree": f"https://smsreceivefree.com/number/{number}"
    }
    
    if service in services:
        try:
            r = requests.get(services[service], timeout=10)
            return {"service": service, "url": services[service], "status": r.status_code}
        except:
            return {"service": service, "error": "lookup failed"}
    else:
        return {"available_services": list(services.keys())}

# ============================================================
# IP REPUTATION OSINT
# ============================================================

def ip_reputation(ip):
    """Comprehensive IP reputation check"""
    results = {"ip": ip, "checks": {}}
    
    # AbuseIPDB (free, 1000 req/day)
    try:
        r = requests.get(
            f"https://api.abuseipdb.com/api/v2/check?ipAddress={ip}",
            headers={"Key": "demo", "Accept": "application/json"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json().get("data", {})
            results["checks"]["abuseipdb"] = {
                "abuse_score": data.get("abuseConfidenceScore"),
                "country": data.get("countryCode"),
                "isp": data.get("isp"),
                "domain": data.get("domain"),
                "usage": data.get("usageType"),
                "reports": data.get("totalReports"),
                "last_reported": data.get("lastReportedAt")
            }
    except:
        pass
    
    # VirusTotal (free, 4 req/min)
    try:
        r = requests.get(
            f"https://www.virustotal.com/api/v3/ip_addresses/{ip}",
            timeout=10
        )
        if r.status_code == 200:
            data = r.json().get("data", {}).get("attributes", {})
            results["checks"]["virustotal"] = {
                "harmless": data.get("last_analysis_stats", {}).get("harmless"),
                "malicious": data.get("last_analysis_stats", {}).get("malicious"),
                "suspicious": data.get("last_analysis_stats", {}).get("suspicious"),
                "reputation": data.get("reputation"),
                "asn": data.get("asn"),
                "as_owner": data.get("as_owner")
            }
    except:
        pass
    
    # GreyNoise (free, 50 req/day)
    try:
        r = requests.get(
            f"https://api.greynoise.io/v3/community/{ip}",
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            results["checks"]["greynoise"] = {
                "noise": data.get("noise"),
                "riot": data.get("riot"),
                "classification": data.get("classification"),
                "name": data.get("name"),
                "link": data.get("link")
            }
    except:
        pass
    
    # IPQualityScore (free tier)
    try:
        r = requests.get(
            f"https://ipqualityscore.com/api/json/ip/7FhA4sKr1WUt7Z5o6Qw2vN8mJx3kLb9p/{ip}",
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            results["checks"]["ipqualityscore"] = {
                "fraud_score": data.get("fraud_score"),
                "is_proxy": data.get("proxy"),
                "is_vpn": data.get("vpn"),
                "is_tor": data.get("tor"),
                "is_mobile": data.get("mobile"),
                "country_code": data.get("country_code"),
                "isp": data.get("ISP"),
                "hosting": data.get("hosting")
            }
    except:
        pass
    
    return results

def reverse_ip_lookup(ip):
    """Reverse IP lookup - find domains on same IP"""
    try:
        # SecurityTrails free
        r = requests.get(
            f"https://api.securitytrails.com/v1/domain/{ip}/subdomains",
            timeout=10
        )
        if r.status_code == 200:
            return {"ip": ip, "domains": r.json().get("subdomains", [])}
    except:
        pass
    
    # Fallback: DNS reverse lookup
    try:
        hostname = socket.gethostbyaddr(ip)
        return {"ip": ip, "hostname": hostname[0], "aliases": hostname[1]}
    except:
        return {"ip": ip, "error": "no results"}

def geoip(ip):
    """Geolocation lookup"""
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,mobile,proxy,hosting,query", timeout=5)
        return r.json()
    except:
        return {"ip": ip, "error": "lookup failed"}

# ============================================================
# SOCIAL MEDIA OSINT
# ============================================================

def social_media_check(username):
    """Comprehensive social media username check"""
    platforms = {
        "GitHub": "https://github.com/{u}",
        "Twitter": "https://twitter.com/{u}",
        "Instagram": "https://www.instagram.com/{u}/",
        "LinkedIn": "https://www.linkedin.com/in/{u}",
        "Reddit": "https://www.reddit.com/user/{u}",
        "Medium": "https://medium.com/@{u}",
        "Dev.to": "https://dev.to/{u}",
        "Keybase": "https://keybase.io/{u}",
        "HackerNews": "https://news.ycombinator.com/user?id={u}",
        "Patreon": "https://www.patreon.com/{u}",
        "YouTube": "https://www.youtube.com/@{u}",
        "TikTok": "https://www.tiktok.com/@{u}",
        "Pinterest": "https://www.pinterest.com/{u}",
        "Twitch": "https://www.twitch.tv/{u}",
        "Steam": "https://steamcommunity.com/id/{u}",
        "Spotify": "https://open.spotify.com/user/{u}",
        "SoundCloud": "https://soundcloud.com/{u}",
        "Flickr": "https://www.flickr.com/people/{u}",
        "Tumblr": "https://{u}.tumblr.com",
        "WordPress": "https://{u}.wordpress.com",
        "Blogger": "https://{u}.blogspot.com",
        "Gravatar": "https://en.gravatar.com/{u}",
        "About.me": "https://about.me/{u}",
        "Linktree": "https://linktr.ee/{u}",
        "Trello": "https://trello.com/{u}",
        "GitLab": "https://gitlab.com/{u}",
        "Bitbucket": "https://bitbucket.org/{u}/",
        "npm": "https://www.npmjs.com/~{u}",
        "PyPI": "https://pypi.org/user/{u}/",
        "DockerHub": "https://hub.docker.com/u/{u}",
        "HackerOne": "https://hackerone.com/{u}",
        "BugBounty": "https://bugbounty.com/{u}",
        "Telegram": "https://t.me/{u}",
        "Signal": "https://signal.me/#p/{u}",
        "Mastodon": "https://mastodon.social/@{u}",
        "Bluesky": "https://bsky.app/profile/{u}"
    }
    
    results = {"username": username, "platforms": {}, "found": [], "not_found": []}
    
    for platform, url_template in platforms.items():
        url = url_template.format(u=username)
        try:
            r = httpx.get(url, follow_redirects=False, timeout=5) if httpx else None
            status = r.status_code if r else "N/A"
            exists = status == 200 if isinstance(status, int) else None
            
            results["platforms"][platform] = {
                "url": url,
                "status": status,
                "exists": exists
            }
            
            if exists:
                results["found"].append(platform)
            elif isinstance(status, int):
                results["not_found"].append(platform)
        except:
            results["platforms"][platform] = {"url": url, "status": "error"}
    
    return results

def email_social_lookup(email):
    """Look up social profiles by email (limited, uses public data)"""
    results = {"email": email, "profiles": []}
    
    # Gravatar
    try:
        import hashlib
        email_hash = hashlib.md5(email.lower().encode()).hexdigest()
        r = requests.get(f"https://www.gravatar.com/{email_hash}.json", timeout=5)
        if r.status_code == 200:
            data = r.json()
            for entry in data.get("entry", []):
                results["profiles"].append({
                    "service": "Gravatar",
                    "display_name": entry.get("displayName"),
                    "photos": [p.get("value") for p in entry.get("photos", [])],
                    "urls": [u.get("value") for u in entry.get("urls", [])]
                })
    except:
        pass
    
    return results

# ============================================================
# DOMAIN/IP SHADOW ATTACK SURFACE
# ============================================================

def attack_surface(domain):
    """Map potential attack surface"""
    results = {"domain": domain, "findings": []}
    
    # Check common subdomains for exposure
    checks = [
        ("admin", ["admin", "portal", "cpanel", "phpmyadmin", "wp-admin"]),
        ("dev", ["dev", "staging", "test", "sandbox", "debug"]),
        ("api", ["api", "graphql", "rest", "v1", "v2", "swagger"]),
        ("cloud", ["s3", "aws", "gcp", "azure", "storage"]),
        ("mail", ["mail", "smtp", "imap", "pop3", "webmail"]),
        ("vpn", ["vpn", "remote", "rdp", "ssh", "bastion"]),
        ("backup", ["backup", "bak", "old", "archive"]),
        ("monitoring", ["monitor", "grafana", "kibana", "prometheus", "nagios"])
    ]
    
    for category, subdomains in checks:
        for sub in subdomains:
            full = f"{sub}.{domain}"
            try:
                answers = dns.resolver.resolve(full, 'A')
                ip = str(answers[0])
                results["findings"].append({
                    "category": category,
                    "subdomain": full,
                    "ip": ip
                })
            except:
                pass
    
    return results

# ============================================================
# INTERACTIVE SHELL
# ============================================================

def interactive():
    """Interactive OSINT shell"""
    print("=" * 60)
    print("  OsintNeoAI Local Bridge v2")
    print(f"  Model: {MODEL}")
    print("=" * 60)
    print("\nCommands:")
    print("  recon <domain>         - Full domain reconnaissance")
    print("  deeprecon <domain>     - Deep recon with full port scan")
    print("  dns <domain>           - DNS enumeration")
    print("  subdomain <domain>     - Subdomain enumeration")
    print("  whois <domain/ip>      - WHOIS lookup")
    print("  port <host>            - Quick port scan")
    print("  deepport <host>        - Full port scan (1-1024+)")
    print("  http <url>             - HTTP header analysis")
    print("  tech <url>             - Technology fingerprint")
    print("  ssl <host>             - SSL certificate check")
    print("  cert <domain>          - Certificate transparency")
    print("  email <email>          - Email OSINT")
    print("  username <user>        - Username OSINT")
    print("  shodan <ip>            - Shodan lookup")
    print("  ip <ip>                - IP information")
    print("  ai <question>          - Ask AI anything")
    print("  analyze <data>         - Analyze data with AI")
    print("  quit                   - Exit")
    print("-" * 60)
    
    while True:
        try:
            cmd = input("\nosint> ").strip()
            if not cmd:
                continue
            
            parts = cmd.split(" ", 1)
            action = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""
            
            if action == "quit":
                break
            elif action == "recon" and arg:
                print(json.dumps(recon(arg), indent=2, default=str))
            elif action == "deeprecon" and arg:
                print(json.dumps(full_recon(arg), indent=2, default=str))
            elif action == "dns" and arg:
                print(json.dumps(dns_full(arg), indent=2))
            elif action == "subdomain" and arg:
                print(json.dumps(subdomain_enum(arg), indent=2))
            elif action == "whois" and arg:
                if '.' in arg and not arg.replace('.','').isdigit():
                    print(json.dumps(whois_domain(arg), indent=2, default=str))
                else:
                    print(json.dumps(whois_ip(arg), indent=2, default=str))
            elif action == "port" and arg:
                print(json.dumps(port_scan(arg), indent=2))
            elif action == "deepport" and arg:
                print(json.dumps(full_port_scan(arg), indent=2))
            elif action == "http" and arg:
                print(json.dumps(http_headers(arg), indent=2))
            elif action == "tech" and arg:
                print(json.dumps(technology_fingerprint(arg), indent=2))
            elif action == "ssl" and arg:
                print(json.dumps(ssl_check(arg), indent=2))
            elif action == "cert" and arg:
                print(json.dumps(cert_transparency(arg), indent=2))
            elif action == "email" and arg:
                print(json.dumps(email_check(arg), indent=2))
            elif action == "username" and arg:
                print(json.dumps(username_check(arg), indent=2))
            elif action == "shodan" and arg:
                print(json.dumps(shodan_lookup(arg), indent=2))
            elif action == "ip" and arg:
                print(json.dumps(ip_info(arg), indent=2))
            elif action == "ai" and arg:
                print(query_ollama(arg))
            elif action == "analyze" and arg:
                print(query_ollama(f"Analyze this data: {arg}"))
            else:
                print("Unknown command or missing argument. Type 'help' for commands.")
        except KeyboardInterrupt:
            print("\n[!] Interrupted")
        except EOFError:
            break

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Command line mode
        cmd = " ".join(sys.argv[1:])
        if cmd.startswith("recon "):
            domain = cmd.split(" ", 1)[1]
            print(json.dumps(recon(domain), indent=2, default=str))
        else:
            print("Usage: python osint_bridge.py recon <domain>")
    else:
        if check_ollama():
            interactive()
        else:
            print("ERROR: Ollama not running on localhost:11434")
            print("Start Ollama first: ollama serve")
