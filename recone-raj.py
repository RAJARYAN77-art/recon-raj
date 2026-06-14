#!/usr/bin/env python3
# ==========================================================
# RECONE-RAJ v4.0 - Advanced OSINT Recon Framework
# Author: Raj Aryan
# Features:
# - Parallel Execution
# - Live Statistics
# - Progress Bars
# - Automatic Tool Detection
# - JSON + HTML Reports
# - WHOIS / ASN / CIDR Lookup
# - Certificate Transparency (crt.sh)
# - Shodan / VirusTotal / SecurityTrails APIs
# - Technology Fingerprinting
# - Email Harvesting
# - GitHub Dorking hints
# - Open Redirect / Juicy URL pattern detection
# - DNS Record full dump
# - IP Geolocation
# ==========================================================

import os
import json
import time
import socket
import shutil
import threading
import subprocess
import urllib.request
import urllib.parse
import ssl
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# ==========================
# CONFIG
# ==========================
VERSION = "4.0"
REPORT_DIR = "reports"
os.makedirs(REPORT_DIR, exist_ok=True)

# Optional: Set API keys here or via environment variables
SHODAN_API_KEY    = os.environ.get("SHODAN_API_KEY", "")
VT_API_KEY        = os.environ.get("VT_API_KEY", "")
SECTRAILS_API_KEY = os.environ.get("SECTRAILS_API_KEY", "")

# ==========================
# COLORS
# ==========================
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
CYAN   = "\033[96m"
WHITE  = "\033[97m"
MAGENTA= "\033[95m"
RESET  = "\033[0m"

# ==========================
# BANNER
# ==========================
BANNER = rf"""
{CYAN}
██████╗ ███████╗ ██████╗ ██████╗ ███╗   ██╗███████╗
██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗  ██║██╔════╝
██████╔╝█████╗  ██║     ██║   ██║██╔██╗ ██║█████╗
██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╗██║██╔══╝
██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║███████╗
╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝
        RECONE-RAJ v{VERSION}
     Advanced OSINT Recon Framework
{RESET}
"""

# ==========================
# TOOL DETECTION
# ==========================
TOOLS = [
    "subfinder", "assetfinder", "amass", "httpx",
    "naabu", "nmap", "waybackurls", "gau", "katana",
    "hakrawler", "dnsx", "whois", "dig", "theHarvester",
    "ffuf", "nuclei"
]

detected_tools = {}

def detect_tools():
    print(f"\n{YELLOW}[+] Detecting Installed Tools...{RESET}\n")
    for tool in TOOLS:
        found = shutil.which(tool) is not None
        detected_tools[tool] = found
        status = f"{GREEN}[FOUND]{RESET}" if found else f"{RED}[MISSING]{RESET}"
        print(f"  {status} {tool}")

# ==========================
# LIVE STATS
# ==========================
stats = {
    "commands": 0,
    "successful": 0,
    "failed": 0,
    "start_time": time.time()
}
lock = threading.Lock()

def update_stats(success=True):
    with lock:
        stats["commands"] += 1
        if success:
            stats["successful"] += 1
        else:
            stats["failed"] += 1

# ==========================
# PROGRESS BAR
# ==========================
def progress(current, total):
    percent = int((current / total) * 100)
    bar = "█" * (percent // 2)
    print(f"\r{CYAN}[{bar:<50}] {percent}%{RESET}", end="", flush=True)

# ==========================
# COMMAND EXECUTOR
# ==========================
results = {}

def run_command(name, cmd):
    print(f"\n{BLUE}[RUNNING]{RESET} {name}")
    try:
        output = subprocess.check_output(
            cmd, shell=True,
            stderr=subprocess.DEVNULL,
            timeout=600
        ).decode(errors="ignore").strip()
        results[name] = output if output else "(no output)"
        update_stats(True)
    except Exception as e:
        results[name] = f"ERROR: {str(e)}"
        update_stats(False)

# ==========================
# PASSIVE API MODULES
# ==========================

def fetch_url(url, headers=None):
    """Simple HTTPS GET, returns string or None."""
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers=headers or {
        "User-Agent": "RECONE-RAJ/4.0"
    })
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
            return r.read().decode(errors="ignore")
    except Exception as e:
        return f"ERROR: {e}"

