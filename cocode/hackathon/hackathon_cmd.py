"""
Hackathon analysis command implementation.
"""

import os
from typing import List, Optional

from pipelex import log, pretty_print
from pipelex.core.stuffs.stuff_content import TextContent
from pipelex.hub import get_pipeline_tracker, get_report_delegate
from pipelex.pipeline.execute import execute_pipeline

from cocode.repox.models import OutputStyle
from cocode.repox.process_python import PythonProcessingRule
from cocode.repox.repox_cmd import repox_command


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
        output_dir=output_dir,
        to_stdout=False,
    )

    # Read the generated text content
    temp_file_path = os.path.join(output_dir, temp_filename)
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

        # Step 3: Save the HTML report
        output_path = os.path.join(output_dir, output_filename)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_report.text)

        log.info(f"Hackathon analysis complete! HTML report saved to: {output_path}")

        # Display results
        pretty_print(pipe_output, title="Hackathon Analysis Results")
        get_report_delegate().generate_report()
        get_pipeline_tracker().output_flowchart()

    except Exception as e:
        log.error(f"Failed to run hackathon analysis pipeline: {e}")
        raise
