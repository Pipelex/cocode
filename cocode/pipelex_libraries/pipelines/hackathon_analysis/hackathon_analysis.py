"""Structured content models for hackathon codebase analysis."""

from typing import List, Optional

from pipelex.core.stuffs.stuff_content import StructuredContent
from pydantic import Field


class ProjectSummary(StructuredContent):
    """Summary of the hackathon project concept and purpose."""

    project_name: str = Field(..., description="Name of the project")
    concept: str = Field(..., description="Core concept and purpose of the project")
    target_audience: str = Field(..., description="Intended users or audience")
    key_value_proposition: str = Field(..., description="Main value the project provides")
    technology_stack: List[str] = Field(default_factory=list, description="Main technologies used")


class FeatureAnalysis(StructuredContent):
    """Analysis of project features - real vs fake functionality."""

    real_features: List[str] = Field(default_factory=list, description="Features with actual implementation")
    fake_features: List[str] = Field(default_factory=list, description="Features that are just UI mockups")
    partially_implemented: List[str] = Field(default_factory=list, description="Features with incomplete implementation")
    feature_depth_score: int = Field(..., description="Score 1-10 for feature implementation depth")
    evidence: str = Field(..., description="Evidence supporting the analysis")


class ArchitectureAnalysis(StructuredContent):
    """Analysis of code architecture and modularity."""

    architecture_pattern: str = Field(..., description="Main architectural pattern used")
    modularity_score: int = Field(..., description="Score 1-10 for code modularity")
    separation_of_concerns: str = Field(..., description="How well concerns are separated")
    code_organization: str = Field(..., description="Assessment of file and folder structure")
    design_patterns: List[str] = Field(default_factory=list, description="Design patterns identified")
    technical_debt: str = Field(..., description="Assessment of technical debt")


class CodeQualityAnalysis(StructuredContent):
    """Analysis of code quality metrics."""

    has_tests: bool = Field(..., description="Whether tests are present")
    test_coverage_estimate: str = Field(..., description="Estimated test coverage")
    has_typing: bool = Field(..., description="Whether type hints are used")
    has_linting: bool = Field(..., description="Whether linting is configured")
    has_ci_cd: bool = Field(..., description="Whether CI/CD is set up")
    documentation_quality: str = Field(..., description="Quality of documentation")
    code_style_consistency: str = Field(..., description="Consistency of code style")
    quality_score: int = Field(..., description="Overall quality score 1-10")


class SecurityAnalysis(StructuredContent):
    """Analysis of security vulnerabilities and issues."""

    vulnerabilities_found: List[str] = Field(default_factory=list, description="Security vulnerabilities identified")
    dependency_issues: List[str] = Field(default_factory=list, description="Dependency security issues")
    secrets_in_code: List[str] = Field(default_factory=list, description="Hardcoded secrets or credentials")
    security_best_practices: List[str] = Field(default_factory=list, description="Security practices followed")
    security_score: int = Field(..., description="Security score 1-10")
    recommendations: List[str] = Field(default_factory=list, description="Security improvement recommendations")


class XFactorAnalysis(StructuredContent):
    """Analysis of standout positive or negative elements."""

    positive_highlights: List[str] = Field(default_factory=list, description="Impressive or innovative aspects")
    negative_highlights: List[str] = Field(default_factory=list, description="Concerning or problematic aspects")
    innovation_score: int = Field(..., description="Innovation score 1-10")
    execution_quality: int = Field(..., description="Execution quality score 1-10")
    overall_impression: str = Field(..., description="Overall impression of the project")


class HackathonAspects(StructuredContent):
    """Analysis of aspects of Hackathon codebase."""

    feature_analysis: FeatureAnalysis = Field(..., description="Feature implementation analysis")
    architecture_analysis: ArchitectureAnalysis = Field(..., description="Architecture and modularity analysis")
    code_quality_analysis: CodeQualityAnalysis = Field(..., description="Code quality metrics")
    security_analysis: SecurityAnalysis = Field(..., description="Security assessment")
    x_factor_analysis: XFactorAnalysis = Field(..., description="Standout elements analysis")


class HackathonFinalAnalysis(StructuredContent):
    """Final hackathon codebase analysis."""

    overall_score: int = Field(..., description="Overall project score 1-100")
    final_verdict: str = Field(..., description="Final assessment and recommendation")


class HackathonAnalysis(StructuredContent):
    """Complete hackathon codebase analysis result."""

    project_summary: ProjectSummary = Field(..., description="Project concept summary")
    feature_analysis: FeatureAnalysis = Field(..., description="Feature implementation analysis")
    architecture_analysis: ArchitectureAnalysis = Field(..., description="Architecture and modularity analysis")
    code_quality_analysis: CodeQualityAnalysis = Field(..., description="Code quality metrics")
    security_analysis: SecurityAnalysis = Field(..., description="Security assessment")
    x_factor_analysis: XFactorAnalysis = Field(..., description="Standout elements analysis")
    overall_score: int = Field(..., description="Overall project score 1-100")
    final_verdict: str = Field(..., description="Final assessment and recommendation")