def crt_sh(domain):
    """Certificate Transparency log search via crt.sh"""
    print(f"\n{MAGENTA}[CRT.SH]{RESET} Fetching certificate transparency logs...")
    url = f"https://crt.sh/?q=%.{urllib.parse.quote(domain)}&output=json"
    raw = fetch_url(url)
    if raw.startswith("ERROR"):
        results["CRT.SH"] = raw
        return
    try:
        data = json.loads(raw)
        names = sorted(set(
            entry.get("name_value", "").replace("*.", "")
            for entry in data
            if entry.get("name_value")
        ))
        results["CRT.SH - Certificate Transparency"] = "\n".join(names)
        print(f"  {GREEN}[+]{RESET} Found {len(names)} entries from crt.sh")
    except Exception as e:
        results["CRT.SH"] = f"Parse error: {e}"

def whois_lookup(domain):
    """WHOIS lookup using system whois or fallback API"""
    print(f"\n{MAGENTA}[WHOIS]{RESET} Looking up registration data...")
    if detected_tools.get("whois"):
        run_command("WHOIS", f"whois {domain}")
    else:
        raw = fetch_url(f"https://www.whois.com/whois/{domain}")
        results["WHOIS (web fallback)"] = raw[:3000] if raw else "N/A"

def dns_full_dump(domain):
    """Full DNS record dump: A, AAAA, MX, NS, TXT, CNAME, SOA, CAA"""
    print(f"\n{MAGENTA}[DNS]{RESET} Full DNS record dump...")
    record_types = ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA", "CAA", "SRV"]
    if detected_tools.get("dig"):
        all_records = []
        for rtype in record_types:
            try:
                out = subprocess.check_output(
                    f"dig +short {rtype} {domain}",
                    shell=True, stderr=subprocess.DEVNULL, timeout=10
                ).decode(errors="ignore").strip()
                if out:
                    all_records.append(f"=== {rtype} ===\n{out}")
            except:
                pass
        results["DNS Full Dump"] = "\n\n".join(all_records) if all_records else "No records"
    else:
        # Python fallback for A records
        try:
            ips = socket.getaddrinfo(domain, None)
            results["DNS (Python fallback)"] = "\n".join(set(i[4][0] for i in ips))
        except Exception as e:
            results["DNS (Python fallback)"] = str(e)

def reverse_ip_lookup(ip):
    """Find other domains on the same IP via HackerTarget"""
    print(f"\n{MAGENTA}[REVERSE IP]{RESET} Checking co-hosted domains on {ip}...")
    url = f"https://api.hackertarget.com/reverseiplookup/?q={ip}"
    raw = fetch_url(url)
    results["Reverse IP Lookup"] = raw if raw else "N/A"

def asn_lookup(ip):
    """ASN and CIDR info via ip-api.com"""
    print(f"\n{MAGENTA}[ASN/GEO]{RESET} IP geolocation and ASN lookup for {ip}...")
    raw = fetch_url(f"http://ip-api.com/json/{ip}?fields=status,country,regionName,city,isp,org,as,query")
    try:
        data = json.loads(raw)
        output = "\n".join(f"{k}: {v}" for k, v in data.items())
        results["IP Geolocation + ASN"] = output
        print(f"  {GREEN}[+]{RESET} {data.get('org','')} | {data.get('as','')} | {data.get('country','')}")
    except:
        results["IP Geolocation + ASN"] = raw

