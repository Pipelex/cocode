domain = "swe"
definition = "Pipelines for software engineering tasks."

[concept]
SoftwareDoc = "Documentation related to software engineering projects or codebases."
InconsistencyReport = "A text report enumerating any inconsistencies detected within the provided documentation."
SoftwareFeaturesRecap = "A comprehensive overview of software features highlighting key capabilities, strengths, and limitations without technical implementation details."
FundamentalsDoc = "A comprehensive overview of the fundamental concepts and principles of software engineering."
EnvironmentBuildDoc = "A comprehensive overview of the environment and build setup for a software project."
CodingStandardsDoc = "A comprehensive overview of the coding standards and best practices for a software project."
TestStrategyDoc = "A comprehensive overview of the testing strategy and procedures for a software project."
ContextualGuidelinesDoc = "A comprehensive overview of the contextual development guidelines and conventions for a software project."
CollaborationDoc = "A comprehensive overview of the collaboration and workflow information for a software project."
OnboardingDocumentation = "Complete set of documentation needed for onboarding new developers to a project."

[pipe]
[pipe.check_docs_consistency]
type = "PipeLLM"
definition = "Identify inconsistencies in a set of software engineering documents."
inputs = { repo_text = "SoftwareDoc" }
output = "InconsistencyReport"
llm = "llm_for_swe"
system_prompt = """
You are an expert technical writer and software architect. Your task is to carefully review software documentation and point out any inconsistencies or contradictions.
"""
prompt_template = """
Analyze the following documentation snippets. Highlight every occurrence where statements contradict each other, create ambiguity, or provide conflicting information.

@repo_text

Reply with a numbered list where each item contains:
1. The conflicting or ambiguous excerpts quoted exactly (you may truncate long excerpts with ellipsis … while keeping enough context).
2. A concise explanation (1-2 sentences) of why these excerpts are inconsistent.

If you find no inconsistencies, reply exactly: "No inconsistencies detected.".
"""

[pipe.extract_onboarding_documentation]
type = "PipeParallel"
definition = "Extract comprehensive onboarding documentation from software project docs"
inputs = { repo_text = "SoftwareDoc" }
output = "OnboardingDocumentation"
parallels = [
    { pipe = "extract_fundamentals", result = "fundamentals" },
    { pipe = "extract_environment_build", result = "environment_build" },
    { pipe = "extract_coding_standards", result = "coding_standards" },
    { pipe = "extract_test_strategy", result = "test_strategy" },
    { pipe = "extract_collaboration", result = "collaboration" },
]
combined_output = "swe.OnboardingDocumentation"

[pipe.extract_fundamentals]
type = "PipeLLM"
definition = "Extract fundamental project information from documentation"
inputs = { repo_text = "SoftwareDoc" }
output = "FundamentalsDoc"
llm = "llm_for_swe"
system_prompt = """
You are an expert at extracting structured project information from software documentation. Focus on identifying core project context and foundational information.
"""
prompt_template = """
Extract fundamental project information from the following documentation:

@repo_text

Please extract and structure the following information (if available in the documentation):

- Project Overview: Mission, key features, architecture overview, demo links
- Core Concepts: Name and definition for project-specific terms, acronyms, data model names, background knowledge, business rules, domain entities.
- Repository Map: Directory layout explanation and purpose of each folder

Return the information in a structured format. If any category is not found in the documentation, omit it from the response.
"""

[pipe.extract_environment_build]
type = "PipeLLM"
definition = "Extract environment setup and build information from documentation"
inputs = { repo_text = "SoftwareDoc" }
output = "EnvironmentBuildDoc"
llm = "llm_for_swe"
system_prompt = """
You are an expert at extracting development environment setup information from software documentation.
"""
prompt_template = """
Extract environment and build setup information from the following documentation:

@repo_text

Please extract and structure the following information (if available):

1. Prerequisites: OS requirements, language runtimes, system-level dependencies
2. Installation Commands: Package managers, dependency installation steps
3. Environment Configuration: Environment variables, configuration files setup
4. Build Commands: Compilation, asset generation, container build steps
5. Run Commands: Local server startup, watching, hot-reload commands

Return the information in a structured format. If any category is not found, omit it from the response.
"""

