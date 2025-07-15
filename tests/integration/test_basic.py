from pipelex.hub import get_required_concept


def test_boot():
    assert True


def test_concept_exists():
    assert get_required_concept("swe.OnboardingDocumentation") is not None
