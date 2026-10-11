---
title: Usage Statistics
---

# Usage Statistics

cocode sends no usage statistics of its own. It runs its analyses on the Pipelex runtime, which collects **anonymous usage statistics** from the Pipelex release whose changelog announces them: counts of runs, pipe types, models and tokens. Pipelex never collects your methods, prompts, inputs, outputs, file names or pipe names, so nothing of the code cocode reads is sent. What is collected, where it goes and every way to turn it off is on Pipelex's [Usage Statistics](https://docs.pipelex.com/latest/setup/usage-statistics/) page.

## cocode is named as the host

Each event can name the program that embeds Pipelex in its `host` property, so the runs that program drives can be told apart from the rest. Before it boots Pipelex, cocode sets `PIPELEX_USAGE_STATS_HOST=cocode` in its own process, so the runs it drives carry `"host": "cocode"`. A value the environment already sets is kept.

## Turning them off

Every switch Pipelex offers turns them off for cocode too. For example:

```bash
# For one cocode run
DO_NOT_TRACK=1 cocode changelog update v1.0.0

# For every Pipelex tool on this machine
pipelex usage-stats disable
```

The full list, which includes a project setting you can commit for everyone working in a repository, is in Pipelex's [Turning them off](https://docs.pipelex.com/latest/setup/usage-statistics/#turning-them-off) section.
