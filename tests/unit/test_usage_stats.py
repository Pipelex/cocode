import os

import pytest
from pytest_mock import MockerFixture
from typer import Context as TyperContext

from cocode.cli.main import main
from cocode.usage_stats import COCODE_USAGE_STATS_HOST, PIPELEX_USAGE_STATS_HOST_VAR


class TestUsageStatsHost:
    @pytest.mark.parametrize(
        ("declared_host", "expected_host_at_boot"),
        [
            (None, COCODE_USAGE_STATS_HOST),
            ("mthds-agent", "mthds-agent"),
        ],
    )
    def test_host_is_declared_before_pipelex_boots(self, mocker: MockerFixture, declared_host: str | None, expected_host_at_boot: str) -> None:
        """The CLI declares `cocode` as the host before it boots pipelex, and keeps a host the environment already declares."""
        mocker.patch.dict(os.environ)
        os.environ.pop(PIPELEX_USAGE_STATS_HOST_VAR, None)
        if declared_host is not None:
            os.environ[PIPELEX_USAGE_STATS_HOST_VAR] = declared_host

        hosts_seen_at_boot: list[str | None] = []

        def record_host_at_boot(**_kwargs: object) -> None:
            hosts_seen_at_boot.append(os.environ.get(PIPELEX_USAGE_STATS_HOST_VAR))

        mocker.patch("cocode.cli.main.Pipelex.make", side_effect=record_host_at_boot)
        ctx = mocker.Mock(spec=TyperContext)
        ctx.invoked_subcommand = "validate"

        main(ctx=ctx)

        assert hosts_seen_at_boot == [expected_host_at_boot]
