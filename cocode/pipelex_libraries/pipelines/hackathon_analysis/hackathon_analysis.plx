domain = "hackathon_analysis"
definition = "Pipeline to analyze hackathon codebases for features, architecture, quality, security, and X-factors"

[concept]
CodebaseContent = "Text representation of a codebase including file structure and code"
ProjectSummary = "Summary of the hackathon project concept and purpose"
FeatureAnalysis = "Analysis of project features - real vs fake functionality"
ArchitectureAnalysis = "Analysis of code architecture and modularity"
CodeQualityAnalysis = "Analysis of code quality metrics"
SecurityAnalysis = "Analysis of security vulnerabilities and issues"
XFactorAnalysis = "Analysis of standout positive or negative elements"
HackathonAnalysis = "Complete hackathon codebase analysis result"
HTMLReport = "HTML formatted analysis report"

[pipe.analyze_codebase_v2]
type = "PipeSequence"
definition = "Complete analysis of a hackathon codebase"
inputs = { codebase = "CodebaseContent" }
output = "HTMLReport"
steps = [
    { pipe = "summarize_project_v2", result = "project_summary" },
    { pipe = "analyze_features_v2", result = "feature_analysis" },
    { pipe = "analyze_architecture_v2", result = "architecture_analysis" },
    { pipe = "analyze_code_quality_v2", result = "code_quality_analysis" },
    { pipe = "analyze_security_v2", result = "security_analysis" },
    { pipe = "identify_x_factors_v2", result = "x_factor_analysis" },
    { pipe = "compile_analysis_v2", result = "complete_analysis" },
    { pipe = "generate_html_report_v2", result = "html_report" }
]

[pipe.summarize_project_v2]
type = "PipeLLM"
definition = "Analyze and summarize the project concept"
inputs = { codebase = "CodebaseContent" }
output = "ProjectSummary"
llm = { llm_handle = "blackboxai/google/gemini-2.5-pro", temperature = 0.2 }
system_prompt = "You are an expert at analyzing software projects and understanding their core concepts and purposes."
prompt_template = """
Analyze this hackathon codebase and provide a comprehensive project summary.

Focus on:
- Project name and core concept
- Target audience and use cases
- Key value proposition
- Technology stack used

@codebase

Provide a clear, concise summary of what this project is trying to achieve.
"""

[pipe.analyze_features_v2]
type = "PipeLLM"
definition = "Analyze whether features are real implementations or just UI mockups"
inputs = { codebase = "CodebaseContent" }
output = "FeatureAnalysis"
llm = { llm_handle = "blackboxai/google/gemini-2.5-pro", temperature = 0.1 }
system_prompt = "You are an expert at distinguishing between real feature implementations and fake/mockup features in codebases."
prompt_template = """
Analyze this codebase to determine which features are actually implemented vs just UI mockups.

Look for:
- Real backend logic and data processing
- Actual API endpoints with business logic
- Database operations and data persistence
- vs. Static UI components without functionality
- Hardcoded data instead of dynamic content
- Missing backend implementations

@codebase

Categorize features as real, fake, or partially implemented. Provide evidence for your assessment.
"""

[pipe.analyze_architecture_v2]
type = "PipeLLM"
definition = "Evaluate code architecture and modularity"
inputs = { codebase = "CodebaseContent" }
output = "ArchitectureAnalysis"
llm = { llm_handle = "blackboxai/google/gemini-2.5-pro", temperature = 0.2 }
system_prompt = "You are a software architecture expert specializing in code organization and design patterns."
prompt_template = """
Analyze the architecture and modularity of this codebase.

Evaluate:
- Overall architectural pattern (MVC, microservices, monolith, etc.)
- Code organization and file structure
- Separation of concerns
- Modularity and reusability
- Design patterns used
- Technical debt and code smells

@codebase

Provide scores and detailed analysis of the architectural quality.
"""

[pipe.analyze_code_quality_v2]
type = "PipeLLM"
definition = "Assess code quality metrics including tests, typing, documentation"
inputs = { codebase = "CodebaseContent" }
output = "CodeQualityAnalysis"
llm = { llm_handle = "blackboxai/google/gemini-2.5-pro", temperature = 0.1 }
system_prompt = "You are a code quality expert who evaluates testing, documentation, and development practices."
prompt_template = """
Analyze the code quality of this hackathon project.

Check for:
- Unit tests and test coverage
- Integration tests
- Type hints and static typing
- Linting configuration (eslint, pylint, etc.)
- CI/CD setup
- Documentation quality (README, docstrings, comments)
- Code style consistency
- Error handling

@codebase

Provide a comprehensive quality assessment with specific examples.
"""