def shodan_lookup(ip):
    """Shodan host intelligence (requires API key)"""
    if not SHODAN_API_KEY:
        results["Shodan"] = "SKIPPED - Set SHODAN_API_KEY env var"
        return
    print(f"\n{MAGENTA}[SHODAN]{RESET} Querying Shodan for {ip}...")
    url = f"https://api.shodan.io/shodan/host/{ip}?key={SHODAN_API_KEY}"
    raw = fetch_url(url)
    try:
        data = json.loads(raw)
        ports   = data.get("ports", [])
        hostnames = data.get("hostnames", [])
        vulns   = list(data.get("vulns", {}).keys())
        os_info = data.get("os", "Unknown")
        out = (
            f"Open Ports    : {', '.join(str(p) for p in ports)}\n"
            f"Hostnames     : {', '.join(hostnames)}\n"
            f"OS            : {os_info}\n"
            f"CVEs (public) : {', '.join(vulns) if vulns else 'None listed'}\n"
            f"ISP           : {data.get('isp','')}\n"
            f"Country       : {data.get('country_name','')}\n"
        )
        results["Shodan Intelligence"] = out
    except:
        results["Shodan Intelligence"] = raw

def virustotal_lookup(domain):
    """VirusTotal passive DNS and reputation (requires API key)"""
    if not VT_API_KEY:
        results["VirusTotal"] = "SKIPPED - Set VT_API_KEY env var"
        return
    print(f"\n{MAGENTA}[VIRUSTOTAL]{RESET} Querying VirusTotal for {domain}...")
    url = f"https://www.virustotal.com/api/v3/domains/{domain}"
    raw = fetch_url(url, headers={
        "x-apikey": VT_API_KEY,
        "User-Agent": "RECONE-RAJ/4.0"
    })
    try:
        data = json.loads(raw)
        attrs = data.get("data", {}).get("attributes", {})
        stats_vt = attrs.get("last_analysis_stats", {})
        cats = attrs.get("categories", {})
        results["VirusTotal Reputation"] = (
            f"Malicious     : {stats_vt.get('malicious', 0)}\n"
            f"Suspicious    : {stats_vt.get('suspicious', 0)}\n"
            f"Harmless      : {stats_vt.get('harmless', 0)}\n"
            f"Undetected    : {stats_vt.get('undetected', 0)}\n"
            f"Categories    : {json.dumps(cats, indent=2)}\n"
            f"Reputation    : {attrs.get('reputation', 'N/A')}\n"
        )
    except:
        results["VirusTotal Reputation"] = raw

def hackertarget_headers(domain):
    """Fetch HTTP security headers via HackerTarget"""
    print(f"\n{MAGENTA}[HTTP HEADERS]{RESET} Checking security headers for {domain}...")
    url = f"https://api.hackertarget.com/httpheaders/?q=https://{domain}"
    raw = fetch_url(url)
    results["HTTP Security Headers"] = raw if raw else "N/A"

def hackertarget_links(domain):
    """Extract page links via HackerTarget"""
    print(f"\n{MAGENTA}[PAGE LINKS]{RESET} Extracting links from {domain}...")
    url = f"https://api.hackertarget.com/pagelinks/?q=https://{domain}"
    raw = fetch_url(url)
    results["Page Links (HackerTarget)"] = raw if raw else "N/A"

def hackertarget_subnet(ip):
    """CIDR subnet / network info for an IP"""
    print(f"\n{MAGENTA}[SUBNET]{RESET} Getting network range for {ip}...")
    url = f"https://api.hackertarget.com/subnetcalc/?q={ip}"
    raw = fetch_url(url)
    results["Subnet / Network Range"] = raw if raw else "N/A"

def email_harvest(domain):
    """Email harvesting via theHarvester if available"""
    if detected_tools.get("theHarvester"):
        print(f"\n{MAGENTA}[EMAIL HARVEST]{RESET} Searching for emails on {domain}...")
        run_command("theHarvester - Email/Subdomain Harvest",
                    f"theHarvester -d {domain} -b all -l 200")
    else:
        results["theHarvester"] = "SKIPPED - theHarvester not installed"

