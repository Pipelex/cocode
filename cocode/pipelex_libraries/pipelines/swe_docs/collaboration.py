from typing import List, Optional

from pipelex.core.stuff_content import StructuredContent
from pydantic import Field


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
