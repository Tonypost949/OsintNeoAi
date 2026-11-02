import os
import socket
import json
import random
import time
import datetime
import requests

from .entities import (
    Entity, Domain, Email, IPAddress, SocialProfile,
    ThreatScore, ServiceInfo, WHOISRecord, SSLCertificate,
    BreachRecord, DNSRecord, GeoLocation, ReputationScore,
    URLScanResult, ASNInfo
)

# ─────────────────────────────────────────────────────────────
# HTTP 429 Rate-Limit Handling — Exponential Backoff
# ─────────────────────────────────────────────────────────────

RETRYABLE_STATUS_CODES = (429, 502, 503, 504)
DEFAULT_MAX_RETRIES = 4            # retries after the initial attempt
DEFAULT_BASE_DELAY = 1.0           # first backoff interval (seconds)
MAX_BACKOFF_DELAY = 60.0           # hard cap per sleep (seconds)
BACKOFF_JITTER = 0.25              # ±25% jitter avoids thundering-herd retries


def _retry_after_delay(response, fallback: float) -> float:
    """Return the server-supplied Retry-After (seconds or HTTP-date), else fallback."""
    header = (getattr(response, "headers", None) or {}).get("Retry-After")
    if not header:
        return fallback
    try:
        return max(0.0, min(float(header), MAX_BACKOFF_DELAY))
    except (TypeError, ValueError):
        pass
    try:
        from email.utils import parsedate_to_datetime
        when = parsedate_to_datetime(header)
        delta = (when - datetime.datetime.now(datetime.timezone.utc)).total_seconds()
        return max(0.0, min(delta, MAX_BACKOFF_DELAY))
    except Exception:
        return fallback


def _backoff_delay(attempt: int, base_delay: float = DEFAULT_BASE_DELAY) -> float:
    """Exponential backoff with jitter: base_delay * 2**attempt, capped at MAX_BACKOFF_DELAY."""
    delay = min(base_delay * (2 ** attempt), MAX_BACKOFF_DELAY)
    jitter = delay * BACKOFF_JITTER
    return max(0.0, delay + random.uniform(-jitter, jitter))


def http_request(method: str, url: str, *,
                 max_retries: int = DEFAULT_MAX_RETRIES,
                 base_delay: float = DEFAULT_BASE_DELAY,
                 **kwargs) -> requests.Response:
    """
    requests.request() wrapper that retries with exponential backoff when the
    server answers HTTP 429 (rate limit) or a transient 502/503/504.

    - Honours an explicit Retry-After header (seconds or HTTP-date).
    - Delay sequence: base_delay * 2**attempt (±25% jitter), capped at 60s.
    - Returns the final response once retries are exhausted so the caller
      can decide how to report the failure.
    """
    kwargs.setdefault("timeout", 10)
    delay = base_delay
    response = None
    for attempt in range(max_retries + 1):
        response = requests.request(method, url, **kwargs)
        if response.status_code not in RETRYABLE_STATUS_CODES or attempt >= max_retries:
            return response
        sleep_for = _retry_after_delay(response, delay)
        host = url.split("/")[2] if "//" in url else url
        print(f"  [!] HTTP {response.status_code} from {host} — "
              f"backoff {attempt + 1}/{max_retries}, retrying in {sleep_for:.1f}s")
        time.sleep(sleep_for)
        delay = _backoff_delay(attempt + 1, base_delay)
    return response


# ─────────────────────────────────────────────────────────────
# Base Transform
# ─────────────────────────────────────────────────────────────

class Transform:
    name = "BaseTransform"
    input_type = Entity
    output_type = Entity

    def run(self, entity: Entity) -> list[Entity]:
        raise NotImplementedError


# ─────────────────────────────────────────────────────────────
# 1. DomainToIP — Real DNS resolution
# ─────────────────────────────────────────────────────────────

