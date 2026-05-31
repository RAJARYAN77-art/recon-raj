#!/usr/bin/env python3
# ==========================================================
# RECONE-RAJ v3.0 - Advanced Recon Framework
# Author: Raj Aryan
# Features:
# - Parallel Execution
# - Live Statistics
# - Progress Bars
# - Automatic Tool Detection
# - JSON Report
# - HTML Report
# - Colored UI
# - Fast Recon Engine
# ==========================================================

import os
import json
import time
import socket
import shutil
import threading
import subprocess
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# ==========================
# CONFIG
# ==========================

VERSION = "3.0"
REPORT_DIR = "reports"

os.makedirs(REPORT_DIR, exist_ok=True)

# ==========================
# COLORS
# ==========================

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
WHITE = "\033[97m"
RESET = "\033[0m"

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

██████╗  █████╗      ██╗
██╔══██╗██╔══██╗     ██║
██████╔╝███████║     ██║
██╔══██╗██╔══██║██   ██║
██║  ██║██║  ██║╚█████╔╝
╚═╝  ╚═╝╚═╝  ╚═╝ ╚════╝

        RECONE-RAJ v{VERSION}
     Advanced Recon Framework
{RESET}
"""

# ==========================
# TOOL DETECTION
# ==========================

TOOLS = [
    "subfinder",
    "assetfinder",
    "amass",
    "httpx",
    "naabu",
    "nmap",
    "waybackurls",
    "gau",
    "katana",
    "hakrawler",
    "dnsx"
]

detected_tools = {}

def detect_tools():
    print(f"\n{YELLOW}[+] Detecting Installed Tools...{RESET}\n")

    for tool in TOOLS:
        if shutil.which(tool):
            detected_tools[tool] = True
            print(f"{GREEN}[FOUND]{RESET} {tool}")
        else:
            detected_tools[tool] = False
            print(f"{RED}[MISSING]{RESET} {tool}")

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
    print(
        f"\r{CYAN}[{bar:<50}] {percent}%{RESET}",
        end="",
        flush=True
    )

# ==========================
# COMMAND EXECUTOR
# ==========================

results = {}

def run_command(name, cmd):

    print(f"\n{BLUE}[RUNNING]{RESET} {name}")

    try:
        output = subprocess.check_output(
            cmd,
            shell=True,
            stderr=subprocess.DEVNULL,
            timeout=600
        ).decode(errors="ignore")

        results[name] = output
        update_stats(True)

    except Exception as e:
        results[name] = f"ERROR: {str(e)}"
        update_stats(False)

# ==========================
# RECON MODULES
# ==========================

def build_commands(domain):

    cmds = {}

    if detected_tools.get("subfinder"):
        cmds["Subfinder"] = f"subfinder -silent -d {domain}"

    if detected_tools.get("assetfinder"):
        cmds["Assetfinder"] = f"assetfinder --subs-only {domain}"

    if detected_tools.get("amass"):
        cmds["Amass"] = f"amass enum -passive -d {domain}"

    if detected_tools.get("httpx"):
        cmds["HTTPX"] = f"echo {domain} | httpx -silent"

    if detected_tools.get("naabu"):
        cmds["Naabu"] = f"naabu -host {domain} -silent"

    if detected_tools.get("nmap"):
        cmds["Nmap"] = f"nmap -F {domain}"

    if detected_tools.get("waybackurls"):
        cmds["WaybackURLs"] = f'echo "{domain}" | waybackurls'

    if detected_tools.get("gau"):
        cmds["GAU"] = f'gau "{domain}"'

    if detected_tools.get("katana"):
        cmds["Katana"] = f'echo "https://{domain}" | katana -silent'

    if detected_tools.get("hakrawler"):
        cmds["Hakrawler"] = f'echo "https://{domain}" | hakrawler'

    if detected_tools.get("dnsx"):
        cmds["DNSX"] = f'echo "{domain}" | dnsx'

    return cmds

# ==========================
# JSON REPORT
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

# ==========================
# HTML REPORT
# ==========================

def save_html(domain):

    file = f"{REPORT_DIR}/{domain}_report.html"

    html = f"""
<html>
<head>
<title>RECONE-RAJ REPORT</title>

<style>

body {{
background:#111;
color:white;
font-family:monospace;
}}

pre {{
background:#222;
padding:15px;
border-radius:10px;
overflow:auto;
}}

h1 {{
color:cyan;
}}

</style>

</head>

<body>

<h1>RECONE-RAJ v3.0 Report</h1>

<p>Target: {domain}</p>
<p>Date: {datetime.now()}</p>

"""

    for name, output in results.items():

        html += f"""
<h2>{name}</h2>
<pre>{output}</pre>
"""

    html += "</body></html>"

    with open(file, "w") as f:
        f.write(html)

    return file

# ==========================
# MAIN RECON ENGINE
# ==========================

def run_recon(domain):

    commands = build_commands(domain)

    total = len(commands)

    if total == 0:
        print(f"{RED}No recon tools found!{RESET}")
        return

    print(f"\n{GREEN}[+] Running {total} Recon Modules{RESET}\n")

    completed = 0

    with ThreadPoolExecutor(max_workers=10) as executor:

        futures = []

        for name, cmd in commands.items():
            futures.append(
                executor.submit(
                    run_command,
                    name,
                    cmd
                )
            )

        for future in futures:
            future.result()

            completed += 1
            progress(completed, total)

    print("\n")

# ==========================
# DOMAIN INFO
# ==========================

def domain_info(domain):

    try:
        ip = socket.gethostbyname(domain)

        print(f"\n{GREEN}[DOMAIN]{RESET} {domain}")
        print(f"{GREEN}[IP]{RESET} {ip}")

    except:
        pass

# ==========================
# DASHBOARD
# ==========================

def dashboard():

    runtime = int(time.time() - stats["start_time"])

    print(f"""
{CYAN}
===================================
           LIVE STATS
===================================
Commands Run : {stats["commands"]}
Successful   : {stats["successful"]}
Failed       : {stats["failed"]}
Runtime      : {runtime}s
===================================
{RESET}
""")

# ==========================
# MAIN
# ==========================

def main():

    os.system("clear")

    print(BANNER)

    detect_tools()

    domain = input(
        f"\n{CYAN}[TARGET DOMAIN]{RESET} > "
    ).strip()

    domain_info(domain)

    start = time.time()

    run_recon(domain)

    dashboard()

    json_report = save_json(domain)
    html_report = save_html(domain)

    print(f"{GREEN}[+] JSON Report:{RESET} {json_report}")
    print(f"{GREEN}[+] HTML Report:{RESET} {html_report}")

    print(
        f"\n{GREEN}[✓] Recon Completed in "
        f"{round(time.time()-start,2)} seconds{RESET}"
    )

if __name__ == "__main__":
    main()
