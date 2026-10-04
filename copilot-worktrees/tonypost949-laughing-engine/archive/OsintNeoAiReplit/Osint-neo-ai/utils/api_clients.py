import os
import requests
import json
from datetime import datetime

TIMEOUT = 15

# ═══════════════════════════════════════════════════════════
# IP GEOLOCATION
# ═══════════════════════════════════════════════════════════

def ipinfo_lookup(ip):
    """Lookup IP using ipinfo.io (free tier: 50K/month, no key needed)."""
    key = os.environ.get("IPINFO_API_KEY")
    try:
        url = f"https://ipinfo.io/{ip}/json"
        if key:
            url += f"?token={key}"
        r = requests.get(url, timeout=TIMEOUT)
        if r.status_code == 200:
            d = r.json()
            return {
                "ip": d.get("ip"),
                "city": d.get("city"),
                "region": d.get("region"),
                "country": d.get("country"),
                "loc": d.get("loc"),
                "org": d.get("org"),
                "postal": d.get("postal"),
                "timezone": d.get("timezone"),
                "asn": d.get("asn"),
                "company": d.get("company"),
            }
    except Exception as e:
        return {"error": str(e)}
    return None


# ═══════════════════════════════════════════════════════════
# SHODAN
# ═══════════════════════════════════════════════════════════

def shodan_lookup(ip):
    """Lookup IP using Shodan API."""
    key = os.environ.get("SHODAN_API_KEY")
    if not key:
        return None
    try:
        r = requests.get(f"https://api.shodan.io/shodan/host/{ip}?key={key}", timeout=TIMEOUT)
        if r.status_code == 200:
            d = r.json()
            return {
                "ip": d.get("ip_str"),
                "ports": d.get("ports", []),
                "hostnames": d.get("hostnames", []),
                "os": d.get("os"),
                "isp": d.get("isp"),
                "org": d.get("org"),
                "asn": d.get("asn"),
                "vulns": list(d.get("vulns", {}).keys())[:10],
                "tags": d.get("tags", []),
                "last_update": d.get("last_update"),
            }
    except Exception as e:
        return {"error": str(e)}
    return None