class DomainToIP(Transform):
    name = "DomainToIP"

    def run(self, entity: Entity) -> list[Entity]:
        print(f"[*] Resolving DNS for: {entity.value}")
        try:
            ip = socket.gethostbyname(entity.value)
            return [IPAddress(value=ip)]
        except Exception as e:
            print(f"[-] DNS resolution failed: {e}")
            return []


# ─────────────────────────────────────────────────────────────
# 2. EmailToSocialProfile — Username pivot across platforms
# ─────────────────────────────────────────────────────────────

class EmailToSocialProfile(Transform):
    name = "EmailToSocialProfile"

    PLATFORMS = [
        ("Twitter/X",  "https://twitter.com/{u}"),
        ("LinkedIn",   "https://www.linkedin.com/in/{u}"),
        ("GitHub",     "https://github.com/{u}"),
        ("Instagram",  "https://www.instagram.com/{u}"),
        ("Reddit",     "https://www.reddit.com/user/{u}"),
    ]

    def run(self, entity: Entity) -> list[Entity]:
        username = entity.value.split("@")[0]
        print(f"[*] Pivoting on username: {username}")
        results = []
        for platform, url_template in self.PLATFORMS:
            url = url_template.format(u=username)
            try:
                r = http_request("HEAD", url, allow_redirects=True, timeout=5,
                                 headers={"User-Agent": "Mozilla/5.0"})
                if r.status_code == 200:
                    results.append(SocialProfile(value=f"{platform}: {url}"))
                    print(f"  [+] {platform}: ACTIVE")
                else:
                    print(f"  [-] {platform}: {r.status_code}")
            except Exception as e:
                print(f"  [?] {platform}: unreachable ({e})")
        return results


# ─────────────────────────────────────────────────────────────
# 3. IPToShodanInfo — Shodan host lookup
# ─────────────────────────────────────────────────────────────

class IPToShodanInfo(Transform):
    name = "IPToShodanInfo"

    def run(self, entity: Entity) -> list[Entity]:
        print(f"[*] Querying Shodan for: {entity.value}")
        api_key = os.environ.get("SHODAN_API_KEY")
        if not api_key:
            print("[-] SHODAN_API_KEY not set — returning stub data.")
            return [
                ServiceInfo(value="80/tcp: http (stub)"),
                ServiceInfo(value="443/tcp: https (stub)"),
            ]
        try:
            import shodan
            api = shodan.Shodan(api_key)
            # Shodan answers rate limits (HTTP 429) with an APIError — retry
            # with the same exponential backoff used for raw HTTP calls.
            host = None
            for attempt in range(DEFAULT_MAX_RETRIES + 1):
                try:
                    host = api.host(entity.value)
                    break
                except Exception as e:
                    msg = str(e).lower()
                    rate_limited = "429" in msg or "rate limit" in msg
                    if rate_limited and attempt < DEFAULT_MAX_RETRIES:
                        sleep_for = _backoff_delay(attempt)
                        print(f"  [!] Shodan rate limited — backoff "
                              f"{attempt + 1}/{DEFAULT_MAX_RETRIES}, retrying in {sleep_for:.1f}s")
                        time.sleep(sleep_for)
                        continue
                    raise
            results = []
            for item in host.get("data", []):
                port = item.get("port")
                banner = item.get("product", "unknown")
                results.append(ServiceInfo(value=f"{port}/tcp — {banner}"))
            return results
        except Exception as e:
            print(f"[-] Shodan query failed: {e}")
            return []


# ─────────────────────────────────────────────────────────────
# 4. DomainToVirusTotal — VT reputation check
# ─────────────────────────────────────────────────────────────

