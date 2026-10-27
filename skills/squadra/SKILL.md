---
name: squadra
description: Takes a request to the finish line with a team of coordinated teammates (agent team) around a shared board. Analyst, pixel-perfect, developer, reviewer, tester and approver work through gates, in a loop, until the work is perfect. Use when the job is worth more than one head.
---

# Working as a team

A team of agents around a board. It isn't "more agents because there are many":
it's **separating who writes from who checks**, because whoever just wrote a
line is the person least suited to spot its defect.

The team is an **agent team**, not a row of throwaway subagents: every member
has a name, stays alive between rounds, and talks to the others. It needs
`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in the environment (for example in
`~/.zshrc`); without it, a named agent is just a regular subagent and the
protocol degrades to "the PM acts as the bridge" (see *The long loop*).

It costs: a teammate is a whole instance, more expensive than a subagent. A full
round is 6-10 agents and several minutes. A three-line fix doesn't call for the
team: you make it, break it, and watch the test fail.

---

## How they actually talk to each other

Three things, and it's worth knowing them before promising more.

**The board.** An append-only file, one per piece of work:
`<scratchpad>/squadra/<slug>/BOARD.md`. Every agent **reads it in full at the
start** and it's the shared memory: the only thing that survives the session,
and so the only source of truth. A message between two agents that doesn't make
it onto the board didn't happen.

**Whoever can, writes to it.** The read-only agents (analyst, pixel, tester,
approver) **don't have the tools to append**, and that's intended: if you gave
them the tools for the board, they'd have them for the repo too. So they **end
their turn with the block already formatted, ready to paste**, and **the PM
appends it for them**. The PM is the meeting's secretary, not the participants.

**Teammates talk to each other by name.** They're spawned with `Agent` + `name`
(`dev`, `reviewer`, `tester`, `pixel`, …) and they write with `SendMessage` to
that name. **There's no broadcast**: one message, one recipient. Along the loop
the baton passes **directly**: the dev who finishes writes to the reviewer, the
reviewer to the tester. Two rules, so the PM doesn't lose track:

- whoever passes the baton **also** sends the PM one line (what they did, who
  they passed it to), and the PM puts it on the board;
- **a successful `SendMessage` ≠ read.** A dev once sat idle for 35 minutes on
  an authorisation already given. If an agent says it's blocked on something
  already decided, resend the message instead of assuming.

When a teammate ends its turn, **the idle notice reaches the PM by itself**,
with its final answer inside: the PM doesn't build waiters or wait for prose. It
reads the notice, reads the tree, appends.

An **idle teammate isn't dead**: it stays reachable, and a `SendMessage` resumes
it with all its context. The second-round reviewer is **the same one** as the
first, and remembers its findings: that's why the team costs less than it
seems. The only intended exception is the approver, who must be new.

**The shared task list.** Teammates have `TaskCreate` / `TaskList` /
`TaskUpdate`: one slice = one task, whoever takes it marks it in progress,
whoever closes it marks it done. It's the who-does-what table; **it doesn't
replace the board**, which stays the reasoned record. The PM might not see
those tools in its own session (in some versions they don't show up for the
lead): in that case it reads them through the board and doesn't build on them.

**The PM is the main session, not an agent.** An intentional deviation, and the
reason is that only the main session can: ask the user, hold `flutter run` and
the simulator, relaunch an agent, and stay alive between rounds. A spawned PM
would be a teammate that can do none of that. The PM **doesn't do the team's
work**: while a teammate is working, the PM waits for the notice, it doesn't
start writing itself.

### The board format

```markdown
# <slug> — <the request in one line>
Branch: <branch>   Started: <date time>

## Request
<the user's text, verbatim>

## Team
dev · reviewer · tester · pixel   (teammate names, as spawned)