def wayback_juicy_urls(domain):
    """Pull and filter juicy paths from Wayback Machine"""
    print(f"\n{MAGENTA}[JUICY URLS]{RESET} Filtering sensitive URL patterns from Wayback...")
    url = (
        f"https://web.archive.org/cdx/search/cdx"
        f"?url=*.{domain}/*&output=text&fl=original&collapse=urlkey&limit=5000"
    )
    raw = fetch_url(url)
    if not raw or raw.startswith("ERROR"):
        results["Wayback Juicy URLs"] = raw or "N/A"
        return

    juicy_patterns = [
        ".env", "config", "backup", ".bak", ".sql", ".db",
        "admin", "login", "password", "passwd", "secret",
        "api/v", "/api/", ".git", "wp-config", "credentials",
        "token", "auth", "phpinfo", "debug", ".log", ".xml",
        "swagger", "graphql", ".json", "upload", ".zip", ".tar"
    ]
    lines = raw.splitlines()
    juicy = [l for l in lines if any(p in l.lower() for p in juicy_patterns)]
    results["Wayback Juicy URL Patterns"] = (
        f"Total URLs fetched : {len(lines)}\n"
        f"Juicy matches     : {len(juicy)}\n\n"
        + "\n".join(juicy[:500])
    )
    print(f"  {GREEN}[+]{RESET} {len(juicy)} juicy URL patterns found out of {len(lines)} archived URLs")

def github_dork_hints(domain):
    """Print GitHub dork queries to search manually"""
    print(f"\n{MAGENTA}[GITHUB DORKS]{RESET} Generating GitHub dork queries...")
    company = domain.split(".")[0]
    dorks = [
        f'"{domain}" password',
        f'"{domain}" secret',
        f'"{domain}" api_key',
        f'"{domain}" token',
        f'"{company}" config',
        f'"{company}" credentials',
        f'"{company}" .env',
        f'"{company}" internal',
        f'org:{company} filename:.env',
        f'org:{company} filename:config.json',
        f'org:{company} filename:secrets',
    ]
    results["GitHub Dork Queries (Manual)"] = (
        "Search these on https://github.com/search?type=code\n\n"
        + "\n".join(dorks)
    )

def google_dork_hints(domain):
    """Print Google dork queries"""
    print(f"\n{MAGENTA}[GOOGLE DORKS]{RESET} Generating Google dork queries...")
    dorks = [
        f"site:{domain} filetype:pdf",
        f"site:{domain} filetype:xls OR filetype:xlsx",
        f"site:{domain} filetype:doc OR filetype:docx",
        f"site:{domain} inurl:admin",
        f"site:{domain} inurl:login",
        f"site:{domain} inurl:config",
        f"site:{domain} inurl:backup",
        f"site:{domain} intext:password",
        f"site:{domain} intext:username",
        f"site:{domain} intitle:\"index of\"",
        f"site:{domain} ext:env OR ext:log OR ext:bak",
        f"\"@{domain}\" email",
    ]
    results["Google Dork Queries (Manual)"] = (
        "Search these on https://www.google.com\n\n"
        + "\n".join(dorks)
    )

def nuclei_scan(domain):
    """Run nuclei with passive/info templates if available"""
    if detected_tools.get("nuclei"):
        print(f"\n{MAGENTA}[NUCLEI]{RESET} Running nuclei info/exposure templates on {domain}...")
        run_command("Nuclei - Info/Exposure Templates",
                    f"nuclei -u https://{domain} -severity info,low -silent -timeout 5")
    else:
        results["Nuclei"] = "SKIPPED - nuclei not installed"