class DomainToVirusTotal(Transform):
    name = "DomainToVirusTotal"

    def run(self, entity: Entity) -> list[Entity]:
        print(f"[*] Querying VirusTotal for: {entity.value}")
        api_key = os.environ.get("VT_API_KEY")
        if not api_key:
            print("[-] VT_API_KEY not set — returning stub score.")
            return [ThreatScore(value="Score: 2/89 (Low Risk — stub)")]
        try:
            url = f"https://www.virustotal.com/api/v3/domains/{entity.value}"
            r = http_request("GET", url, headers={"x-apikey": api_key}, timeout=10)
            r.raise_for_status()
            stats = r.json()["data"]["attributes"]["last_analysis_stats"]
            malicious = stats.get("malicious", 0)
            total = sum(stats.values())
            return [ThreatScore(value=f"VT Score: {malicious}/{total}")]
        except Exception as e:
            print(f"[-] VirusTotal query failed: {e}")
            return []


# ─────────────────────────────────────────────────────────────
# 5. DomainToWHOIS — WHOIS via RDAP + python-whois fallback
# ─────────────────────────────────────────────────────────────

class DomainToWHOIS(Transform):
    name = "DomainToWHOIS"

    def run(self, entity: Entity) -> list[Entity]:
        domain = entity.value.strip().lower()
        print(f"[*] WHOIS lookup for: {domain}")
        results = []

        # Strategy 1: RDAP
        try:
            r = http_request("GET", f"https://rdap.org/domain/{domain}", timeout=10,
                             headers={"Accept": "application/json"})
            if r.status_code == 200:
                data = r.json()
                registrar = ""
                for ei in data.get("entities", []):
                    if "registrar" in ei.get("roles", []):
                        vcard = ei.get("vcardArray", [])
                        if len(vcard) > 1:
                            for field in vcard[1]:
                                if field[0] == "fn":
                                    registrar = field[3]
                                    break
                        if not registrar:
                            registrar = ei.get("handle", "")
                events = {e["eventAction"]: e["eventDate"] for e in data.get("events", [])}
                registered = events.get("registration", "unknown")[:10]
                expires    = events.get("expiration",   "unknown")[:10]
                updated    = events.get("last changed", events.get("last update", "unknown"))
                if updated != "unknown":
                    updated = updated[:10]
                status = ", ".join(data.get("status", [])) or "unknown"
                nameservers = ", ".join(ns.get("ldhName", "") for ns in data.get("nameservers", [])) or "unknown"
                results += [
                    WHOISRecord(value=f"Registrar: {registrar or 'unknown'}"),
                    WHOISRecord(value=f"Registered: {registered}"),
                    WHOISRecord(value=f"Expires: {expires}"),
                    WHOISRecord(value=f"Updated: {updated}"),
                    WHOISRecord(value=f"Status: {status}"),
                    WHOISRecord(value=f"Nameservers: {nameservers}"),
                ]
                print(f"  [+] RDAP success — {len(results)} fields.")
                return results
        except Exception as e:
            print(f"  [!] RDAP failed: {e} — falling back to python-whois")

        # Strategy 2: python-whois
        try:
            import whois as pywhois
            w = pywhois.whois(domain)
            def _fmt(v):
                if isinstance(v, list): v = v[0]
                return str(v)[:80] if v else "unknown"
            results += [
                WHOISRecord(value=f"Registrar: {_fmt(w.registrar)}"),
                WHOISRecord(value=f"Registered: {_fmt(w.creation_date)}"),
                WHOISRecord(value=f"Expires: {_fmt(w.expiration_date)}"),
                WHOISRecord(value=f"Updated: {_fmt(w.updated_date)}"),
                WHOISRecord(value=f"Org: {_fmt(w.org)}"),
                WHOISRecord(value=f"Country: {_fmt(w.country)}"),
            ]
            if w.name_servers:
                results.append(WHOISRecord(value=f"Nameservers: {', '.join(list(w.name_servers)[:4])}"))
            print(f"  [+] python-whois success — {len(results)} fields.")
        except ImportError:
            results.append(WHOISRecord(value="Install python-whois: pip install python-whois"))
        except Exception as e:
            print(f"  [-] python-whois failed: {e}")
            if not results:
                results.append(WHOISRecord(value=f"WHOIS lookup failed: {e}"))
        return results


# ─────────────────────────────────────────────────────────────
# 6. DomainToSSLCert — TLS certificate introspection
# ─────────────────────────────────────────────────────────────