[pipe.extract_coding_standards]
type = "PipeLLM"
definition = "Extract code quality and style information from documentation"
inputs = { repo_text = "SoftwareDoc" }
output = "CodingStandardsDoc"
llm = "llm_for_swe"
system_prompt = """
You are an expert at extracting code quality standards and tooling information from software documentation.
"""
prompt_template = """
Extract code quality and style information from the following documentation:

@repo_text

Please extract and structure the following information (if available):

1. Code Style Guide: Naming rules, idioms, formatter configuration locations
2. Automatic Formatters: Tools like black, prettier; how to run locally/CI
3. Linters: Static analysis setup like ruff, ESLint, flake8, etc.
4. Type Checking: pyright, mypy, TypeScript, build-time type provenance
5. Security Linters: bandit, semgrep, secret-scan hooks, SAST policies
6. Commit Message Spec: Conventional commits or other guidelines

Return the information in a structured format. If any category is not found, omit it from the response.
"""

[pipe.extract_test_strategy]
type = "PipeLLM"
definition = "Extract testing strategy and procedures from documentation"
inputs = { repo_text = "SoftwareDoc" }
output = "TestStrategyDoc"
llm = "llm_for_swe"
system_prompt = """
You are an expert at extracting testing strategies and procedures from software documentation.
"""
prompt_template = """
Extract testing strategy information from the following documentation:

@repo_text

Please extract and structure the following information (if available):

1. Test Philosophy: Unit vs integration strategy, TDD approach, coverage targets
2. Unit Test Commands: Commands to run unit tests locally and in CI
3. Integration Test Commands: Commands for end-to-end, API, or database tests
4. Test Data Setup: Fixtures, factories, database seeding procedures
5. Performance Benchmarks: Load testing, profiling tools, performance criteria

Return the information in a structured format. If any category is not found, omit it from the response.
"""

[pipe.extract_contextual_guidelines]
type = "PipeLLM"
definition = "Extract contextual development guidelines from documentation"
inputs = { repo_text = "SoftwareDoc" }
output = "ContextualGuidelinesDoc"
llm = "llm_for_swe"
system_prompt = """
You are an expert at extracting contextual development guidelines and conventions from software documentation.
"""
prompt_template = """
Extract contextual guidelines from the following documentation:

@repo_text

Please extract and structure the following information (if available):

1. Path-Specific Rules: Special conventions for specific directories or modules
2. Topic-Specific Rules: Guidelines for security, API design, database patterns
3. Framework Conventions: React patterns, Django best practices, etc.

Return the information in a structured format. If any category is not found, omit it from the response.
"""

[pipe.extract_collaboration]
type = "PipeLLM"
definition = "Extract collaboration and workflow information from documentation"
inputs = { repo_text = "SoftwareDoc" }
output = "CollaborationDoc"
llm = "llm_for_swe"
system_prompt = """
You are an expert at extracting collaboration processes and workflow information from software documentation.
"""
prompt_template = """
Extract collaboration and workflow information from the following documentation:

@repo_text

Please extract and structure the following information (if available):

1. Branching Strategy: Git flow, feature branches, main/develop conventions
2. Pull Request Process: Review requirements, approval process, merge policies
3. Issue Templates: Bug report, feature request, documentation templates
4. Release Process: Versioning, changelog, deployment workflow
5. License Information: Project license, attribution requirements, copyright

Return the information in a structured format. If any category is not found, omit it from the response.
"""

[pipe.extract_features_recap]
type = "PipeLLM"
definition = "Extract and analyze software features from documentation to create a comprehensive feature overview"
inputs = { repo_text = "SoftwareDoc" }
output = "SoftwareFeaturesRecap"
llm = "llm_for_swe"
system_prompt = """
You are a product analyst and technical writer specializing in software feature analysis. Your task is to analyze software documentation and create compelling feature presentations that highlight capabilities, strengths, and potential limitations.
"""
prompt_template = """
Analyze the following software documentation and create a comprehensive features recap:

@repo_text

Please extract and present the following information in a clear, structured format:

1. **Core Features Overview**: List and describe the main features and capabilities of the software
2. **Key Strengths**: Highlight what makes this software particularly strong or unique
3. **Notable Capabilities**: Special functionalities, integrations, or advanced features that stand out
4. **Potential Limitations**: Areas where the software might have constraints or trade-offs
5. **Use Case Suitability**: What types of users or scenarios this software is best suited for

Guidelines:
- Focus on WHAT the software does, not HOW it's implemented
- Avoid code examples, technical implementation details, or setup instructions
- Present features from a user/business perspective
- Be objective about both strengths and limitations
- Use clear, non-technical language where possible
- Structure the response for easy reading and presentation

If insufficient information is available in the documentation to assess features comprehensively, indicate which aspects need additional information.
"""

