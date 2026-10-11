"""cocode's declaration to the anonymous usage statistics of the pipelex runtime it embeds.

cocode sends no statistics of its own: the pipelex runtime reports the runs cocode drives through its own client, and
cocode only names itself as their `host`, so those runs can be told apart from the rest. The declaration is the
`PIPELEX_USAGE_STATS_HOST` variable, which pipelex reads with its other usage-statistics switches when it boots, and
which every process cocode starts inherits. pipelex's statistics client also takes the declaration through a Python
call, but the variable is the route pipelex documents, and it works whatever pipelex release cocode pins: a release
that sends no statistics simply ignores it.
"""

import os

PIPELEX_USAGE_STATS_HOST_VAR = "PIPELEX_USAGE_STATS_HOST"
COCODE_USAGE_STATS_HOST = "cocode"


def declare_cocode_usage_stats_host() -> None:
    """Declare cocode as the program embedding pipelex, before cocode boots it.

    A host the environment already declares is kept: a program that starts cocode with its own declaration is the one
    the runs belong to.
    """
    os.environ.setdefault(PIPELEX_USAGE_STATS_HOST_VAR, COCODE_USAGE_STATS_HOST)
