# canvas-ap-world

Reads AP World History course materials from Canvas via the Canvas LMS API,
analyzes them, and generates new study material to facilitate learning and
practicing the content (study guides, practice questions, flashcards, etc.).

## How it works

1. **Ingest** — Pull course modules, pages, assignments, and files for an
   AP World course through the Canvas API.
2. **Analyze** — Extract structured content and key concepts from the raw
   course material.
3. **Generate** — Produce new learning aids (summaries, practice questions,
   exercises) from the analyzed material.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Configuration

Copy `.env.example` to `.env` and fill in your Canvas credentials:

- `CANVAS_API_URL` — e.g. `https://<yourschool>.instructure.com`
- `CANVAS_API_TOKEN` — generated in Canvas under Account → Settings →
  Approved Integrations
- `CANVAS_COURSE_ID` — the numeric Canvas course id for the AP World course

Never commit `.env` or API tokens.

## Usage

```bash
# List the courses visible to your token
ap-world list-courses

# Pull materials for the configured course into ./data
ap-world pull

# Analyze pulled materials and generate study aids
ap-world generate
```

## Development

```bash
# Run tests
.venv/bin/python -m pytest --tb=short -q

# Type check
.venv/bin/python -m mypy src
```