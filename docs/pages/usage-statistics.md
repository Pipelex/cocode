---
title: Usage Statistics
---

# Usage Statistics

cocode sends no usage statistics of its own. It runs its analyses on the Pipelex runtime, and Pipelex collects **anonymous usage statistics** from the Pipelex release that introduces them. Once cocode moves to that release, the runs it drives report through Pipelex's statistics and name cocode as their host, `"host": "cocode"`, so they can be told apart from the rest. Before that, nothing is sent.

cocode declares itself by setting `PIPELEX_USAGE_STATS_HOST=cocode` in its own process before it boots Pipelex, and keeps any value the environment already sets.

What Pipelex collects, what it never collects, where it goes and every way to turn it off are on Pipelex's [Usage Statistics](https://docs.pipelex.com/latest/setup/usage-statistics/) page. Each switch described there turns the statistics off for cocode too.
