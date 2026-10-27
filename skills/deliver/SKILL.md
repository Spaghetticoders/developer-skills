---
name: deliver
description: Turns a dirty working tree into disjoint, readable commits, with English messages. Never pushes unless told to, and when given a time it really commits and pushes at that time.
---

# Delivering

## The rules that don't change

- **Never push** unless the user says so. A commit is proposed, not taken for
  granted: yesterday's authorisation doesn't hold today.
- **Messages in English**, conventional commits.
- **Code comments in English**, even where the file next door has them in
  another language.
- **AI signatures in commits: the team decides, once.** If the team doesn't want
  them (`Co-Authored-By`, "Generated with" in commits, PRs and release notes),
  make it mechanical instead of trusting memory: turn attribution off in the
  Claude Code settings and add a `commit-msg` hook that rejects a message
  containing it.

```sh
# .git/hooks/commit-msg
grep -qiE 'co-authored-by:.*(claude|anthropic)|generated with' "$1" \
  && { echo "commit-msg: AI signature in the message"; exit 1; } || exit 0
```

## Before committing

1. **Sweep the junk**: `find . -name '._*' -not -path './.git/*' -delete` on
   ExFAT or network volumes, and check none of it made it into the index.
2. **Leave local files out.** Some projects have changes that must never be
   committed (framework swaps for the simulator, local xcconfigs). They are
   listed in the project docs. After the commit, **check they stayed out**.
3. **Check the language of added comments**, mechanically and not from memory.
   Example for people who work in Italian:

```sh
git diff | grep '^+' | grep -vE '^\+\+\+' | sed 's/^+//' | grep -E '^\s*(///|//)' \
  | grep -iE '\b(che|non|della|delle|una|perché|quindi|senza|già|questo|questa)\b'
```

   If it prints anything, you wrote it in Italian. It happens because the
   conversation is in Italian and you write in the language you think in: the
   check catches it, good intentions don't.

## Grouping

With many modified files, a single commit is unreadable. Partition them into
**disjoint** groups, one theme per commit, and check before running:

- every modified file is in exactly one group;
- no group names files that haven't changed.

A file touched by two different themes goes into one group only: pick the one
that tells the why, and mention the other in the message body.

## Commits at a given time

If the user says "commit at 17:54", the commit and the push must happen
**really at that time**, not earlier with a rewritten date.

Prepare the groups and the messages, schedule the run, and **don't touch the
files in those groups** until it has fired: the command adds whatever it finds
at that moment, so any other change in between would end up inside. Work on
other files while you wait, and check the log afterwards.

**And don't stage anything while you wait.** `git add <paths>` followed by
`git commit -F <file>` commits **the whole index**, not just the added paths:
work done in the meantime and staged would end up in the scheduled commit with
a message that has nothing to do with it. Before each scheduled time, check that
`git diff --cached --name-only` prints nothing.

**Verify afterwards, on the commits and not on the working state.** A file that
is still modified doesn't prove it wasn't committed earlier:
`git log --name-only --format=%h <base>..HEAD | grep '^ios/'` is the right question.

## The message

It says **what changes and why**, not which lines. If the fix comes from a
measurement, the measurement goes in the body: that's what makes the commit
useful six months from now.
