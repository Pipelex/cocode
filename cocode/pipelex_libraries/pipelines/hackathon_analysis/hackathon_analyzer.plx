domain = "hackathon_analyzer"
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

[pipe.analyze_hackathon_project]
type = "PipeSequence"
definition = "Complete analysis of a hackathon codebase"
inputs = { codebase = "CodebaseContent" }
output = "HTMLReport"
steps = [
    { pipe = "summarize_hackathon_project", result = "project_summary" },
    { pipe = "analyze_aspects", result = "aspects" },
    { pipe = "final_hackathon_analysis", result = "final_analysis" },
    { pipe = "generate_hackathon_html_report", result = "html_report" }
]

[pipe.analyze_aspects]
type = "PipeParallel"
definition = "Analyze different apsects of the hackathon project"
inputs = { codebase = "CodebaseContent" }
output = "HackathonAspects"
parallels = [
    { pipe = "analyze_hackathon_features", result = "feature_analysis" },
    { pipe = "analyze_hackathon_architecture", result = "architecture_analysis" },
    { pipe = "analyze_hackathon_code_quality", result = "code_quality_analysis" },
    { pipe = "analyze_hackathon_security", result = "security_analysis" },
    { pipe = "identify_hackathon_x_factors", result = "x_factor_analysis" },
]
combined_output = "HackathonAspects"

[pipe.final_hackathon_analysis]
type = "PipeLLM"
definition = "Assess the overall score and final verdict"
inputs = { project_summary = "ProjectSummary", aspects = "HackathonAspects" }
output = "HackathonFinalAnalysis"
llm = { llm_handle = "blackboxai/google/gemini-2.5-pro", temperature = 0.2 }
system_prompt = "You are a hackathon judge who synthesizes multiple analysis reports into a final comprehensive assessment."
prompt_template = """
Synthesize the following project summary and detailed analyses into a final hackathon assessment.

Project Summary:
@project_summary

Detailed Analyses:
@aspects

Provide an overall score (1-100) and final verdict considering all aspects. Weight the scoring as follows:
- Features (30%): Real functionality vs mockups
- Architecture (20%): Code organization and design
- Code Quality (20%): Tests, documentation, best practices
- Security (15%): Vulnerabilities and security practices
- X-Factor (15%): Innovation and execution quality

Base your final verdict on the weighted score and provide constructive feedback.
"""

[pipe.summarize_hackathon_project]
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

[pipe.analyze_hackathon_features]
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

[pipe.analyze_hackathon_architecture]
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

[pipe.analyze_hackathon_code_quality]
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

[pipe.analyze_hackathon_security]
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

[pipe.identify_hackathon_x_factors]
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

[pipe.compile_hackathon_analysis]
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

