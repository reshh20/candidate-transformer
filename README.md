# Multi-Source Candidate Data Transformer

A Python-based pipeline that transforms messy candidate information from multiple sources into a clean, canonical, deduplicated JSON profile with provenance tracking, confidence scoring, runtime configuration, and validation.



## Overview

This project combines candidate information from:

- Structured Source: Recruiter CSV
- Unstructured Source: GitHub Public REST API (via the `github_username` column)

The pipeline extracts, normalizes, merges, validates, and outputs configurable JSON profiles without modifying the core pipeline logic.



## Features

- Multi-source data integration (Recruiter CSV + GitHub API)
- Candidate deduplication and merge
- Phone normalization (E.164)
- Date normalization (YYYY-MM)
- Canonical skill normalization
- Provenance tracking for every merged field
- Per-field and overall confidence scoring
- Runtime configurable output (`default.json` / `minimal.json`)
- Schema validation
- Command Line Interface (CLI)
- Optional Streamlit Web UI
- Automated unit tests using Pytest



# Project Structure

```text
candidate-transformer/
│
├── app.py                     # Streamlit Web UI
├── main.py                    # CLI entry point
├── README.md
├── requirements.txt
├── pytest.ini
├── .gitignore
│
├── src/
│   ├── extract_csv.py
│   ├── extract_github.py
│   ├── normalize.py
│   ├── merge.py
│   ├── project.py
│   ├── validate.py
│   └── pipeline.py
│
├── configs/
│   ├── default.json
│   └── minimal.json
│
├── sample_inputs/
│   └── recruiter.csv
│
├── sample_outputs/
│
├── tests/
│
└── Design_Document.pdf
```



# Installation

Clone the repository.

Create a virtual environment.

```bash
python -m venv venv
```

Activate it.

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```



# Running the Project

## Option 1 — Command Line Interface (CLI)

Generate the complete canonical output.

```bash
python main.py --csv sample_inputs/recruiter.csv --out sample_outputs/output_default.json
```

Generate output using the minimal configuration.

```bash
python main.py --csv sample_inputs/recruiter.csv --config configs/minimal.json --out sample_outputs/output_minimal.json
```

Generate output using the default runtime configuration.

```bash
python main.py --csv sample_inputs/recruiter.csv --config configs/default.json --out sample_outputs/output_default_config.json
```



## Option 2 — Streamlit Web UI

Launch the web interface.

```bash
streamlit run app.py
```

The browser interface allows you to:

- Upload a recruiter CSV or use the bundled sample CSV
- Automatically retrieve GitHub data using the `github_username` column
- Choose between `default.json` and `minimal.json`
- Run the pipeline
- View candidate profiles interactively
- Download the generated JSON output

> The Streamlit UI uses the exact same pipeline functions as the CLI. No duplicate business logic is implemented.



# Running Tests

Execute all unit tests.

```bash
pytest -v
```



# Sample Input

`sample_inputs/recruiter.csv` contains four example candidates:

- Two candidates linked to real GitHub users (`octocat` and `torvalds`) with intentionally conflicting names to demonstrate conflict resolution.
- One candidate without a GitHub username (single-source processing).
- One candidate referencing a non-existent GitHub username (`ghost-user-404`) to demonstrate graceful API failure handling.



# Pipeline


Recruiter CSV
        │
        ▼
Extract CSV Fields
        │
        ▼
GitHub API Lookup (if github_username exists)
        │
        ▼
Normalize
(phones, dates, skills)
        │
        ▼
Merge Candidate Records
        │
        ▼
Assign Confidence
        │
        ▼
Record Provenance
        │
        ▼
Apply Runtime Configuration
        │
        ▼
Validate Output
        │
        ▼
Output JSON



# Design Decisions

- GitHub usernames stored in the recruiter CSV act as the linkage between the structured and unstructured sources.
- When names conflict, GitHub is preferred because it is considered self-reported by the candidate.
- CSV remains the preferred source for recruiter-entered information such as company/title.
- Every merge decision is recorded in the provenance field.
- Confidence scores follow the assignment's policy:
  - 1.0 → confirmed by multiple independent sources
  - 0.6 → available from one structured source
  - 0.3 → available from one unstructured source
  - 0.0 → value missing



# Edge Cases Handled

- Missing recruiter CSV
- Empty CSV
- Invalid GitHub username
- GitHub API failure
- Invalid phone number
- Missing email
- Missing GitHub username
- Conflicting names between CSV and GitHub
- Missing fields handled according to runtime configuration (`null`, `omit`, or `error`)



# Assumptions

- GitHub usernames are provided in the recruiter CSV.
- Public GitHub API is available.
- Only public GitHub profile information is used.
- Runtime configuration determines the final output format.



# Deliverables

This repository contains:

- Source code
- Design document
- Sample inputs
- Sample outputs
- Runtime configuration files
- Automated tests
- Streamlit UI
- CLI implementation
- README



# Demo Video

A short demonstration video showing:

- Running the pipeline end-to-end
- Default output
- Custom configuration output
- Design decisions
- Edge case handling

Demo Video: https://drive.google.com/file/d/11_cmF-0K2HiZt7ydOvEE-c3UvLud6Mdg/view?usp=sharing




