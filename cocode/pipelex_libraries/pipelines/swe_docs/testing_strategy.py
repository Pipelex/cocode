from typing import List, Optional

from pipelex.core.stuff_content import StructuredContent
from pydantic import Field


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
