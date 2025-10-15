import asyncio

from pipelex.hub import get_pipes, get_required_concept
from pipelex.pipe_run.dry_run import dry_run_pipes


def test_boot():
    assert True


def test_concept_exists():
    assert get_required_concept("swe.OnboardingDocumentation") is not None


def test_dry_run_all_pipes():
    """Test that dry_run_all_pipes() runs successfully without errors."""
    # This should not raise any exceptions
    asyncio.run(dry_run_pipes(get_pipes()))
