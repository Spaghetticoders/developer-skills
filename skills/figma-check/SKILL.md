---
name: figma-check
description: Downloads node and render from Figma and compares them with the app's real screen, measurements included. Recognises an expired token in a single call, and when the design looks wrong it stops and asks instead of deciding on its own.
---

# Comparing with Figma

## Access

The Figma personal access token lives in an environment variable (`FIGMA_TOKEN`),
never in the repo. The file key lives in the project docs. **A project can have
more than one file**: asking the wrong file for a node returns `null` without
saying why, and it's the first place time gets lost.

```sh
curl -sH "X-Figma-Token: $FIGMA_TOKEN" "https://api.figma.com/v1/files/$KEY/nodes?ids=123:456"
curl -sH "X-Figma-Token: $FIGMA_TOKEN" "https://api.figma.com/v1/images/$KEY?ids=123:456&format=png&scale=2"
```

Ids use `-` in URLs and `:` in the API. The render comes back as a short-lived
URL: download it right away.

**The token expires.** The signature is `{"status":403,"err":"Token expired"}` on
**any** call, `/v1/me` included: try that one first and you'll know in one shot
whether it's the token or the permissions. When it has expired, don't look for
workarounds: ask the user for a new token.

## Finding the node

If you only have the screen's name, walk down level by level instead of guessing:
`?depth=1` gives the pages, `?depth=2` the sections, then the frames inside the section.

## Comparing

Put the render next to the simulator capture (`gui-test`) and look at **text,
sizes and order**, not the general impression. For text, read `characters` from
the node: that's the source, not what you read in the render.

**Watch out for truncated text.** If a title ends with an ellipsis, check
`textTruncation`, `maxLines` and the box width: if they aren't there, **the
designer typed the dots** and it isn't an elision. It happens.

## When the design looks wrong

**Stop and ask before implementing.** Don't invent copy or measurements, and
don't silently ship the version that looks right to you.

Don't block everything else: implement what doesn't depend on that answer,
hold back the uncertain piece, and ask at the right moment.

If the user decides to deviate from the node, **write it down where someone will
find it**: a code comment with the node id and the measurement, the docs, and a
test that fails if it goes back. Otherwise the next person who rereads Figma
"restores" it in good faith.
