import socket
import sys
import argparse
import time
from datetime import datetime

def grab_banner(ip, port):
    try:
        s = socket.socket()
        s.settimeout(3)
        s.connect((ip, port))
        if port == 80:
            s.send(b"HEAD / HTTP/1.0\r\n\r\n")
        banner = s.recv(1024)
        s.close()
        return banner.decode().strip()
    except Exception as e:
        return None

def main():
    parser = argparse.ArgumentParser(description='Clean OSINT Banner Grabber')
    parser.add_argument('--target', required=True, help='Target domain or IP')
    parser.add_argument('--ports', default='21,22,23,25,53,80,110,135,139,143,443,445,3306,3389', help='Comma separated ports')
    args = parser.parse_args()

    target = args.target
    ports = [int(p) for p in args.ports.split(',')]
    timestamp = datetime.now().isoformat()
    log_file = f"banner_scan_{target}_{int(time.time())}.log"
    
    with open(log_file, "w") as f:
        f.write(f"SCAN_START: {timestamp}\n")
        f.write(f"TARGET: {target}\n")
        f.write("-" * 50 + "\n")
        for port in ports:
            banner = grab_banner(target, port)
            if banner:
                result = f"PORT {port}: OPEN | BANNER: {repr(banner)}"
                f.write(result + "\n")
            else:
                f.write(f"PORT {port}: CLOSED/FILTERED\n")
        f.write("-" * 50 + "\n")
        f.write(f"SCAN_END: {datetime.now().isoformat()}\n")

if __name__ == "__main__":
    main()