from typing import Dict, Optional

from pipelex.core.stuff_content import StructuredContent
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
