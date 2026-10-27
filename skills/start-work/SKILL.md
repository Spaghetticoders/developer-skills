---
name: start-work
description: Starts a piece of work from a list of tickets (Jira, Linear, ClickUp) or from a description. Reads the cards and their comments, writes a plan and stops to wait for the go-ahead. Then runs the full protocol (branch, development, tests, gui-test, audit rounds, report) without committing until told to.
---

# Starting a piece of work

Invoked with a list of tickets, or with a description in words. Everything else
in this file is the protocol: it applies even when the user doesn't repeat it.

## 1. Understand before planning

- **Read every card and its comments.** Comments hold course corrections the
  description doesn't: fix requests, decisions made in a call, Figma nodes.
  A card read without its comments is a card read halfway.
- **Check whether it's already done.** Before estimating, look at the code: a
  card sometimes describes something someone else has already closed. Checking
  costs a grep and changes the plan.
- Project facts (base branch, tracker, simulator, flavor, Figma file) live in
  the project docs: `AGENTS.md`, `CLAUDE.md`, the project memory. Read them,
  don't ask for them. Only ask for what really isn't there.

## 2. The plan, and then stop

A short plan: what changes, where, what breaks, what is still to be decided.
**Then stop and wait for the go-ahead.** Don't touch the code before that.

If reading raises a question that would change the plan, ask it now, not
halfway through the work.

## 3. Execution

Branch from the project's base branch, following the convention the repo
already uses (look at the latest branches: `git for-each-ref --sort=-committerdate refs/remotes`).

Then, for each slice: development → tests → **gui-test on the simulator** →
iterate until the screen is right. See `gui-test` and `figma-check`.

**Cases that can't be produced on demand get mocked.** If a condition needs data
the backend doesn't return (an empty profile, an expired cache, no network),
build a mock page in a developer menu, next to the project's other ones. It's
also how people who don't code get to try the case.

## 4. Audit rounds

Audit 1, 2, ... N. An *audit* means rereading the diff **and** rerunning tests
and gui-test, not just looking at the code.

**Stop when a whole round produces only cosmetic findings**: formatting, a stale
number in a doc. That's the sign the curve has flattened: the first rounds find
real defects, the last ones hygiene. Then one last security audit (what ends up
on disk, what in the logs, what survives logout) and one last round of tests.

Every fix must be verified with `verify-for-real`: break it and watch the test
fail before keeping it.

## 5. When the design looks wrong

**Stop and ask before implementing.** Don't invent copy or measurements, and
don't silently implement the version that looks right to you.

But don't block everything: do all the work that doesn't depend on that answer,
hold back only the uncertain piece, and ask at the right moment, not at the end
of the turn. If the user decides to deviate from Figma, **the deviation must be
written down** (code, docs, test) or someone will "restore" it by rereading the node.

## 6. Wrapping up

- **No commits and no pushes** until the user says so. See `deliver`.
- **No comments on the tickets** unless asked.
- A final report: what was done, which defects came up and how they were
  measured, what is still open and what is waiting for the user's decision.