def shodan_search(query):
    """Search Shodan for query."""
    key = os.environ.get("SHODAN_API_KEY")
    if not key:
        return None
    try:
        r = requests.get(
            f"https://api.shodan.io/shodan/host/search?key={key}&query={requests.utils.quote(query)}",
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            d = r.json()
            return {
                "total": d.get("total"),
                "matches": [
                    {
                        "ip": m.get("ip_str"),
                        "port": m.get("port"),
                        "hostnames": m.get("hostnames"),
                        "org": m.get("org"),
                        "isp": m.get("isp"),
                        "location": m.get("location", {}),
                    }
                    for m in d.get("matches", [])[:10]
                ],
            }
    except Exception as e:
        return {"error": str(e)}
    return None


# ═══════════════════════════════════════════════════════════
# ABUSE IPDB
# ═══════════════════════════════════════════════════════════

def abuseipdb_check(ip):
    """Check IP reputation on AbuseIPDB."""
    key = os.environ.get("ABUSEIPDB_API_KEY")
    if not key:
        return None
    try:
        r = requests.get(
            "https://api.abuseipdb.com/api/v2/check",
            headers={"Key": key, "Accept": "application/json"},
            params={"ipAddress": ip, "maxAgeInDays": 90, "verbose": True},
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            d = r.json().get("data", {})
            return {
                "ip": d.get("ipAddress"),
                "abuse_confidence": d.get("abuseConfidenceScore", 0),
                "country": d.get("countryCode"),
                "isp": d.get("isp"),
                "domain": d.get("domain"),
                "total_reports": d.get("totalReports", 0),
                "last_reported": d.get("lastReportedAt"),
                "usage_type": d.get("usageType"),
            }
    except Exception as e:
        return {"error": str(e)}
    return None


# ═══════════════════════════════════════════════════════════
# VIRUSTOTAL
# ═══════════════════════════════════════════════════════════

def virustotal_ip(ip):
    """Check IP on VirusTotal."""
    key = os.environ.get("VIRUSTOTAL_API_KEY")
    if not key:
        return None
    try:
        r = requests.get(
            f"https://www.virustotal.com/api/v3/ip_addresses/{ip}",
            headers={"x-apikey": key},
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            d = r.json().get("data", {}).get("attributes", {})
            stats = d.get("last_analysis_stats", {})
            return {
                "ip": ip,
                "malicious": stats.get("malicious", 0),
                "suspicious": stats.get("suspicious", 0),
                "harmless": stats.get("harmless", 0),
                "undetected": stats.get("undetected", 0),
                "reputation": d.get("reputation", 0),
                "country": d.get("country"),
                "asn": d.get("asn"),
                "as_owner": d.get("as_owner"),
                "last_analysis_date": d.get("last_analysis_date"),
            }
    except Exception as e:
        return {"error": str(e)}
    return None


def virustotal_domain(domain):
    """Check domain on VirusTotal."""
    key = os.environ.get("VIRUSTOTAL_API_KEY")
    if not key:
        return None
    try:
        r = requests.get(
            f"https://www.virustotal.com/api/v3/domains/{domain}",
            headers={"x-apikey": key},
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            d = r.json().get("data", {}).get("attributes", {})
            stats = d.get("last_analysis_stats", {})
            return {
                "domain": domain,
                "malicious": stats.get("malicious", 0),
                "suspicious": stats.get("suspicious", 0),
                "harmless": stats.get("harmless", 0),
                "undetected": stats.get("undetected", 0),
                "reputation": d.get("reputation", 0),
                "creation_date": d.get("creation_date"),
                "registrar": d.get("registrar"),
                "last_analysis_date": d.get("last_analysis_date"),
            }
    except Exception as e:
        return {"error": str(e)}
    return None


# ═══════════════════════════════════════════════════════════
# PHONE LOOKUP
# ═══════════════════════════════════════════════════════════

def numverify_lookup(phone):
    """Lookup phone using NumVerify."""
    key = os.environ.get("NUMVERIFY_API_KEY")
    if not key:
        return None
    try:
        r = requests.get(
            f"http://apilayer.net/api/validate?access_key={key}&number={phone}&format=1",
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            d = r.json()
            return {
                "valid": d.get("valid"),
                "number": d.get("number"),
                "local_format": d.get("local_format"),
                "intl_format": d.get("international_format"),
                "country_code": d.get("country_code"),
                "country": d.get("country_name"),
                "location": d.get("location"),
                "carrier": d.get("carrier"),
                "line_type": d.get("line_type"),
            }
    except Exception as e:
        return {"error": str(e)}
    return None


# ═══════════════════════════════════════════════════════════
# GITHUB
# ═══════════════════════════════════════════════════════════

def github_user(username):
    """Get GitHub user profile."""
    key = os.environ.get("GITHUB_TOKEN")
    headers = {}
    if key:
        headers["Authorization"] = f"token {key}"
    try:
        r = requests.get(f"https://api.github.com/users/{username}", headers=headers, timeout=TIMEOUT)
        if r.status_code == 200:
            d = r.json()
            return {
                "username": d.get("login"),
                "profile_url": d.get("html_url"),
                "found": True,
                "followers": d.get("followers", 0),
                "following": d.get("following", 0),
                "repos": d.get("public_repos", 0),
                "gists": d.get("public_gists", 0),
                "bio": d.get("bio") or "",
                "location": d.get("location") or "Not disclosed",
                "company": d.get("company") or "",
                "blog": d.get("blog") or "",
                "created_at": d.get("created_at"),
                "updated_at": d.get("updated_at"),
                "avatar": d.get("avatar_url"),
                "type": d.get("type"),
            }
        elif r.status_code == 404:
            return {"found": False, "username": username}
    except Exception as e:
        return {"error": str(e)}
    return None


def github_repos(username):
    """Get GitHub user repos (top 10)."""
    key = os.environ.get("GITHUB_TOKEN")
    headers = {}
    if key:
        headers["Authorization"] = f"token {key}"
    try:
        r = requests.get(f"https://api.github.com/users/{username}/repos?sort=updated&per_page=10", headers=headers, timeout=TIMEOUT)
        if r.status_code == 200:
            return [
                {
                    "name": repo.get("name"),
                    "url": repo.get("html_url"),
                    "stars": repo.get("stargazers_count", 0),
                    "forks": repo.get("forks_count", 0),
                    "language": repo.get("language") or "Unknown",
                    "updated": repo.get("updated_at"),
                    "private": repo.get("private"),
                    "description": repo.get("description") or "",
                }
                for repo in r.json()
            ]
    except Exception as e:
        return {"error": str(e)}
    return None


# ═══════════════════════════════════════════════════════════
# REDDIT
# ═══════════════════════════════════════════════════════════

def reddit_user(username):
    """Get Reddit user profile (no auth needed for public)."""
    try:
        r = requests.get(
            f"https://www.reddit.com/user/{username}/about.json",
            headers={"User-Agent": "OSINTAI-Neo/1.0"},
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            d = r.json().get("data", {})
            return {
                "username": username,
                "found": True,
                "karma": d.get("total_karma", 0),
                "link_karma": d.get("link_karma", 0),
                "comment_karma": d.get("comment_karma", 0),
                "created_utc": d.get("created_utc"),
                "is_gold": d.get("is_gold", False),
                "is_mod": d.get("is_mod", False),
                "profile_url": f"https://reddit.com/u/{username}",
            }
        elif r.status_code == 404:
            return {"found": False, "username": username}
    except Exception as e:
        return {"error": str(e)}
    return None


# ═══════════════════════════════════════════════════════════
# TWITTER / X
# ═══════════════════════════════════════════════════════════

def twitter_user(username):
    """Get Twitter user via API v2."""
    key = os.environ.get("TWITTER_BEARER_TOKEN")
    if not key:
        return None
    try:
        r = requests.get(
            f"https://api.twitter.com/2/users/by/username/{username}",
            headers={"Authorization": f"Bearer {key}"},
            params={"user.fields": "created_at,public_metrics,description,location,verified"},
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            d = r.json().get("data", {})
            metrics = d.get("public_metrics", {})
            return {
                "username": d.get("username"),
                "found": True,
                "followers": metrics.get("followers_count", 0),
                "following": metrics.get("following_count", 0),
                "tweets": metrics.get("tweet_count", 0),
                "listed": metrics.get("listed_count", 0),
                "bio": d.get("description") or "",
                "location": d.get("location") or "Not disclosed",
                "verified": d.get("verified", False),
                "created_at": d.get("created_at"),
                "profile_url": f"https://twitter.com/{username}",
            }
        elif r.status_code == 404:
            return {"found": False, "username": username}
    except Exception as e:
        return {"error": str(e)}
    return None


# ═══════════════════════════════════════════════════════════
# GOOGLE NLP
# ═══════════════════════════════════════════════════════════

def google_nlp_analyze(text):
    """Analyze text using Google Cloud NLP API."""
    key = os.environ.get("GOOGLE_API_KEY")
    if not key:
        return None
    try:
        r = requests.post(
            f"https://language.googleapis.com/v1/documents:analyzeEntities?key={key}",
            json={
                "document": {"type": "PLAIN_TEXT", "content": text},
                "encodingType": "UTF8",
            },
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            d = r.json()
            entities = []
            for e in d.get("entities", []):
                entities.append({
                    "name": e.get("name"),
                    "type": e.get("type"),
                    "salience": e.get("salience"),
                    "metadata": e.get("metadata", {}),
                })
            return {"entities": entities}
    except Exception as e:
        return {"error": str(e)}
    return None


# ═══════════════════════════════════════════════════════════
# THREAT AGGREGATION
# ═══════════════════════════════════════════════════════════

def aggregate_ip_intel(ip):
    """Run all available IP intelligence APIs and merge results."""
    intel = {
        "target": ip,
        "type": "IP Address",
        "scanned_at": datetime.now().isoformat(),
        "sources": [],
    }

    info = ipinfo_lookup(ip)
    if info and "error" not in info:
        intel["sources"].append("ipinfo")
        intel["city"] = info.get("city", "Unknown")
        intel["region"] = info.get("region", "Unknown")
        intel["country"] = info.get("country", "Unknown")
        intel["org"] = info.get("org", "Unknown")
        intel["loc"] = info.get("loc")
        intel["postal"] = info.get("postal")
        intel["timezone"] = info.get("timezone")

    shodan = shodan_lookup(ip)
    if shodan and "error" not in shodan:
        intel["sources"].append("shodan")
        intel["ports"] = shodan.get("ports", [])
        intel["hostnames"] = shodan.get("hostnames", [])
        intel["os"] = shodan.get("os")
        intel["isp"] = shodan.get("isp", intel.get("isp", "Unknown"))
        intel["org"] = shodan.get("org", intel.get("org", "Unknown"))
        intel["asn"] = shodan.get("asn")
        intel["vulns"] = shodan.get("vulns", [])
        intel["tags"] = shodan.get("tags", [])

    abuse = abuseipdb_check(ip)
    if abuse and "error" not in abuse:
        intel["sources"].append("abuseipdb")
        intel["abuse_confidence"] = abuse.get("abuse_confidence", 0)
        intel["total_reports"] = abuse.get("total_reports", 0)
        intel["usage_type"] = abuse.get("usage_type")
        intel["last_reported"] = abuse.get("last_reported")

    vt = virustotal_ip(ip)
    if vt and "error" not in vt:
        intel["sources"].append("virustotal")
        intel["vt_malicious"] = vt.get("malicious", 0)
        intel["vt_suspicious"] = vt.get("suspicious", 0)
        intel["vt_harmless"] = vt.get("harmless", 0)
        intel["vt_reputation"] = vt.get("reputation", 0)
        intel["vt_as_owner"] = vt.get("as_owner")

    if not intel["sources"]:
        intel["note"] = "No API keys configured. Add keys in Replit Secrets for live intelligence."
    else:
        intel["note"] = f"Intelligence from {len(intel['sources'])} source(s): {', '.join(intel['sources'])}"

    return intel


def aggregate_domain_intel(domain):
    """Run all available domain intelligence APIs."""
    intel = {
        "target": domain,
        "type": "Domain",
        "scanned_at": datetime.now().isoformat(),
        "sources": [],
    }

    try:
        import socket
        ip = socket.gethostbyname(domain)
        intel["resolved_ip"] = ip
        intel["dns_a_records"] = [ip]
    except Exception:
        pass

    try:
        import whois
        w = whois.whois(domain)
        intel["whois_registrar"] = str(w.registrar) if w.registrar else "N/A"
        intel["whois_created"] = str(w.creation_date) if w.creation_date else "N/A"
        intel["whois_expires"] = str(w.expiration_date) if w.expiration_date else "N/A"
        if w.name_servers:
            intel["name_servers"] = [str(ns) for ns in w.name_servers[:4]]
        if w.emails:
            intel["contact_emails"] = [str(e) for e in (w.emails if isinstance(w.emails, list) else [w.emails])]
    except Exception:
        pass

    vt = virustotal_domain(domain)
    if vt and "error" not in vt:
        intel["sources"].append("virustotal")
        intel["vt_malicious"] = vt.get("malicious", 0)
        intel["vt_suspicious"] = vt.get("suspicious", 0)
        intel["vt_reputation"] = vt.get("reputation", 0)
        intel["vt_registrar"] = vt.get("registrar")
        intel["vt_creation_date"] = vt.get("creation_date")

    if not intel["sources"]:
        intel["note"] = "No API keys configured. Add keys in Replit Secrets for live intelligence."
    else:
        intel["note"] = f"Intelligence from {len(intel['sources'])} source(s): {', '.join(intel['sources'])}"

    return intel


def aggregate_phone_intel(phone):
    """Run all available phone intelligence APIs."""
    intel = {
        "target": phone,
        "type": "Phone Number",
        "scanned_at": datetime.now().isoformat(),
        "sources": [],
    }

    nv = numverify_lookup(phone)
    if nv and "error" not in nv:
        intel["sources"].append("numverify")
        intel["valid"] = nv.get("valid")
        intel["country"] = nv.get("country")
        intel["country_code"] = nv.get("country_code")
        intel["carrier"] = nv.get("carrier")
        intel["line_type"] = nv.get("line_type")
        intel["location"] = nv.get("location")
        intel["intl_format"] = nv.get("intl_format")
        intel["local_format"] = nv.get("local_format")

    if not intel["sources"]:
        intel["note"] = "No API keys configured. Add keys in Replit Secrets for live intelligence."
    else:
        intel["note"] = f"Intelligence from {len(intel['sources'])} source(s): {', '.join(intel['sources'])}"

    return intel


def lookup_social_username(username, platform):
    """Dispatch to the right social media API."""
    platform = platform.lower()
    if platform in ("github", "git_hub"):
        result = github_user(username)
        if result:
            result["platform"] = "GitHub"
            return result
    elif platform in ("reddit",):
        result = reddit_user(username)
        if result:
            result["platform"] = "Reddit"
            return result
    elif platform in ("twitter", "x", "twitter/x"):
        result = twitter_user(username)
        if result:
            result["platform"] = "Twitter/X"
            return result
    return None
