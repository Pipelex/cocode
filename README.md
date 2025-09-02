# Cocode ⚡️

*Cocode is the friend of your code*

Cocode is a powerful command-line tool for analyzing and processing code repositories. It converts repository structures and contents into text formats, extracts code interfaces, and performs software engineering analysis using **AI-powered pipelines** using [Pipelex](https://github.com/Pipelex/pipelex).

## ⚠️ Limitations

This tool is in early development! There are many things to fix and improve. You may encounter bugs, incomplete features, or unexpected behavior. We're actively working on making Cocode more robust and user-friendly.

If you run into issues or have suggestions, please check our [GitHub Issues](https://github.com/Pipelex/cocode/issues) section to report problems or see what we're working on.

## 🚀 Main Features

### 📝 **Automatic Documentation & Release Management**
Streamline your documentation workflow with AI-powered automation:
- **Automatic Changelog Generation**: Generate comprehensive changelogs from git diffs and version comparisons
- **Smart Documentation Updates**: Automatically update docs and README files based on releases and code changes
- **Documentation Proofreading**: Detect critical inconsistencies between documentation and actual codebase that could break user code

## 📦 Installation

```bash
pip install cocode
```

## ✅ Validation

```bash
# Verify setup and pipelines
cocode validate
```

### Set up environment variables

Enter your API keys into your `.env` file. The `OPENAI_API_KEY` is enough to get you started, but some pipelines require models from other providers.
Some complex pipelines require GCP credentials (See [GCP credentials](https://docs.pipelex.com/pages/build-reliable-ai-workflows-with-pipelex/ai-plugins-for-multi-llm-workflows/#4-google-vertex-ai-configuration) for more details), or Anthropic API keys `ANTHROPIC_API_KEY`.

## 🛠️ Quick Start

### Automatic Documentation & Release Features
```bash
# Update documentation based on code changes
cocode swe-doc-update v1.0.0 .

# Proofread documentation against codebase
cocode swe-doc-proofread --doc-dir docs .

# Generate changelog from version diff
cocode swe-from-repo-diff write_changelog v1.0.0 .

# Update AI instructions (AGENTS.md, CLAUDE.md, cursor rules) based on code changes
cocode swe-ai-instruction-update v1.0.0 .
```

### 📁 Output Location

The results of these commands will be saved in a `results` (default behavior) folder at the root of your project.

## 🔧 Other Features

### 🤖 **AI-Powered Software Engineering Analysis**
Leverage AI pipelines for advanced code understanding:
- Extract project fundamentals and architecture insights
- Generate comprehensive onboarding documentation
- Analyze software features and capabilities
- Create structured development guides

### 📊 **Repository Analysis**
Transform entire repositories into structured, analyzable formats:
- Convert codebases to text for AI processing and documentation
- Extract directory structures and file contents
- Filter by file types, paths, and patterns
- Multiple output formats for different use cases

### 🐍 **Smart Python Processing**
Intelligent Python code analysis with multiple extraction modes:
- **Interface Mode**: Extract class/function signatures and docstrings only
- **Imports Mode**: Analyze dependencies and import relationships  
- **Integral Mode**: Include complete source code

### 🎯 **Flexible Output Formats**
Choose the right format for your needs:
- **Repo Map**: Complete tree structure with file contents
- **Flat**: Clean content-only output
- **Tree**: Directory structure visualization
- **Import List**: Dependency analysis format

### Commands for Other Features

#### Basic Repository Analysis
```bash
# Converts repositories into AI-readable text formats
cocode repox

# Analyze specific project
cocode repox path/to/project --output-filename project-analysis.txt
```

#### Smart Code Extraction
```bash
# Extract Python interfaces only
cocode repox --python-rule interface

# Analyze import dependencies
cocode repox --python-rule imports --output-style import_list
```

#### AI-Powered Analysis
```bash
# Extract project fundamentals
cocode swe-from-repo extract_fundamentals . --output-filename overview.json

# Generate feature documentation
cocode swe-from-file extract_features_recap ./analysis.txt --output-filename features.md
```

## 🔧 Configuration

Cocode integrates with the [Pipelex](https://github.com/Pipelex/pipelex) framework for AI pipeline processing. Configuration files control default settings, output directories, and pipeline behaviors.

For detailed command options and advanced usage, see [CLI_README.md](CLI_README.md).

---

## Contact & Support

| Channel                                | Use case                                                                  |
| -------------------------------------- | ------------------------------------------------------------------------- |
| **GitHub Discussions → "Show & Tell"** | Share ideas, brainstorm, get early feedback.                              |
| **GitHub Issues**                      | Report bugs or request features.                                          |
| **Email (privacy & security)**         | [security@pipelex.com](mailto:security@pipelex.com)                       |
| **Discord**                            | Real-time chat — [https://go.pipelex.com/discord](https://go.pipelex.com/discord) |

## 📝 License

This project is licensed under the [MIT license](LICENSE). Runtime dependencies are distributed under their own licenses via PyPI.

---

*Happy coding!* 🚀