# ==========================
# BUILD TOOL COMMANDS
# ==========================
def build_commands(domain):
    cmds = {}
    if detected_tools.get("subfinder"):
        cmds["Subfinder - Passive Subdomains"] = f"subfinder -silent -d {domain}"
    if detected_tools.get("assetfinder"):
        cmds["Assetfinder - Subdomains"] = f"assetfinder --subs-only {domain}"
    if detected_tools.get("amass"):
        cmds["Amass - Passive Enum"] = f"amass enum -passive -d {domain}"
    if detected_tools.get("httpx"):
        cmds["HTTPX - Live Hosts + Tech"] = f"echo {domain} | httpx -silent -title -tech-detect -status-code"
    if detected_tools.get("naabu"):
        cmds["Naabu - Top Port Scan"] = f"naabu -host {domain} -silent -top-ports 1000"
    if detected_tools.get("nmap"):
        cmds["Nmap - Service Version Scan"] = f"nmap -sV -F --open {domain}"
    if detected_tools.get("waybackurls"):
        cmds["WaybackURLs"] = f'echo "{domain}" | waybackurls'
    if detected_tools.get("gau"):
        cmds["GAU - All URLs"] = f'gau --subs "{domain}"'
    if detected_tools.get("katana"):
        cmds["Katana - Crawl"] = f'echo "https://{domain}" | katana -silent -depth 3'
    if detected_tools.get("hakrawler"):
        cmds["Hakrawler - Crawl"] = f'echo "https://{domain}" | hakrawler -subs -d 3'
    if detected_tools.get("dnsx"):
        cmds["DNSX - DNS Probe"] = f'echo "{domain}" | dnsx -resp -a -aaaa -mx -ns -txt'
    return cmds

# ==========================
# DOMAIN INFO
# ==========================
def domain_info(domain):
    try:
        ip = socket.gethostbyname(domain)
        print(f"\n{GREEN}[DOMAIN]{RESET} {domain}")
        print(f"{GREEN}[IP]{RESET}     {ip}")
        return ip
    except Exception as e:
        print(f"{RED}[!] Could not resolve {domain}: {e}{RESET}")
        return None

# ==========================
# PASSIVE API RUNNER
# ==========================
def run_passive_apis(domain, ip):
    print(f"\n{YELLOW}{'='*50}")
    print(f"  PASSIVE OSINT API MODULES")
    print(f"{'='*50}{RESET}")

    passive_tasks = [
        lambda: crt_sh(domain),
        lambda: whois_lookup(domain),
        lambda: dns_full_dump(domain),
        lambda: hackertarget_headers(domain),
        lambda: hackertarget_links(domain),
        lambda: wayback_juicy_urls(domain),
        lambda: github_dork_hints(domain),
        lambda: google_dork_hints(domain),
        lambda: email_harvest(domain),
        lambda: nuclei_scan(domain),
    ]

    if ip:
        passive_tasks += [
            lambda: reverse_ip_lookup(ip),
            lambda: asn_lookup(ip),
            lambda: hackertarget_subnet(ip),
            lambda: shodan_lookup(ip),
        ]

    passive_tasks.append(lambda: virustotal_lookup(domain))

    for task in passive_tasks:
        try:
            task()
        except Exception as e:
            print(f"{RED}[ERROR]{RESET} {e}")

# ==========================
# RECON ENGINE
# ==========================
def run_recon(domain):
    commands = build_commands(domain)
    total = len(commands)
    if total == 0:
        print(f"{YELLOW}[!] No external tools found — running API-only mode{RESET}")
        return

    print(f"\n{GREEN}[+] Running {total} Tool-Based Recon Modules{RESET}\n")
    completed = 0
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [
            executor.submit(run_command, name, cmd)
            for name, cmd in commands.items()
        ]
        for future in futures:
            future.result()
            completed += 1
            progress(completed, total)
    print("\n")

# ==========================
# REPORTS
# ==========================
def save_json(domain):
    file = f"{REPORT_DIR}/{domain}_report.json"
    data = {
        "domain": domain,
        "date": str(datetime.now()),
        "stats": stats,
        "results": results
    }
    with open(file, "w") as f:
        json.dump(data, f, indent=4)
    return file

