# CronJobOrganize

A lightweight, no-dependency Python script designed for quick parsing and categorization of cron jobs. 


## Features

* **Human-Readable Frequencies:** Converts standard `* * * * *` syntax and macros like `@daily` into plain English (e.g., "Once a day", "Every minute").
* **Smart Rounding:** Recognizes step intervals and translates them naturally. For example, a minute field of `*/15` becomes "About every 15 minutes," and a month field of `*/3` becomes "Quarterly."
* **Executable Extraction:** Automatically isolates the base script or executable name (e.g., `curl`, `bash`, `backup.sh`), stripping away absolute paths and command-line arguments.
* **Comment Awareness:** Detects and flags whether a cron job is active or commented out (`#`), making it easy to spot dormant tasks.

## Prerequisites

Nothing extra is required! This script relies entirely on the Python Standard Library (`csv`, `os`). 

There are no external packages to install, which means it runs out-of-the-box on any system with Python installed.

## Usage

1. Save your raw list of cron jobs into a text file named `cron_jobs.txt`.
2. Place `cron_jobs.txt` in the exact same directory as the Python script.
3. Run the script from your terminal:
   ```bash
   python cron_parser_rounded.py
