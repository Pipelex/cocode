---
title: Cocode
---

# Cocode

Repository analysis and AI-powered code understanding.

## What it does

- **Analyze repositories** - Convert code to text formats for analysis
- **Extract Python interfaces** - Get signatures, imports, or full code
- **AI analysis** - Generate docs, changelogs, and insights using LLMs
- **Git integration** - Analyze diffs and track changes

## Installation

```bash
pip install cocode
```

Cocode runs its AI workflows on your machine, with your own provider keys, and ships configured for OpenAI. Set your OpenAI API key in a `.env` file in the directory you run Cocode from:

```bash
echo "OPENAI_API_KEY=sk-..." > .env
```

To run on another provider, see [Getting Started](pages/getting-started.md#setup).

## Quick example

```bash
# Analyze current directory
cocode repox

# Extract Python interfaces
cocode repox --python-rule interface --include-pattern "*.py"

# Generate project overview with AI
cocode swe-from-repo extract_fundamentals .
```

## Learn more

- [Getting Started](pages/getting-started.md) - Installation and setup
- [Commands](pages/commands.md) - All available commands
- [Examples](pages/examples.md) - Common use cases

---

[GitHub](https://github.com/pipelex/cocode) | [Discord](https://go.pipelex.com/discord) | [PyPI](https://pypi.org/project/cocode/)
