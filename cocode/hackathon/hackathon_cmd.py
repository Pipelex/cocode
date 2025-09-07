"""
Hackathon analysis command implementation.
"""

import json
import os
from pathlib import Path
from typing import List, Optional

from pipelex import log, pretty_print
from pipelex.core.stuffs.stuff_content import TextContent
from pipelex.hub import get_pipeline_tracker, get_report_delegate
from pipelex.pipeline.execute import execute_pipeline

from cocode.github.github_repo_manager import GitHubRepoManager
from cocode.pipelex_libraries.pipelines.hackathon_analysis.hackathon_analysis import (
    HackathonAnalysis,
    HackathonAspects,
    HackathonFinalAnalysis,
    ProjectSummary,
)
from cocode.repox.models import OutputStyle
from cocode.repox.process_python import PythonProcessingRule
from cocode.repox.repox_cmd import repox_command


def _extract_repo_name(repo_path: str) -> str:
    """Extract a clean repo name from GitHub URL or local path for directory naming."""
    # Check if it's a GitHub URL or identifier
    if GitHubRepoManager.is_github_url(repo_path):
        try:
            owner, repo, _ = GitHubRepoManager.parse_github_url(repo_path)
            return f"{owner}_{repo}".replace("/", "_")
        except Exception:
            # Fallback to extracting from URL manually
            repo_name = repo_path.rstrip("/").split("/")[-1]
            if repo_name.endswith(".git"):
                repo_name = repo_name[:-4]
            return repo_name.replace("/", "_")
    else:
        # Local path - use directory name
        return Path(repo_path).name.replace("/", "_")


async def hackathon_analyze_repo(
    repo_path: str,
    ignore_patterns: Optional[List[str]],
    include_patterns: Optional[List[str]],
    path_pattern: Optional[str],
    python_processing_rule: PythonProcessingRule,
    output_style: OutputStyle,
    output_filename: str,
    output_dir: str,
    dry_run: bool = False,
) -> None:
    """Analyze a hackathon repository and generate HTML report."""

    log.info(f"Starting hackathon analysis for repository: {repo_path}")

    # Create subdirectory based on repo name
    repo_name = _extract_repo_name(repo_path)
    repo_output_dir = os.path.join(output_dir, repo_name)
    os.makedirs(repo_output_dir, exist_ok=True)
    log.info(f"Created output directory: {repo_output_dir}")

    # Step 1: Convert repository to text using repox
    log.info("Converting repository to text representation...")

    # Create a temporary text representation of the repo
    temp_filename = "temp_repo_content.txt"
    repox_command(
        repo_path=repo_path,
        ignore_patterns=ignore_patterns,
        include_patterns=include_patterns,
        path_pattern=path_pattern,
        python_processing_rule=python_processing_rule,
        output_style=output_style,
        output_filename=temp_filename,
        output_dir=repo_output_dir,  # Use the repo-specific directory
        to_stdout=False,
    )

    # Read the generated text content
    temp_file_path = os.path.join(repo_output_dir, temp_filename)
    try:
        with open(temp_file_path, "r", encoding="utf-8") as f:
            codebase_content = f.read()
    except FileNotFoundError:
        log.error(f"Failed to read temporary file: {temp_file_path}")
        raise
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

    if dry_run:
        log.info("Dry run mode - skipping pipeline execution")
        log.info(f"Would analyze codebase content of {len(codebase_content)} characters")
        return

    # Step 2: Run the hackathon analysis pipeline
    log.info("Running hackathon analysis pipeline...")

    try:
        pipe_output = await execute_pipeline(
            pipe_code="analyze_hackathon_project",
            input_memory={
                "codebase": TextContent(text=codebase_content),
            },
        )

        # Extract the HTML report from the pipeline output
        html_report = pipe_output.main_stuff_as(content_type=TextContent)

        # Step 3: Save the HTML report in the repo subdirectory
        html_output_path = os.path.join(repo_output_dir, output_filename)
        with open(html_output_path, "w", encoding="utf-8") as f:
            f.write(html_report.text)
        log.info(f"HTML report saved to: {html_output_path}")

        # Step 4: Assemble and save the complete analysis as JSON
        # Extract components from working memory
        project_summary_stuff = pipe_output.working_memory.get_stuff("project_summary")
        aspects_stuff = pipe_output.working_memory.get_stuff("aspects")
        final_analysis_stuff = pipe_output.working_memory.get_stuff("final_analysis")

        # Extract the content from each stuff
        project_summary = project_summary_stuff.content_as(content_type=ProjectSummary)
        aspects = aspects_stuff.content_as(content_type=HackathonAspects)
        final_analysis = final_analysis_stuff.content_as(content_type=HackathonFinalAnalysis)

        # Assemble the complete analysis in Python
        complete_analysis = HackathonAnalysis(
            project_summary=project_summary,
            feature_analysis=aspects.feature_analysis,
            architecture_analysis=aspects.architecture_analysis,
            code_quality_analysis=aspects.code_quality_analysis,
            security_analysis=aspects.security_analysis,
            x_factor_analysis=aspects.x_factor_analysis,
            overall_score=final_analysis.overall_score,
            final_verdict=final_analysis.final_verdict,
        )

        # Save as JSON
        json_filename = output_filename.replace(".html", ".json")
        json_output_path = os.path.join(repo_output_dir, json_filename)

        with open(json_output_path, "w", encoding="utf-8") as f:
            json.dump(complete_analysis.model_dump(), f, indent=2, ensure_ascii=False)
        log.info(f"Complete analysis JSON saved to: {json_output_path}")

        log.info(f"Hackathon analysis complete! Files saved to: {repo_output_dir}")

        # Display results
        pretty_print(pipe_output, title="Hackathon Analysis Results")
        get_report_delegate().generate_report()
        get_pipeline_tracker().output_flowchart()

    except Exception as e:
        log.error(f"Failed to run hackathon analysis pipeline: {e}")
        raise