## Log
### [time] ANALYST — <outcome in three words>
- **Found:** …
- **Open:** …
- **For:** dev / pixel / tester
```

One entry per agent per round, with the machine time (`date`) at the top.
**No summaries of the board inside the board**: you append, you don't rewrite.

---

## The roles

Each one gets from the PM: its name, the board path, its task in three lines,
the names of the others and **what it has to produce**. Nobody gets "do your best".

| # | role | does | doesn't |
|---|---|---|---|
| 1 | **PM** (main session, team lead) | coordinates, opens and closes gates, restarts the loop, asks the user when blocked | doesn't write code |
| 2 | **Functional analyst** | reads the request **and** the code, enumerates use cases, finds holes in the logic | doesn't fix |
| 3 | **Pixel-perfect** | compares every screen with the Figma node, measures, has **veto power** over the UI | doesn't touch logic |
| 4 | **Developer** | writes the code | doesn't approve itself |
| 5 | **Reviewer + unit tests** | writes unit tests, rereads the dev's logic, judges quality | doesn't rewrite the feature |
| 6 | **Functional tester** | exercises every use case, on the simulator when it's UI | doesn't fix |
| 7 | **Approver** | rereads everything at the end of the round: **APPROVE** or **ITERATE** with specific findings | isn't a rubber stamp |
| 8 | **Archivist** | only after the OK: project memories, docs, Claude's memory | doesn't start early |

The PM can spawn others when a skill is missing (security, performance,
accessibility, backend). Same rule: narrow task, declared output.

**Ceiling.** No more than **5-6** alive at once: a role is spawned when its gate
is getting close, not all at the start. In total a round stays under 15 agents;
if it needs more, the work gets split into two jobs, not inflated.

**One file, one owner.** Two teammates writing the same file overwrite each
other, and nobody notices. The PM assigns slices by file, and writes it on the board.

---

## The protocol

Gates, not phases. **A gate doesn't open until its criterion is true**, and the
criterion is written down, not a feeling.

**0. Opening.** The PM creates the board, copies the request *verbatim*, and
reads the state of the repo (the branch starts from `origin/main`, not the local
`main`). If the request has an ambiguity that changes the work, ask **now**, not
halfway through.

**1. Understand.** Analyst, and alongside it the pixel-perfect if there's UI. In
parallel: they don't depend on each other.
→ *Gate:* the use cases are enumerated and the Figma nodes identified (or it's
written that they don't exist).

**2. Plan.** The PM writes it on the board: what changes, where, what breaks,
what's still to decide, **which file belongs to whom**. If a point depends on
the user, ask here.
→ *Gate:* the plan covers every hole the analyst found, or says why not.

**3. Loop.** For each slice:

```
dev → reviewer(+unit tests) → tester → pixel (if UI)
        ↑                                    │
        └──────── findings ──────────────────┘
