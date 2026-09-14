# cronjoborganize

![PyPI](https://img.shields.io/pypi/v/cronjoborganize?v=1)
![License](https://img.shields.io/pypi/l/cronjoborganize?v=1)
![Python](https://img.shields.io/pypi/pyversions/cronjoborganize?v=1)

A Python command-line tool designed to seamlessly parse and structure cron job expressions into well-organized CSV reports. 

## Features

* **Parse Cron Expressions:** Accurately reads standard cron scheduling syntax.
* **CSV Reporting:** Exports your parsed cron jobs into a structured, readable CSV format for straightforward auditing and analysis.
* **CLI Interface:** Provides a lightweight and intuitive command-line interface.

## Installation

You can install `cronjoborganize` directly using pip:

```bash
pip install cronjoborganize
```
## Usage

Once installed, the package provides a global command-line utility: `cron-organize`.

### 1. Analyze Live System Cron Jobs 
You can pipe your current crontab directly into the tool without needing to save it to a file first:
```bash
crontab -l | cron-organize
```

### 2. Analyze a Specific File
If you have a saved text file containing cron expressions, pass it as an argument:
```bash
cron-organize path/to/cron_jobs.txt
```

### 3. Customizing the Output
By default, the tool generates a file named `cron_analysis.csv` in your current directory. You can specify a custom output filename using the `-o` or `--output` flag:
```bash
crontab -l | cron-organize -o my_server.csv
```

### Help 
To see all available options at any time, run:
```bash
cron-organize --help
```