class DomainToSSLCert(Transform):
    name = "DomainToSSLCert"

    def run(self, entity: Entity) -> list[Entity]:
        import ssl, datetime
        hostname = entity.value.strip().lower()
        print(f"[*] Fetching SSL/TLS cert for: {hostname}")
        results = []

        # Strategy 1: direct TLS handshake
        try:
            ctx = ssl.create_default_context()
            with ctx.wrap_socket(
                socket.socket(socket.AF_INET, socket.SOCK_STREAM),
                server_hostname=hostname
            ) as conn:
                conn.settimeout(8)
                conn.connect((hostname, 443))
                cert = conn.getpeercert()
            subj  = dict(x[0] for x in cert.get("subject", []))
            issr  = dict(x[0] for x in cert.get("issuer",  []))
            cn     = subj.get("commonName", "unknown")
            org    = subj.get("organizationName", "unknown")
            issuer = issr.get("organizationName", issr.get("commonName", "unknown"))
            not_before = cert.get("notBefore", "unknown")
            not_after  = cert.get("notAfter",  "unknown")
            try:
                exp = datetime.datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
                days_left = (exp - datetime.datetime.utcnow()).days
                expiry_str = f"{not_after} ({days_left}d remaining)"
            except Exception:
                expiry_str = not_after
            san_list = [v for t, v in cert.get("subjectAltName", []) if t == "DNS"]
            results += [
                SSLCertificate(value=f"CN: {cn}"),
                SSLCertificate(value=f"Org: {org}"),
                SSLCertificate(value=f"Issuer: {issuer}"),
                SSLCertificate(value=f"Valid From: {not_before}"),
                SSLCertificate(value=f"Expires: {expiry_str}"),
            ]
            if san_list:
                results.append(SSLCertificate(value=f"SANs ({len(san_list)}): {', '.join(san_list[:8])}"))
            print(f"  [+] Direct TLS handshake success.")
            return results
        except Exception as e:
            print(f"  [!] Direct TLS failed: {e} — trying crt.sh")

        # Strategy 2: crt.sh
        try:
            r = http_request("GET", f"https://crt.sh/?q={hostname}&output=json", timeout=10)
            seen = set()
            for c in r.json()[:20]:
                name = c.get("name_value", "").strip()
                issuer = c.get("issuer_name", "").strip()
                not_after = c.get("not_after", "")[:10]
                key = f"{name}|{not_after}"
                if key not in seen:
                    seen.add(key)
                    results.append(SSLCertificate(
                        value=f"[crt.sh] CN:{name} | Expires:{not_after} | Issuer:{issuer[:60]}"
                    ))
            print(f"  [+] crt.sh: {len(results)} records.")
        except Exception as e:
            results.append(SSLCertificate(value=f"SSL lookup failed: {e}"))
        return results


# ─────────────────────────────────────────────────────────────
# 7. EmailToHIBP — HaveIBeenPwned breach check
# ─────────────────────────────────────────────────────────────

