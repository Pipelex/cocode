import asyncio

import pytest
from pipelex.hub import get_required_concept

from cocode.validation_cli import dry_run_all_pipes


def test_boot():
    assert True


def test_concept_exists():
    assert get_required_concept("swe.OnboardingDocumentation") is not None


@pytest.mark.gha_disabled  # Requires model resolution which fails without configured backends
def test_dry_run_all_pipes():
    """Test that dry_run_all_pipes() runs successfully without errors."""
    # This should not raise any exceptions
    asyncio.run(dry_run_all_pipes())