def save_html(domain):
    file = f"{REPORT_DIR}/{domain}_report.html"
    sections = ""
    for name, output in results.items():
        escaped = str(output).replace("<", "&lt;").replace(">", "&gt;")
        sections += f"<h2>{name}</h2><pre>{escaped}</pre>\n"

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>RECONE-RAJ v{VERSION} - {domain}</title>
<style>
  body  {{ background:#0d1117; color:#c9d1d9; font-family:monospace; padding:20px; }}
  h1    {{ color:#58a6ff; border-bottom:1px solid #30363d; padding-bottom:8px; }}
  h2    {{ color:#f0883e; margin-top:30px; }}
  pre   {{ background:#161b22; border:1px solid #30363d; padding:15px;
           border-radius:6px; overflow:auto; white-space:pre-wrap; word-break:break-all; }}
  .meta {{ color:#8b949e; font-size:0.9em; margin-bottom:20px; }}
  .stat {{ display:inline-block; background:#1f6feb22; border:1px solid #1f6feb;
           padding:4px 12px; border-radius:4px; margin:4px; }}
</style>
</head>
<body>
<h1>🔍 RECONE-RAJ v{VERSION} Report</h1>
<div class="meta">
  <b>Target:</b> {domain}<br>
  <b>Date:</b> {datetime.now()}<br>
  <b>Commands:</b> <span class="stat">{stats['commands']} run</span>
  <span class="stat">{stats['successful']} OK</span>
  <span class="stat">{stats['failed']} failed</span>
</div>
{sections}
</body>
</html>"""
    with open(file, "w") as f:
        f.write(html)
    return file

def save_markdown(domain):
    file = f"{REPORT_DIR}/{domain}_report.md"
    lines = [
        f"# RECONE-RAJ v{VERSION} — {domain}",
        f"**Date:** {datetime.now()}",
        f"**Commands:** {stats['commands']} | OK: {stats['successful']} | Failed: {stats['failed']}",
        ""
    ]
    for name, output in results.items():
        lines.append(f"## {name}")
        lines.append("```")
        lines.append(str(output)[:5000])
        lines.append("```")
        lines.append("")
    with open(file, "w") as f:
        f.write("\n".join(lines))
    return file

# ==========================
# DASHBOARD
# ==========================
def dashboard():
    runtime = int(time.time() - stats["start_time"])
    print(f"""
{CYAN}
╔══════════════════════════════════════╗
║           FINAL STATISTICS           ║
╠══════════════════════════════════════╣
║  Commands Run  :  {str(stats['commands']).ljust(18)}║
║  Successful    :  {str(stats['successful']).ljust(18)}║
║  Failed        :  {str(stats['failed']).ljust(18)}║
║  Runtime       :  {(str(runtime)+'s').ljust(18)}║
╚══════════════════════════════════════╝
{RESET}""")

# ==========================
# MAIN
# ==========================
def main():
    os.system("clear")
    print(BANNER)
    detect_tools()

    domain = input(f"\n{CYAN}[TARGET DOMAIN]{RESET} > ").strip()
    if not domain:
        print(f"{RED}[!] No domain entered.{RESET}")
        return

    print(f"\n{YELLOW}[*] Starting recon on: {domain}{RESET}")
    print(f"{YELLOW}[*] Time: {datetime.now()}{RESET}")

    ip = domain_info(domain)
    start = time.time()

    # Phase 1: Tool-based parallel recon
    run_recon(domain)

    # Phase 2: Passive API modules (sequential, network-light)
    run_passive_apis(domain, ip)

    dashboard()

    json_file = save_json(domain)
    html_file = save_html(domain)
    md_file   = save_markdown(domain)

    print(f"{GREEN}[+] JSON Report    :{RESET} {json_file}")
    print(f"{GREEN}[+] HTML Report    :{RESET} {html_file}")
    print(f"{GREEN}[+] Markdown Report:{RESET} {md_file}")
    print(f"\n{GREEN}[✓] Recon completed in {round(time.time()-start, 2)}s{RESET}\n")

if __name__ == "__main__":
    main()
