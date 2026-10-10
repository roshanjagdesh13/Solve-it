# 🧠 File Solver

> **AI-powered CLI tool that solves questions inside images, PDFs, and text files.**

[![CI](https://github.com/your-username/file-solver/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/file-solver/actions)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## What is File Solver?

File Solver is an open-source command-line tool that reads a file containing
questions or problems, sends the content to an AI model (OpenAI GPT-4o by
default), and saves a complete, structured solution into a `.solved` file.

```
question.pdf  →  question.pdf.solved
math.png      →  math.png.solved
assignment.txt →  assignment.txt.solved
```

It handles **mathematics, programming questions, theory, MCQs, handwriting,
diagrams, tables**, and more — anything a student might encounter in an
assignment or exam paper.

---

## Features

- 📄 **PDF support** — text PDFs and scanned/image PDFs (via OCR)
- 🖼️ **Image support** — PNG, JPG, JPEG, WEBP (multimodal AI or Tesseract OCR)
- 📝 **Text/Markdown support** — plain text and Markdown files
- 🤖 **Multimodal AI** — uses GPT-4o vision to understand handwriting, diagrams, equations
- 📦 **Batch processing** — solve multiple files or an entire directory at once
- 🔌 **Extensible solver architecture** — plug in any AI provider without rewriting the app
- 🛡️ **Secure by design** — API keys never logged, files never executed
- 🌍 **Cross-platform** — Windows, Linux, macOS

---

## Supported File Formats

| Format       | Extension(s)               | Method              |
|-------------|----------------------------|---------------------|
| Image        | `.png` `.jpg` `.jpeg` `.webp` | Vision API / OCR |
| PDF          | `.pdf`                     | Text extraction + OCR for scanned pages |
| Plain text   | `.txt`                     | Direct read         |
| Markdown     | `.md`                      | Direct read         |

---

## Requirements

- Python 3.9 or later
- An **OpenAI API key** ([get one here](https://platform.openai.com/api-keys))
- Optional: [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) (fallback for images if vision API unavailable)
- Optional: [Poppler](https://poppler.freedesktop.org/) (required by `pdf2image` for scanned PDFs)

> **Note on API costs**: File Solver uses *your own* OpenAI API key.
> You pay OpenAI directly for the tokens used. There is no shared or
> public key. See [OpenAI pricing](https://openai.com/pricing).

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/file-solver.git
cd file-solver
```

### 2. Create a virtual environment (recommended)

```bash
# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate

# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install File Solver

```bash
pip install -e .
```

This installs the `filesolver` command globally within your virtual environment.

### 4. Configure your API key

```bash
cp .env.example .env
```

Open `.env` and set your key:

```
OPENAI_API_KEY=sk-...your-key-here...
```

**Or** set it as an environment variable directly:

```bash
# Linux / macOS
export OPENAI_API_KEY=sk-...

# Windows (PowerShell)
$env:OPENAI_API_KEY = "sk-..."

# Windows (Command Prompt)
set OPENAI_API_KEY=sk-...
```

---

## Quick Start

```bash
filesolver solve question.pdf
```

Output:

```
  File Solver  — AI-powered question solver

  Input : question.pdf
  Type  : PDF

  [1/4] Reading file...
  [2/4] Extracting content...
  [3/4] Solving...
  [4/4] Writing solution...

  ✓ Completed

  Output: question.pdf.solved
```

Open the output:

```bash
# Linux / macOS
cat question.pdf.solved

# Windows (PowerShell)
Get-Content question.pdf.solved
```

---

## CLI Usage

### Solve a single file

```bash
filesolver solve question.pdf
filesolver solve math.png
filesolver solve assignment.txt
filesolver solve notes.md
```

### Specify an output directory

```bash
filesolver solve question.pdf --output answers/
```

### Specify an exact output filename

```bash
filesolver solve question.pdf --output-file final_answers.txt
```

### Batch processing — multiple files

```bash
filesolver solve q1.pdf q2.png q3.txt
```

### Batch processing — entire directory

```bash
filesolver solve ./questions/
```

Output:

```
Found files in: ./questions/

  ✓ question1.pdf  →  question1.pdf.solved
  ✓ question2.png  →  question2.png.solved
  ✓ assignment.txt →  assignment.txt.solved
  ⊘ notes.docx     —  unsupported format

  Completed: 3/3  (1 skipped)
```

### Debug mode (for developers)

```bash
filesolver solve file.pdf --debug
```

### Help and version

```bash
filesolver --help
filesolver --version
filesolver solve --help
```

---

## Output Format

Each `.solved` file contains:

```
File Solver — Solution Report
════════════════════════════════════════════════════════════════════════
Generated : 2024-01-15 14:30:00
Input file: question.pdf
Model     : gpt-4o
Tokens    : 1200 prompt / 800 completion
════════════════════════════════════════════════════════════════════════

SOLUTIONS
════════════════════════════════════════════════════════════════════════

Question 1
----------
[Complete structured solution...]

Question 2
----------
[Complete structured solution...]
```

### Solution types

| Problem Type     | Output Structure                                      |
|-----------------|-------------------------------------------------------|
| Mathematics      | Approach → Steps → Final Answer                       |
| Programming      | Approach → Algorithm → Complexity → Code → Explanation|
| Conceptual       | Explanation → Answer                                  |
| MCQ              | Correct Option → Explanation                          |

---

## Configuration

All configuration is done via environment variables or a `.env` file.

| Variable          | Required | Default  | Description                              |
|------------------|----------|----------|------------------------------------------|
| `OPENAI_API_KEY`  | ✅ Yes   | —        | Your OpenAI API key                      |
| `SOLVER_MODEL`    | No       | `gpt-4o` | OpenAI model to use                      |
| `MAX_FILE_SIZE`   | No       | `50`     | Maximum file size in megabytes           |
| `OUTPUT_DIRECTORY`| No       | —        | Default directory for `.solved` files    |

---

## Project Architecture

```
file-solver/
├── src/filesolver/
│   ├── cli/
│   │   ├── main.py          # Click commands (solve, --help, --version)
│   │   └── display.py       # Rich terminal output helpers
│   ├── config/
│   │   └── settings.py      # Environment variable loading & validation
│   ├── processors/
│   │   ├── base.py          # BaseProcessor abstract class
│   │   ├── image_processor.py    # Vision API + OCR fallback
│   │   ├── pdf_processor.py      # pypdf + scanned page handling
│   │   ├── text_processor.py     # Plain .txt files
│   │   └── markdown_processor.py # .md files
│   ├── solver/
│   │   ├── base.py          # BaseSolver abstract class
│   │   ├── openai_solver.py # OpenAI Chat Completions implementation
│   │   └── prompts.py       # System prompts per file type
│   ├── output/
│   │   └── writer.py        # Formats and writes .solved files
│   ├── utils/
│   │   └── file_utils.py    # File detection, path building, validation
│   └── engine.py            # Pipeline orchestrator
├── tests/
│   ├── test_utils.py
│   ├── test_processors.py
│   ├── test_solver.py
│   ├── test_output.py
│   ├── test_engine.py
│   ├── test_cli.py
│   └── samples/             # Sample files for testing
├── .github/workflows/ci.yml
├── pyproject.toml
├── .env.example
├── .gitignore
├── LICENSE
├── CONTRIBUTING.md
└── SECURITY.md
```

### Extending File Solver

**Add a new file format** — implement `BaseProcessor` and register the extension.  
**Add a new AI provider** — implement `BaseSolver` and wire it to the CLI.

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed instructions.

---

## Troubleshooting

### `ERROR: OPENAI_API_KEY is not configured.`

Set the environment variable:

```bash
export OPENAI_API_KEY=sk-...        # Linux/macOS
$env:OPENAI_API_KEY = "sk-..."      # Windows PowerShell
```

Or create a `.env` file from `.env.example`.

### `OpenAI API authentication failed.`

Your API key may be invalid or expired.  
Generate a new one at [platform.openai.com/api-keys](https://platform.openai.com/api-keys).

### `OpenAI rate limit reached.`

You have exceeded your API quota. Wait a few seconds and retry, or check your
usage at [platform.openai.com/account/usage](https://platform.openai.com/account/usage).

### `Cannot connect to OpenAI API.`

Check your internet connection.

### Scanned PDF pages not extracting

Install [Poppler](https://github.com/oschwartz10612/poppler-windows/releases) (Windows)
or `sudo apt install poppler-utils` (Linux/macOS). `pdf2image` requires Poppler.

### Image OCR not working (fallback mode)

Install [Tesseract OCR](https://github.com/tesseract-ocr/tesseract#installing-tesseract).
For best results, use the vision API (requires a vision-capable model like `gpt-4o`).

### File too large

Increase the limit in `.env`:

```
MAX_FILE_SIZE=100
```

Or compress/split the file.

### `filesolver` command not found

Make sure you activated your virtual environment:

```bash
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\Activate.ps1       # Windows PowerShell
```

---

## Running Tests

```bash
pytest
```

Tests use mock solvers — **no real API calls** are made. Safe for CI.

```bash
# With coverage
pytest --cov=filesolver --cov-report=term-missing
```

---

## Privacy

- Only the **extracted text** from your file is sent to the OpenAI API — not the original file.
- File Solver does **not** store, log, or transmit your files anywhere else.
- OpenAI may use API inputs for safety monitoring per their [privacy policy](https://openai.com/policies/privacy-policy).
- To use a completely local model with no data leaving your machine, implement a custom `BaseSolver` pointing to a local LLM (e.g. Ollama).

---

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Security

See [SECURITY.md](SECURITY.md) for the security policy and how to report vulnerabilities.

---

## License

[MIT](LICENSE) — free to use, modify, and distribute.
