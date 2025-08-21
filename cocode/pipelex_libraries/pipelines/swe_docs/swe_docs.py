from typing import Dict, List, Optional

from pipelex.core.stuffs.stuff_content import StructuredContent
from pydantic import Field


class FundamentalsDoc(StructuredContent):
    project_overview: Optional[str] = Field(
        None,
        description="Mission, key features, architecture diagram, demo links",
    )
    core_concepts: Optional[Dict[str, str]] = Field(
        None,
        description=(
            "Names and definitions for project-specific terms, acronyms, data model names, background knowledge, business rules, domain entities"
        ),
    )
    repository_map: Optional[str] = Field(
        None,
        description="Directory layout explanation and purpose of each folder",
    )


class EnvironmentBuildDoc(StructuredContent):
    system_requirements: Optional[str] = Field(
        None,
        description="OS, CPU/GPU, RAM, disk, network assumptions",
    )
    quick_start_guide: Optional[str] = Field(
        None,
        description="One-command bootstrap or container setup instructions",
    )
    dependency_management: Optional[List[str]] = Field(
        None,
        description="Tooling and lock-file policy (poetry, npm, go mod, etc.)",
    )
    build_compile_instructions: Optional[str] = Field(
        None,
        description="Commands, Make targets, Gradle profiles, bundler configs",
    )
    env_variables_policy: Optional[str] = Field(
        None,
        description="Where secrets live and how to inject them safely",
    )
    ide_configurations: Optional[List[str]] = Field(
        None,
        description="Recommended editor presets and plugins",
    )


class CodingStandardsDoc(StructuredContent):
    code_style_guide: Optional[str] = Field(
        None,
        description="Naming rules, idioms, formatter config locations",
    )
    automatic_formatters: Optional[List[str]] = Field(
        None,
        description="Tools such as black, prettier; how to run locally/CI",
    )
    linters: Optional[List[str]] = Field(
        None,
        description="Static-analysis setup: ruff, ESLint, flake8, etc.",
    )
    type_checking: Optional[List[str]] = Field(
        None,
        description="pyright, mypy, TypeScript, build-time type provenance",
    )
    security_linters: Optional[List[str]] = Field(
        None,
        description="bandit, semgrep, secret-scan hooks, SAST policies",
    )
    commit_message_spec: Optional[str] = Field(
        None,
        description="Conventional commits or other commit-message guidelines",
    )


class TestingStrategyDoc(StructuredContent):
    test_pyramid_overview: Optional[str] = Field(
        None,
        description="Unit / integration / e2e boundaries and philosophy",
    )
    running_tests_locally: Optional[List[str]] = Field(
        None,
        description="Commands and tooling (pytest, jest, go test, Cypress)",
    )
    coverage_targets: Optional[str] = Field(
        None,
        description="Coverage goals and badge status",
    )
    fixtures_conventions: Optional[str] = Field(
        None,
        description="Fixture and test-data guidelines",
    )
    mocking_guidelines: Optional[str] = Field(
        None,
        description="How to use mocks, stubs or spies",
    )
    property_based_testing: Optional[str] = Field(
        None,
        description="Rules for property-based or fuzz testing",
    )
    performance_testing: Optional[str] = Field(
        None,
        description="Load-test scripts and usage",
    )


class CollaborationDoc(StructuredContent):
    branching_model: Optional[str] = Field(
        None,
        description="trunk-based, GitFlow, hybrid, etc.",
    )
    pull_request_checklist: Optional[List[str]] = Field(
        None,
        description="Items to tick before requesting review",
    )
    code_review_guidelines: Optional[str] = Field(
        None,
        description="Expectations for authors and reviewers",
    )
    issue_templates: Optional[List[str]] = Field(
        None,
        description="Bug, feature, tech-debt, security labels and templates",
    )
    code_of_conduct: Optional[str] = Field(
        None,
        description="Community behavior rules",
    )
    license_notice: Optional[str] = Field(
        None,
        description="License and third-party attributions",
    )


class OnboardingDocumentation(StructuredContent):
    fundamentals: Optional[FundamentalsDoc] = Field(None, description="Core project context and domain primer")
    environment_build: Optional[EnvironmentBuildDoc] = Field(None, description="Local environment requirements and build steps")
    coding_standards: Optional[CodingStandardsDoc] = Field(None, description="Style, linting, typing and security checks")
    testing_strategy: Optional[TestingStrategyDoc] = Field(None, description="Testing philosophy, organization, commands and targets")
    collaboration: Optional[CollaborationDoc] = Field(None, description="Branching, PR flow, issue templates and licenses")