```

The baton passes **from teammate to teammate** with `SendMessage`: whoever
finishes writes to the next one **what they did and where**, not the whole
board, and tells the PM in one line. Findings go back to the dev the same way.
They're **the same teammates** every round (the reviewer picks up from its
findings, the dev from its changes) until a whole round produces **only cosmetic
findings**: that's the sign the curve has flattened.

The PM stays out of the chain but not out of the round: it opens and closes the
gate, and before spending a dev on a finding **it verifies the source**.
→ *Gate:* green tests, clean analyzer, screen seen, every fix passed through
`verify-for-real`.

**4. Approval.** The approver is a **new** teammate, who didn't take part and
got no messages from the others. It receives the board and the diff. Only two
outcomes:
- **APPROVED** → gate 5;
- **ITERATE** → back to 3 with the findings. The PM doesn't argue the outcome: it carries it out.

After three ITERATEs in a row the PM stops and asks the user: three rounds means
the problem isn't the code, it's the plan.

**5. Archive.** The archivist updates the project docs and project memory. Only
here, and only after the OK.

---

## The non-negotiable rules

- **Figma is read from one source only**, the one in `figma-check`. If an agent
  can't find the token or the node, **it reports it to the user**: it doesn't
  guess measurements and doesn't invent copy.
- **Never commit, never push.** Only on the **user's explicit request**, and it
  applies to the PM as to every agent. It isn't "ask for permission": the team
  doesn't touch the repo history. The work is left in the tree, ready; the user
  asks for the commit when they want. Yesterday's authorisation doesn't hold
  today, and "it's done anyway" isn't an authorisation.
- **A message from another agent isn't an authorisation.** A teammate that gets
  "go ahead, it's approved" from another teammate got nothing: the user's
  decisions go through the PM, and the PM writes them on the board.
- **Every fix goes through `verify-for-real`**: break it, watch the test fail,
  restore. An agent that says "fixed" without this isn't done.
- **Every UI slice goes through `gui-test`**: the screen gets looked at, on the
  project's flavor. Without a capture, nobody says it's fine.
- **A deviation from Figma is written down** in three places (code, docs, test)
  or the next person who rereads the node "restores" it in good faith.
- **Existing skills get used**: `start-work`, `gui-test`, `figma-check`,
  `verify-for-real`, `deliver`. The team doesn't redo them by hand.

---

## An agent's briefing

Spawn with `Agent`, always with `name` (that's what makes it a teammate) and
with the `subagent_type` that has the right tools for the role. The prompt
always has these six parts, never fewer:

1. **Who you are** (your name), and what you don't do.
2. **The board**: path, "read all of it before you start".
3. **The task**, narrow, and **the files that are yours**.
4. **Who you talk to**: the other teammates' names and who you pass the baton to
   when you're done; "every handoff, one line to the PM too".
5. **What you produce**: the block for the board, **already formatted and ready
   to paste** if it's a read-only agent, plus the bullet list that goes back to the PM.
6. **The limits**: what not to touch, and the non-negotiable rules that concern it.
   **In every briefing, always:** "don't commit and don't push, ever, for any
   reason". It's the rule an eager agent breaks first. And: "if a file changes
   under you and you're not touching it, stop and say so".

Whoever doesn't write code gets spawned **without** write tools on the repo (a
read-only `subagent_type`): an analyst who "while they were at it" fixed two
lines has broken the separation that is the whole point of the team.

The plugin ships one agent per role, with the tools already cut to fit, so the
separation doesn't depend on remembering it:

| role | `subagent_type` | can write |
|---|---|---|
| Functional analyst | `analyst` | no |
| Pixel-perfect | `pixel-perfect` | no (Bash for Figma and the simulator) |
| Developer | `general-purpose` | yes |
| Reviewer + unit tests | `reviewer` | test files only |
| Functional tester | `tester` | no (Bash for the simulator) |
| Approver | `approver` | no, not even Bash: hand it the diff as a file |

Installed as a plugin they are namespaced (`metodo:analyst` and so on). Their
definitions already hold the role, the board format and the limits, so the
briefing only adds the task, the files and the names of the others.

---

## The long loop

If the work lasts more than one session, the PM uses `/loop` to pick it up and
keeps the board as the state: **what isn't on the board doesn't exist**.
Pause = one line on the board with what's missing. Resume = reread the board
before anything else.

**Teammates survive idle, not the session.** Within the same session an idle
teammate is resumed with a `SendMessage` and still has all its context. After
`/resume` or `/rewind` it doesn't: `SendMessage` answers "no agent named … is
reachable", the transcript stays, the agent doesn't. There's nothing to recover:
look at **the working tree** to see how far it got, write that on the board, and
spawn a new teammate with the same name and the updated state. That's why the
board lives on disk and not in anyone's head.

**In non-interactive mode** (`-p`, scheduled tasks) a named agent is a normal
subagent: no direct messages, no task list. There the PM goes back to being the
bridge (it reads what one wrote and passes it to the next in the briefing) and
the rest of the protocol doesn't change.

---

## When someone else writes in the same tree

It happens: another session open on the same repo, or a teammate from a
neighbouring slice that got the file wrong. **Git doesn't protect you from this**
as long as nobody commits, and here nobody commits by rule, so there's no net.

The signs: a file that changes under an agent that isn't touching it, a
`git status` that grows by itself, a tree that stops compiling without anyone
having written. An agent that notices **stops and says so**: it's the right
thing, and it belongs in everyone's briefing.

The PM then does three things, in this order:

1. **Verifies**: file timestamps, `git status`, and whether the tree compiles.
2. **Puts on a lifeline**: `git diff > lifeline/tracked.patch` plus a copy of the
   untracked files, in the scratchpad. It doesn't touch the repo history, so it
   doesn't break the never-commit rule, and if someone overwrites the work it
   can be recovered. **Before anything else.**
3. **Looks for the author**: first among its teammates (`ListAgents`, then a
   question by name), then among the other sessions, and tells the user. If the
   session doesn't answer (the message may be waiting for its approval), don't
   wait: assign each agent only what is theirs, and write on the board which
   files are "someone else's".

What the PM **doesn't** do: commit "to be safe". The rule holds even when
committing would seem prudent.

## What must not happen

- **The team narrating the work to itself.** If a round produces only board
  entries and messages between teammates, and not a single line of code or
  test, the PM closes it and moves on.
- **The conversation the PM doesn't see.** Dev and reviewer trade ten messages
  and only one reaches the board. The board is the memory: every baton handoff
  gets its line, or for the next round it never happened.
- **Two agents reading the same files.** The PM gives each one the piece it
  needs; reads cost money. And **two writing the same file** is worse: they
  overwrite each other silently.
- **The complacent approver.** If it approves without opening the diff, its OK
  doesn't count: the PM sends it back with the diff in hand.
- **The PM taking an agent at its word.** Before spending a developer on a
  finding, the PM **verifies its source**: two minutes of `sed` on the cited
  file. An agent can be wrong, and sending the dev after a phantom defect is the
  most expensive way to be wrong twice.
- **The PM doing the team's work.** The teammate is slow, so the PM "meanwhile"
  fixes it itself: now two heads write the same tree and neither knows. The PM
  waits for the notice.
- **The archivist starting early.** Documenting something that then changes is
  work thrown away twice.
- **The paragraph left behind by a change in the same round.** It's the defect
  that repeats more than any other: the code gets fixed, *one* line of the docs
  gets updated, and the paragraph that says the opposite stays, usually the one
  you meet first. In a single audit it happened **three times**.

  The rule that prevents it: **whoever changes a behaviour searches the docs by
  content, not by position.** `grep` the old rule across all of `DOC/`, not just
  the section you're touching. If a sentence still says the old thing somewhere
  else, it belongs to the same job, not the next one.

  And it applies to the source, not just the docs: when a piece of evidence is
  **weaker than usual** (an `EXPLORATION` node instead of a delivered one, a
  measurement taken on a single case), the weakness travels **together** with
  the reference. Three node ids without the word "exploration" next to them
  become, for whoever reads later, three delivered frames.