class EmailToHIBP(Transform):
    name = "EmailToHIBP"

    def run(self, entity: Entity) -> list[Entity]:
        email = entity.value.strip()
        print(f"[*] Checking HaveIBeenPwned for: {email}")
        results = []
        api_key = os.environ.get("HIBP_API_KEY")
        headers = {"User-Agent": "OSINTNeoAi-CLI/1.0", "hibp-api-key": api_key or ""}
        try:
            url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}?truncateResponse=false"
            r = http_request("GET", url, headers=headers, timeout=10)
            if r.status_code == 200:
                breaches = r.json()
                print(f"  [!] FOUND in {len(breaches)} breach(es)!")
                for b in breaches:
                    name = b.get("Name", "Unknown")
                    date = b.get("BreachDate", "?")
                    count = b.get("PwnCount", 0)
                    data_classes = ", ".join(b.get("DataClasses", [])[:5])
                    results.append(BreachRecord(
                        value=f"[BREACH] {name} ({date}) | {count:,} accounts | Data: {data_classes}"
                    ))
            elif r.status_code == 404:
                results.append(BreachRecord(value=f"[CLEAN] {email} — not in HIBP"))
            elif r.status_code == 401:
                results.append(BreachRecord(value="Set HIBP_API_KEY env var (https://haveibeenpwned.com/API/Key)"))
            elif r.status_code == 429:
                results.append(BreachRecord(
                    value=f"HIBP still rate limited after {DEFAULT_MAX_RETRIES} backoff retries — wait 60s and re-run"
                ))
            else:
                results.append(BreachRecord(value=f"HIBP HTTP {r.status_code}"))
        except Exception as e:
            results.append(BreachRecord(value=f"HIBP failed: {e}"))

        # k-Anonymity connectivity check
        try:
            import hashlib
            prefix = hashlib.sha1(b"password").hexdigest().upper()[:5]
            pr = http_request("GET", f"https://api.pwnedpasswords.com/range/{prefix}", timeout=5)
            if pr.status_code == 200:
                results.append(BreachRecord(value="[INFO] HIBP Password API: k-Anonymity endpoint reachable"))
        except Exception:
            pass
        return results


# ─────────────────────────────────────────────────────────────
# 8. DomainToDNS — Full DNS record dump
# ─────────────────────────────────────────────────────────────

class DomainToDNS(Transform):
    name = "DomainToDNS"
    RECORD_TYPES = ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA"]

    def run(self, entity: Entity) -> list[Entity]:
        domain = entity.value.strip().lower()
        print(f"[*] DNS enum for: {domain}")
        results = []

        # Strategy 1: Google DNS over HTTPS
        try:
            for rtype in self.RECORD_TYPES:
                try:
                    r = http_request(
                        "GET",
                        f"https://dns.google/resolve?name={domain}&type={rtype}",
                        timeout=6
                    )
                    if r.status_code == 200:
                        for ans in r.json().get("Answer", []):
                            rdata = ans.get("data", "").strip()
                            if rdata:
                                results.append(DNSRecord(value=f"{rtype}: {rdata}"))
                                print(f"  [+] {rtype}: {rdata[:80]}")
                except Exception:
                    pass
            if results:
                return results
        except Exception as e:
            print(f"  [!] Google DoH failed: {e}")

        # Strategy 2: socket A record
        try:
            ip = socket.gethostbyname(domain)
            results.append(DNSRecord(value=f"A: {ip}"))
        except Exception as e:
            results.append(DNSRecord(value=f"DNS failed: {e}"))
        return results


# ─────────────────────────────────────────────────────────────
# 9. IPToGeoLocation — Geolocation + ASN lookup
# ─────────────────────────────────────────────────────────────

class IPToGeoLocation(Transform):
    name = "IPToGeoLocation"

    def run(self, entity: Entity) -> list[Entity]:
        ip = entity.value.strip()
        print(f"[*] Geolocating IP: {ip}")
        results = []

        # ip-api.com (free)
        try:
            r = http_request(
                "GET",
                f"http://ip-api.com/json/{ip}?fields=status,message,country,regionName,city,zip,lat,lon,isp,org,as",
                timeout=8
            )
            data = r.json()
            if data.get("status") == "success":
                results += [
                    GeoLocation(value=f"Location: {data.get('city','?')}, {data.get('regionName','?')}, {data.get('country','?')} {data.get('zip','')}"),
                    GeoLocation(value=f"Coordinates: {data.get('lat','?')}, {data.get('lon','?')}"),
                    GeoLocation(value=f"ISP: {data.get('isp','?')}"),
                    GeoLocation(value=f"Org: {data.get('org','?')}"),
                    GeoLocation(value=f"ASN: {data.get('as','?')}"),
                ]
                print(f"  [+] ip-api.com: {data.get('city')}, {data.get('country')} | {data.get('isp')}")
                return results
            else:
                print(f"  [!] ip-api: {data.get('message')} — trying ipinfo.io")
        except Exception as e:
            print(f"  [!] ip-api.com failed: {e} — trying ipinfo.io")

        # ipinfo.io fallback
        try:
            token = os.environ.get("IPINFO_TOKEN", "")
            r = http_request(
                "GET",
                f"https://ipinfo.io/{ip}/json",
                params={"token": token} if token else {},
                timeout=8
            )
            data = r.json()
            loc = data.get("loc", "?,?").split(",")
            results.append(GeoLocation(value=f"Location: {data.get('city','?')}, {data.get('region','?')}, {data.get('country','?')}"))
            if len(loc) == 2:
                results.append(GeoLocation(value=f"Coordinates: {loc[0]}, {loc[1]}"))
            results.append(GeoLocation(value=f"Org/ASN: {data.get('org','?')}"))
            print(f"  [+] ipinfo.io success")
        except Exception as e:
            results.append(GeoLocation(value=f"GeoIP failed: {e}"))
        return results


