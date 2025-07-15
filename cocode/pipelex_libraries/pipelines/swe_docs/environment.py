from typing import List, Optional

from pipelex.core.stuff_content import StructuredContent
from pydantic import Field


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
