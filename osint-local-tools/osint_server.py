#!/usr/bin/env python3
"""
OsintNeoAI Local Server - Simple Flask app
Serves the OSINT dashboard and API endpoints
"""
import os
import json
import subprocess
import socket
import ssl
import requests
from datetime import datetime
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__)

# ── OSINT Functions ─────────────────────────────────────────
def dns_lookup(domain):
    import dns.resolver
    results = {}
    for rtype in ['A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA']:
        try:
            answers = dns.resolver.resolve(domain, rtype)
            results[rtype] = [str(r) for r in answers]
        except:
            pass
    return results

def whois_lookup(domain):
    try:
        import whois
        w = whois.whois(domain)
        return {"registrar": w.registrar, "creation": str(w.creation_date), "expiration": str(w.expiration_date)}
    except:
        return {"error": "whois failed"}

def port_scan(host, ports=[21,22,25,53,80,110,143,443,993,995,3306,3389,5432,8080,8443]):
    open_ports = []
    for port in ports:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                if s.connect_ex((host, port)) == 0:
                    open_ports.append(port)
        except:
            pass
    return open_ports

def shodan_lookup(ip):
    try:
        r = requests.get(f"https://internetdb.shodan.io/{ip}", timeout=10)
        return r.json()
    except:
        return {"error": "shodan failed"}

def ip_info(ip):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
        return r.json()
    except:
        return {"error": "ip-api failed"}

def cert_check(domain):
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                return {
                    "subject": dict(x[0] for x in cert.get('subject', [])),
                    "issuer": dict(x[0] for x in cert.get('issuer', [])),
                    "notAfter": cert.get('notAfter'),
                    "san": [x[1] for x in cert.get('subjectAltName', [])]
                }
    except:
        return {"error": "SSL check failed"}

def wifi_scan():
    try:
        result = subprocess.run(['netsh', 'wlan', 'show', 'networks', 'mode=bssid'],
                              capture_output=True, text=True, timeout=10)
        networks = []
        current = {}
        for line in result.stdout.split('\n'):
            line = line.strip()
            if 'SSID' in line and 'BSSID' not in line:
                if current: networks.append(current)
                current = {"ssid": line.split(':', 1)[-1].strip()}
            elif 'Signal' in line: current["signal"] = line.split(':', 1)[-1].strip()
            elif 'Authentication' in line: current["auth"] = line.split(':', 1)[-1].strip()
            elif 'BSSID' in line: current["bssid"] = line.split(':', 1)[-1].strip()
            elif 'Channel' in line: current["channel"] = line.split(':', 1)[-1].strip()
        if current: networks.append(current)
        return networks
    except:
        return []

def bluetooth_scan():
    try:
        result = subprocess.run(['powershell', '-Command',
            'Get-PnpDevice -Class Bluetooth | Select-Object -Property Name,Status | ConvertTo-Json'],
            capture_output=True, text=True, timeout=15)
        devices = json.loads(result.stdout) if result.stdout.strip() else []
        return devices if isinstance(devices, list) else [devices]
    except:
        return []

# ── Routes ──────────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(".", "osint_dashboard.html")

@app.route("/api/dns/<domain>")
def api_dns(domain):
    return jsonify(dns_lookup(domain))

@app.route("/api/whois/<domain>")
def api_whois(domain):
    return jsonify(whois_lookup(domain))

@app.route("/api/ports/<host>")
def api_ports(host):
    return jsonify({"host": host, "open_ports": port_scan(host)})

@app.route("/api/shodan/<ip>")
def api_shodan(ip):
    return jsonify(shodan_lookup(ip))

@app.route("/api/ip/<ip>")
def api_ip(ip):
    return jsonify(ip_info(ip))

@app.route("/api/ssl/<domain>")
def api_ssl(domain):
    return jsonify(cert_check(domain))

@app.route("/api/wifi")
def api_wifi():
    return jsonify(wifi_scan())

@app.route("/api/bluetooth")
def api_bluetooth():
    return jsonify(bluetooth_scan())

@app.route("/api/recon/<domain>")
def api_recon(domain):
    results = {
        "domain": domain,
        "timestamp": datetime.now().isoformat(),
        "dns": dns_lookup(domain),
        "whois": whois_lookup(domain),
        "ssl": cert_check(domain),
    }
    try:
        ips = results["dns"].get("A", [])
        if ips:
            results["ports"] = port_scan(ips[0])
            results["shodan"] = shodan_lookup(ips[0])
            results["ip_info"] = ip_info(ips[0])
    except:
        pass
    return jsonify(results)

@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "time": datetime.now().isoformat()})

if __name__ == "__main__":
    print("Starting OsintNeoAI on http://localhost:8080")
    app.run(host="0.0.0.0", port=8080, debug=False)
