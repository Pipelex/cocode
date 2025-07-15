from typing import Optional

from pipelex.core.stuff_content import StructuredContent
from pydantic import Field

from cocode.pipelex_libraries.pipelines.swe_docs.coding_standards import CodingStandardsDoc
from cocode.pipelex_libraries.pipelines.swe_docs.collaboration import CollaborationDoc
from cocode.pipelex_libraries.pipelines.swe_docs.environment import EnvironmentBuildDoc
from cocode.pipelex_libraries.pipelines.swe_docs.fundamentals import FundamentalsDoc
from cocode.pipelex_libraries.pipelines.swe_docs.testing_strategy import TestingStrategyDoc


class OnboardingDocumentation(StructuredContent):
    fundamentals: Optional[FundamentalsDoc] = Field(None, description="Core project context and domain primer")
    environment_build: Optional[EnvironmentBuildDoc] = Field(None, description="Local environment requirements and build steps")
    coding_standards: Optional[CodingStandardsDoc] = Field(None, description="Style, linting, typing and security checks")
    testing_strategy: Optional[TestingStrategyDoc] = Field(None, description="Testing philosophy, organization, commands and targets")
    collaboration: Optional[CollaborationDoc] = Field(None, description="Branching, PR flow, issue templates and licenses")
