# RECONE-RAJ v3.0

Advanced Recon Framework with Parallel Execution, Progress Tracking, Live Statistics, Automatic Tool Detection, JSON Reports, and HTML Reports.

![Version](https://img.shields.io/badge/version-3.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-green)
![Platform](https://img.shields.io/badge/platform-Linux-orange)

---

## Overview

RECONE-RAJ is a Python-based framework that provides a centralized interface for running installed reconnaissance modules, collecting results, and generating professional reports.

### Features

* Automatic Tool Detection
* Parallel Execution
* Progress Bars
* Live Statistics Dashboard
* JSON Report Generation
* HTML Report Generation
* Colored Terminal UI
* Fast Multi-Threaded Engine
* Single File Deployment
* Easy Customization

---

## Installation

### Clone Repository

```bash
git clone https://github.com/RAJARYAN77-art/recon-raj.git

cd recon-raj
```

Replace `USERNAME` with your GitHub username.

---

### Verify Python Installation

```bash
python3 --version
```

Expected Output:

```text
Python 3.8+
```

---

### Make Script Executable

```bash
chmod +x recone-raj.py
```

---

## Running RECONE-RAJ

Run directly with Python:

```bash
python3 recone-raj.py
```

or

```bash
./recone-raj.py
```

---

## Create Global Command

To run the framework by simply typing:

```bash
recon
```

follow one of the methods below.

---

### Method 1 - Symbolic Link

Find the full path:

```bash
pwd
```

Example:

```text
/home/raj/RECONE-RAJ
```

Create the symbolic link:

```bash
sudo ln -s /home/raj/RECONE-RAJ/recone-raj.py /usr/local/bin/recon
```

Verify:

```bash
which recon
```

Expected:

```text
/usr/local/bin/recon
```

Now run:

```bash
recon
```

from anywhere.

---

### Method 2 - Launcher Script

Create a launcher:

```bash
sudo nano /usr/local/bin/recon
```

Add:

```bash
#!/bin/bash
python3 /home/raj/RECONE-RAJ/recone-raj.py "$@"
```

Save and exit.

Make executable:

```bash
sudo chmod +x /usr/local/bin/recon
```

Run:

```bash
recon
```

---

## Workflow

1. Start RECONE-RAJ
2. Installed tools are detected automatically
3. Enter the target
4. Available modules are executed
5. Progress bar updates in real time
6. Statistics dashboard is displayed
7. Reports are generated automatically

---

## Output Reports

Reports are stored inside:

```text
reports/
```

Generated files:

```text
reports/
├── target_report.json
└── target_report.html
```

---

## JSON Report Example

```json
{
    "domain": "example.com",
    "date": "2026-05-31",
    "stats": {
        "commands": 10,
        "successful": 10,
        "failed": 0
    }
}
```

---

## HTML Report

Open in browser:

```bash
firefox reports/example.com_report.html
```

or

```bash
google-chrome reports/example.com_report.html
```

---

## Statistics Dashboard

Example:

```text
===================================
           LIVE STATS
===================================
Commands Run : 10
Successful   : 10
Failed       : 0
Runtime      : 14s
===================================
```

---

## Project Structure

```text
RECONE-RAJ/
│
├── recone-raj.py
├── README.md
│
└── reports/
    ├── target_report.json
    └── target_report.html
```

---

## Customization

You can extend the framework by:

* Adding new modules
* Creating new report formats
* Adding configuration files
* Implementing plugin support
* Improving dashboard statistics
* Adding logging support

---

## Requirements

### Operating System

* Linux
* Kali Linux
* Ubuntu
* Debian
* Parrot OS

### Python

```text
Python 3.8+
```

---

## Troubleshooting

### Permission Denied

```bash
chmod +x recone-raj.py
```

---

### Command Not Found

Check:

```bash
which recon
```

Verify PATH:

```bash
echo $PATH
```

---

### Python Not Found

Install Python:

```bash
sudo apt update

sudo apt install python3
```

---

## Development

Run syntax check:

```bash
python3 -m py_compile recone-raj.py
```

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push changes
5. Open a Pull Request

---

## Legal Notice

This project should only be used on systems, networks, and assets that you own or are explicitly authorized to assess.

Users are responsible for complying with all applicable laws, regulations, policies, and terms of service.

---

## Author

Raj Aryan

GitHub: https://github.com/YOUR_USERNAME

---

## License

MIT License

Copyright (c) 2026 Raj Aryan

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files to deal in the Software without restriction.
