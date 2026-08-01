import asyncio

import pytest
from pipelex.interpreter_hub import get_required_concept
from pipelex.pipeline.bundle_validator import BundleValidator


def test_boot():
    assert True


def test_concept_exists():
    assert get_required_concept("swe.OnboardingDocumentation") is not None


@pytest.mark.gha_disabled  # Requires model resolution which fails without configured backends
def test_dry_run_all_pipes():
    """Dry-run every pipe in the library loaded by the conftest fixture, expecting no errors."""
    # The session fixture already loaded + activated the pipeline libraries; sweep the current one.
    asyncio.run(BundleValidator().validate_current_library())
