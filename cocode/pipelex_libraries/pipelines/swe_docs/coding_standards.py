from typing import List, Optional

from pipelex.core.stuff_content import StructuredContent
from pydantic import Field


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