# ─────────────────────────────────────────────────────────────
# 10. DomainToReputation — Multi-source reputation check
# ─────────────────────────────────────────────────────────────

class DomainToReputation(Transform):
    name = "DomainToReputation"

    def run(self, entity: Entity) -> list[Entity]:
        domain = entity.value.strip().lower()
        print(f"[*] Reputation check for: {domain}")
        results = []

        # Google Safe Browsing
        gsb_key = os.environ.get("GSB_API_KEY")
        if gsb_key:
            try:
                payload = {
                    "client": {"clientId": "osintneoai", "clientVersion": "1.0"},
                    "threatInfo": {
                        "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
                        "platformTypes": ["ANY_PLATFORM"],
                        "threatEntryTypes": ["URL"],
                        "threatEntries": [{"url": f"http://{domain}"}]
                    }
                }
                r = http_request(
                    "POST",
                    f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={gsb_key}",
                    json=payload, timeout=8
                )
                if r.status_code == 429:
                    # Backoff exhausted — never report a false "Clean" on a rate limit.
                    results.append(ReputationScore(value="[GSB] Rate limited after backoff — retry later"))
                else:
                    data = r.json()
                    if data.get("matches"):
                        for m in data["matches"]:
                            results.append(ReputationScore(
                                value=f"[GSB] THREAT: {m.get('threatType')} — {m.get('platformType')}"
                            ))
                    else:
                        results.append(ReputationScore(value="[GSB] Clean"))
                    print(f"  [+] Google Safe Browsing checked.")
            except Exception as e:
                print(f"  [-] GSB failed: {e}")
        else:
            results.append(ReputationScore(value="[GSB] Set GSB_API_KEY for Google Safe Browsing"))

        # URLHaus (no key)
        try:
            r = http_request("POST", "https://urlhaus-api.abuse.ch/v1/host/",
                             data={"host": domain}, timeout=8)
            data = r.json()
            qs = data.get("query_status", "")
            if qs == "is_host":
                results.append(ReputationScore(
                    value=f"[URLHaus] FLAGGED — {data.get('urls_count', 0)} malicious URL(s)"
                ))
                for u in data.get("urls", [])[:3]:
                    results.append(ReputationScore(
                        value=f"  [{u.get('url_status','?')}] {u.get('url','')} — {u.get('threat','?')}"
                    ))
            elif qs == "no_results":
                results.append(ReputationScore(value="[URLHaus] Clean"))
            else:
                results.append(ReputationScore(value=f"[URLHaus] {qs}"))
            print(f"  [+] URLHaus: {qs}")
        except Exception as e:
            print(f"  [-] URLHaus failed: {e}")

        # AbuseIPDB
        aipdb_key = os.environ.get("ABUSEIPDB_KEY")
        if aipdb_key:
            try:
                ip = socket.gethostbyname(domain)
                r = http_request(
                    "GET",
                    "https://api.abuseipdb.com/api/v2/check",
                    headers={"Key": aipdb_key, "Accept": "application/json"},
                    params={"ipAddress": ip, "maxAgeInDays": 90},
                    timeout=8
                )
                data = r.json().get("data", {})
                score = data.get("abuseConfidenceScore", 0)
                reports = data.get("totalReports", 0)
                results.append(ReputationScore(
                    value=f"[AbuseIPDB] {ip} — Score: {score}% | Reports: {reports}"
                ))
                print(f"  [+] AbuseIPDB: {ip} score={score}%")
            except Exception as e:
                print(f"  [-] AbuseIPDB failed: {e}")

        return results