[pipe.analyze_security_v2]
type = "PipeLLM"
definition = "Identify security vulnerabilities and issues"
inputs = { codebase = "CodebaseContent" }
output = "SecurityAnalysis"
llm = { llm_handle = "blackboxai/google/gemini-2.5-pro", temperature = 0.1 }
system_prompt = "You are a cybersecurity expert specializing in code security analysis and vulnerability assessment."
prompt_template = """
Perform a security analysis of this hackathon codebase.

Look for:
- Common vulnerabilities (SQL injection, XSS, CSRF, etc.)
- Hardcoded secrets, API keys, passwords
- Insecure dependencies or outdated packages
- Missing authentication/authorization
- Insecure data handling
- Missing input validation
- Security best practices followed

@codebase

Identify specific security issues and provide recommendations for improvement.
"""

[pipe.identify_x_factors_v2]
type = "PipeLLM"
definition = "Identify standout positive or negative elements"
inputs = { codebase = "CodebaseContent" }
output = "XFactorAnalysis"
llm = { llm_handle = "blackboxai/google/gemini-2.5-pro", temperature = 0.3 }
system_prompt = "You are an expert judge at hackathons who can identify what makes projects stand out positively or negatively."
prompt_template = """
Analyze this hackathon project for X-factors - elements that make it stand out.

Look for:
POSITIVE:
- Innovative approaches or creative solutions
- Impressive technical implementation
- Unique features or use cases
- Exceptional code quality or architecture
- Creative use of technologies
- Polished user experience

NEGATIVE:
- Major technical flaws or bugs
- Poor user experience
- Overly complex or convoluted solutions
- Missing core functionality
- Security vulnerabilities
- Plagiarism or copied code

@codebase

Identify what makes this project memorable (good or bad) and rate innovation and execution quality.
"""

[pipe.compile_analysis_v2]
type = "PipeLLM"
definition = "Compile all individual analyses into a comprehensive result"
inputs = { project_summary = "ProjectSummary", feature_analysis = "FeatureAnalysis", architecture_analysis = "ArchitectureAnalysis", code_quality_analysis = "CodeQualityAnalysis", security_analysis = "SecurityAnalysis", x_factor_analysis = "XFactorAnalysis" }
output = "HackathonAnalysis"
llm = { llm_handle = "blackboxai/google/gemini-2.5-pro", temperature = 0.2 }
system_prompt = "You are a hackathon judge who synthesizes multiple analysis reports into a final comprehensive assessment."
prompt_template = """
Compile the following individual analyses into a comprehensive hackathon project assessment.

Project Summary:
@project_summary

Feature Analysis:
@feature_analysis

Architecture Analysis:
@architecture_analysis

Code Quality Analysis:
@code_quality_analysis

Security Analysis:
@security_analysis

X-Factor Analysis:
@x_factor_analysis

Provide an overall score (1-100) and final verdict considering all aspects. Weight the scoring as follows:
- Features (30%): Real functionality vs mockups
- Architecture (20%): Code organization and design
- Code Quality (20%): Tests, documentation, best practices
- Security (15%): Vulnerabilities and security practices
- X-Factor (15%): Innovation and execution quality
"""

[pipe.generate_html_report_v2]
type = "PipeLLM"
definition = "Generate HTML report using Jinja2 template"
inputs = { complete_analysis = "HackathonAnalysis" }
output = "HTMLReport"
llm = { llm_handle = "blackboxai/google/gemini-2.5-pro", temperature = 0.1 }
system_prompt = "You are an expert at creating professional HTML reports with clean styling and clear presentation."
prompt_template = """
Generate a professional HTML report for this hackathon analysis using clean, modern styling.

Analysis Data:
@complete_analysis

Create an HTML page with:
- Professional header with project name and overall score
- Executive summary section
- Detailed sections for each analysis area with visual indicators
- Score visualizations (progress bars or similar)
- Clean, responsive CSS styling
- Professional color scheme
- Clear typography and spacing

Make it look like a professional assessment report that judges would want to read.
"""