[pipe.generate_hackathon_html_report]
type = "PipeJinja2"
definition = "Generate HTML report using Jinja2 template"
inputs = { project_summary = "ProjectSummary", aspects = "HackathonAspects", final_analysis = "HackathonFinalAnalysis" }
output = "HTMLReport"
jinja2 = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hackathon Analysis Report - {{ project_summary.project_name }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f7fa;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .overall-score {
            font-size: 3em;
            font-weight: bold;
            margin: 20px 0;
        }

        .score-circle {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            background: conic-gradient(#4CAF50 {{ final_analysis.overall_score * 3.6 }}deg, #ddd 0deg);
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
            position: relative;
        }

        .score-circle::before {
            content: '';
            width: 90px;
            height: 90px;
            border-radius: 50%;
            background: white;
            position: absolute;
        }

        .score-text {
            position: relative;
            z-index: 1;
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }

        .section {
            background: white;
            margin-bottom: 30px;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .section h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8em;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }

        .progress-bar {
            background: #e0e0e0;
            border-radius: 10px;
            height: 20px;
            margin: 10px 0;
            overflow: hidden;
        }

        .progress-fill {
            height: 100%;
            border-radius: 10px;
            transition: width 0.3s ease;
        }

        .score-good { background: #4CAF50; }
        .score-medium { background: #FF9800; }
        .score-poor { background: #f44336; }

        .metric {
            margin-bottom: 15px;
        }

        .metric-label {
            font-weight: bold;
            margin-bottom: 5px;
        }

        .tags {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin: 15px 0;
        }

        .tag {
            background: #667eea;
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.9em;
        }

        .tag.positive { background: #4CAF50; }
        .tag.negative { background: #f44336; }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
        }

        .verdict {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            font-size: 1.2em;
        }

        ul {
            margin-left: 20px;
        }

        li {
            margin-bottom: 8px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ project_summary.project_name }}</h1>
            <p>{{ project_summary.concept }}</p>

            <div class="score-circle">
                <div class="score-text">{{ final_analysis.overall_score }}/100</div>
            </div>

            <div class="tags">
                {% for tech in project_summary.technology_stack %}
                <span class="tag">{{ tech }}</span>
                {% endfor %}
            </div>
        </div>

        <div class="section">
            <h2>Executive Summary</h2>
            <p><strong>Target Audience:</strong> {{ project_summary.target_audience }}</p>
            <p><strong>Value Proposition:</strong> {{ project_summary.key_value_proposition }}</p>
            <div class="verdict">
                <h3>Final Verdict</h3>
                <p>{{ final_analysis.final_verdict }}</p>
            </div>
        </div>

        <div class="grid">
            <div class="section">
                <h2>Features Analysis</h2>
                <div class="metric">
                    <div class="metric-label">Feature Depth Score</div>
                    <div class="progress-bar">
                        <div class="progress-fill {% if aspects.feature_analysis.feature_depth_score >= 7 %}score-good{% elif aspects.feature_analysis.feature_depth_score >= 4 %}score-medium{% else %}score-poor{% endif %}"
                             style="width: {{ aspects.feature_analysis.feature_depth_score * 10 }}%"></div>
                    </div>
                    <span>{{ aspects.feature_analysis.feature_depth_score }}/10</span>
                </div>

                <h4>Real Features:</h4>
                <ul>
                    {% for feature in aspects.feature_analysis.real_features %}
                    <li>{{ feature }}</li>
                    {% endfor %}
                </ul>

                <h4>Fake/Mockup Features:</h4>
                <ul>
                    {% for feature in aspects.feature_analysis.fake_features %}
                    <li>{{ feature }}</li>
                    {% endfor %}
                </ul>

                <p><strong>Evidence:</strong> {{ aspects.feature_analysis.evidence }}</p>
            </div>

            <div class="section">
                <h2>Architecture & Modularity</h2>
                <div class="metric">
                    <div class="metric-label">Modularity Score</div>
                    <div class="progress-bar">
                        <div class="progress-fill {% if aspects.architecture_analysis.modularity_score >= 7 %}score-good{% elif aspects.architecture_analysis.modularity_score >= 4 %}score-medium{% else %}score-poor{% endif %}"
                             style="width: {{ aspects.architecture_analysis.modularity_score * 10 }}%"></div>
                    </div>
                    <span>{{ aspects.architecture_analysis.modularity_score }}/10</span>
                </div>

                <p><strong>Pattern:</strong> {{ aspects.architecture_analysis.architecture_pattern }}</p>
                <p><strong>Organization:</strong> {{ aspects.architecture_analysis.code_organization }}</p>
                <p><strong>Separation of Concerns:</strong> {{ aspects.architecture_analysis.separation_of_concerns }}</p>

                <div class="tags">
                    {% for pattern in aspects.architecture_analysis.design_patterns %}
                    <span class="tag">{{ pattern }}</span>
                    {% endfor %}
                </div>
            </div>

            <div class="section">
                <h2>Code Quality</h2>
                <div class="metric">
                    <div class="metric-label">Quality Score</div>
                    <div class="progress-bar">
                        <div class="progress-fill {% if aspects.code_quality_analysis.quality_score >= 7 %}score-good{% elif aspects.code_quality_analysis.quality_score >= 4 %}score-medium{% else %}score-poor{% endif %}"
                             style="width: {{ aspects.code_quality_analysis.quality_score * 10 }}%"></div>
                    </div>
                    <span>{{ aspects.code_quality_analysis.quality_score }}/10</span>
                </div>

                <p><strong>Tests:</strong> {% if aspects.code_quality_analysis.has_tests %}✅ Present{% else %}❌ Missing{% endif %}</p>
                <p><strong>Type Hints:</strong> {% if aspects.code_quality_analysis.has_typing %}✅ Present{% else %}❌ Missing{% endif %}</p>
                <p><strong>Linting:</strong> {% if aspects.code_quality_analysis.has_linting %}✅ Configured{% else %}❌ Not configured{% endif %}</p>
                <p><strong>CI/CD:</strong> {% if aspects.code_quality_analysis.has_ci_cd %}✅ Set up{% else %}❌ Not set up{% endif %}</p>
                <p><strong>Test Coverage:</strong> {{ aspects.code_quality_analysis.test_coverage_estimate }}</p>
                <p><strong>Documentation:</strong> {{ aspects.code_quality_analysis.documentation_quality }}</p>
            </div>

            <div class="section">
                <h2>Security Analysis</h2>
                <div class="metric">
                    <div class="metric-label">Security Score</div>
                    <div class="progress-bar">
                        <div class="progress-fill {% if aspects.security_analysis.security_score >= 7 %}score-good{% elif aspects.security_analysis.security_score >= 4 %}score-medium{% else %}score-poor{% endif %}"
                             style="width: {{ aspects.security_analysis.security_score * 10 }}%"></div>
                    </div>
                    <span>{{ aspects.security_analysis.security_score }}/10</span>
                </div>

                {% if aspects.security_analysis.vulnerabilities_found %}
                <h4>Vulnerabilities Found:</h4>
                <ul>
                    {% for vuln in aspects.security_analysis.vulnerabilities_found %}
                    <li class="tag negative">{{ vuln }}</li>
                    {% endfor %}
                </ul>
                {% endif %}

                {% if aspects.security_analysis.security_best_practices %}
                <h4>Security Practices:</h4>
                <div class="tags">
                    {% for practice in aspects.security_analysis.security_best_practices %}
                    <span class="tag positive">{{ practice }}</span>
                    {% endfor %}
                </div>
                {% endif %}

                {% if aspects.security_analysis.recommendations %}
                <h4>Recommendations:</h4>
                <ul>
                    {% for rec in aspects.security_analysis.recommendations %}
                    <li>{{ rec }}</li>
                    {% endfor %}
                </ul>
                {% endif %}
            </div>

            <div class="section">
                <h2>X-Factor Analysis</h2>
                <div class="metric">
                    <div class="metric-label">Innovation Score</div>
                    <div class="progress-bar">
                        <div class="progress-fill {% if aspects.x_factor_analysis.innovation_score >= 7 %}score-good{% elif aspects.x_factor_analysis.innovation_score >= 4 %}score-medium{% else %}score-poor{% endif %}"
                             style="width: {{ aspects.x_factor_analysis.innovation_score * 10 }}%"></div>
                    </div>
                    <span>{{ aspects.x_factor_analysis.innovation_score }}/10</span>
                </div>

                <div class="metric">
                    <div class="metric-label">Execution Quality</div>
                    <div class="progress-bar">
                        <div class="progress-fill {% if aspects.x_factor_analysis.execution_quality >= 7 %}score-good{% elif aspects.x_factor_analysis.execution_quality >= 4 %}score-medium{% else %}score-poor{% endif %}"
                             style="width: {{ aspects.x_factor_analysis.execution_quality * 10 }}%"></div>
                    </div>
                    <span>{{ aspects.x_factor_analysis.execution_quality }}/10</span>
                </div>

                {% if aspects.x_factor_analysis.positive_highlights %}
                <h4>Positive Highlights:</h4>
                <div class="tags">
                    {% for highlight in aspects.x_factor_analysis.positive_highlights %}
                    <span class="tag positive">{{ highlight }}</span>
                    {% endfor %}
                </div>
                {% endif %}

                {% if aspects.x_factor_analysis.negative_highlights %}
                <h4>Areas for Improvement:</h4>
                <div class="tags">
                    {% for highlight in aspects.x_factor_analysis.negative_highlights %}
                    <span class="tag negative">{{ highlight }}</span>
                    {% endfor %}
                </div>
                {% endif %}

                <p><strong>Overall Impression:</strong> {{ aspects.x_factor_analysis.overall_impression }}</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