# ─────────────────────────────────────────────────────────────
# 11. WebSearch — Real multi-engine web search
#     Priority: DDGS.text() → Bing scrape → Brave API → Google CSE
# ─────────────────────────────────────────────────────────────

class WebSearch(Transform):
    name = "WebSearch"
    MAX_RESULTS = 10
    _HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }

    def run(self, entity: Entity) -> list[Entity]:
        query = entity.value.strip()
        print(f'[*] Web search: "{query}"')

        results = (
            self._search_ddgs(query)
            or self._search_bing(query)
            or self._search_brave(query)
            or self._search_google_cse(query)
        )

        if results:
            print(f"  [+] {len(results)} result(s) returned.")
        else:
            encoded = requests.utils.quote(query)
            results = [URLScanResult(
                value=f"[WebSearch] All engines failed — manual: https://duckduckgo.com/?q={encoded}"
            )]
            print("  [-] All search engines failed.")

        return results

    # ── Engine 1: duckduckgo-search library (real results, no key) ──
    def _search_ddgs(self, query: str) -> list:
        try:
            from duckduckgo_search import DDGS
            results = []
            with DDGS() as ddgs:
                hits = list(ddgs.text(query, max_results=self.MAX_RESULTS))
            for h in hits:
                title = h.get("title", "").strip()
                href  = h.get("href",  "").strip()
                body  = h.get("body",  "").strip()[:200]
                results.append(URLScanResult(value=f"[DDG] {title} | {href} | {body}"))
            if results:
                print(f"  [+] DDGS: {len(results)} hit(s).")
            return results
        except ImportError:
            print("  [!] duckduckgo-search not installed — run: pip install duckduckgo-search")
            return []
        except Exception as e:
            print(f"  [!] DDGS failed: {e}")
            return []

    # ── Engine 2: Bing Search API v7 (Azure) or HTML scrape fallback ──
    def _search_bing(self, query: str) -> list:
        api_key = os.environ.get("BING_SEARCH_API_KEY", "")

        # Prefer the proper API when key is set
        if api_key:
            try:
                encoded = requests.utils.quote(query)
                r = http_request(
                    "GET",
                    "https://api.bing.microsoft.com/v7.0/search",
                    params={"q": query, "count": self.MAX_RESULTS, "mkt": "en-US"},
                    headers={"Ocp-Apim-Subscription-Key": api_key},
                    timeout=10
                )
                r.raise_for_status()
                results = []
                for item in r.json().get("webPages", {}).get("value", []):
                    title   = item.get("name",    "").strip()
                    href    = item.get("url",     "").strip()
                    snippet = item.get("snippet", "").strip()[:200]
                    results.append(URLScanResult(value=f"[Bing] {title} | {href} | {snippet}"))
                if results:
                    print(f"  [+] Bing API: {len(results)} hit(s).")
                return results
            except Exception as e:
                print(f"  [!] Bing API failed: {e} — falling back to scrape")

        # Scrape fallback (no key needed)
        try:
            from bs4 import BeautifulSoup
            encoded = requests.utils.quote(query)
            url = f"https://www.bing.com/search?q={encoded}&count={self.MAX_RESULTS}&setlang=en"
            r = http_request("GET", url, headers=self._HEADERS, timeout=10)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            results = []
            for li in soup.select("li.b_algo")[:self.MAX_RESULTS]:
                h2   = li.find("h2")
                a    = h2.find("a") if h2 else None
                cite = li.find("cite")   # contains the real clean URL
                p    = li.find("p")
                if a:
                    title   = a.get_text(strip=True)
                    # cite tag has the real URL; fall back to href only if missing
                    href = cite.get_text(strip=True) if cite else a.get("href", "")
                    snippet = p.get_text(strip=True)[:200] if p else ""
                    results.append(URLScanResult(value=f"[Bing] {title} | {href} | {snippet}"))
            if results:
                print(f"  [+] Bing scrape: {len(results)} hit(s).")
            return results
        except Exception as e:
            print(f"  [!] Bing scrape failed: {e}")
            return []


    # ── Engine 3: Brave Search API (free tier key, optional) ──
    def _search_brave(self, query: str) -> list:
        api_key = os.environ.get("BRAVE_SEARCH_API_KEY", "")
        if not api_key:
            return []
        try:
            r = http_request(
                "GET",
                "https://api.search.brave.com/res/v1/web/search",
                params={"q": query, "count": self.MAX_RESULTS},
                headers={**self._HEADERS, "Accept": "application/json",
                         "Accept-Encoding": "gzip", "X-Subscription-Token": api_key},
                timeout=10
            )
            r.raise_for_status()
            results = []
            for item in r.json().get("web", {}).get("results", []):
                title   = item.get("title",       "").strip()
                url_    = item.get("url",          "").strip()
                snippet = item.get("description", "").strip()[:200]
                results.append(URLScanResult(value=f"[Brave] {title} | {url_} | {snippet}"))
            if results:
                print(f"  [+] Brave API: {len(results)} hit(s).")
            return results
        except Exception as e:
            print(f"  [!] Brave Search failed: {e}")
            return []

    # ── Engine 4: Google Custom Search (GOOGLE_CSE_API_KEY + GOOGLE_CSE_ID) ──
    def _search_google_cse(self, query: str) -> list:
        api_key = os.environ.get("GOOGLE_CSE_API_KEY", "")
        cx      = os.environ.get("GOOGLE_CSE_ID", "")
        if not api_key or not cx:
            return []
        try:
            r = http_request(
                "GET",
                "https://www.googleapis.com/customsearch/v1",
                params={"q": query, "key": api_key, "cx": cx, "num": min(self.MAX_RESULTS, 10)},
                timeout=10
            )
            r.raise_for_status()
            results = []
            for item in r.json().get("items", []):
                title   = item.get("title",   "").strip()
                link    = item.get("link",    "").strip()
                snippet = item.get("snippet", "").strip()[:200].replace("\n", " ")
                results.append(URLScanResult(value=f"[Google] {title} | {link} | {snippet}"))
            if results:
                print(f"  [+] Google CSE: {len(results)} hit(s).")
            return results
        except Exception as e:
            print(f"  [!] Google CSE failed: {e}")
            return []


# ─────────────────────────────────────────────────────────────
# Transform Registry
# ─────────────────────────────────────────────────────────────

AVAILABLE_TRANSFORMS = {
    "DomainToIP":           DomainToIP(),
    "EmailToSocialProfile": EmailToSocialProfile(),
    "IPToShodanInfo":       IPToShodanInfo(),
    "DomainToVirusTotal":   DomainToVirusTotal(),
    "DomainToWHOIS":        DomainToWHOIS(),
    "DomainToSSLCert":      DomainToSSLCert(),
    "EmailToHIBP":          EmailToHIBP(),
    "DomainToDNS":          DomainToDNS(),
    "IPToGeoLocation":      IPToGeoLocation(),
    "DomainToReputation":   DomainToReputation(),
    "WebSearch":            WebSearch(),
}

# Case-insensitive alias lookup
_ALIAS_MAP = {k.lower(): v for k, v in AVAILABLE_TRANSFORMS.items()}

def get_transform(name: str) -> Transform | None:
    """Resolve a transform by exact or case-insensitive name."""
    return AVAILABLE_TRANSFORMS.get(name) or _ALIAS_MAP.get(name.lower())
