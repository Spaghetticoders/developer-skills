---
name: gui-test
description: Drives the iOS simulator with idb to really try a screen. Finds elements by label in the accessibility tree, taps, scrolls, types and captures, and reads what it saw instead of assuming it worked.
---

# Testing on the simulator

A screen isn't verified until someone has looked at it. This applies to every
UI slice: without a capture, nobody says it's fine.

## idb is the main road

`idb` talks to the simulator through `idb_companion`: **it doesn't move the Mac's
cursor, it doesn't need the window in front**, and it works with the simulator
behind other windows.

```sh
brew tap facebook/fb && brew install idb-companion
pip install fb-idb
```

Next to this skill there's `sim_drive.py`, which wraps idb. Copy it into the
project's `tool/` folder. It picks the simulator from `SIM_UDID`, or failing
that the first booted one.

## The real difference: you search by label

`idb ui describe-all` returns **the accessibility tree**: label, role, frame in
logical points, enabled or not. So a button is found by name, instead of
cropping a screenshot and redoing the maths on the scale.

```python
import sim_drive as s
s.tap_label('Settings')               # scrolls down, then from the top, then taps
s.labels()                            # everything on screen
s.describe_point(410, 94)             # what's at a point, for controls without a label
s.shot('/tmp/settings.png')           # the capture, to look at
```

It also changes **what you can claim**: `Button "Help" at x=382` and no
`"Back"` is a verification, not a glance at a screenshot. Use the tree for
assertions and the capture for appearance.

## The rules that cost time if you ignore them

**The tree only contains what has been laid out.** In a long list the row you
need is there but with a null frame until you bring it on screen: scroll until
the frame is real. `tap_label` does it by itself.

**A tree read while the list is moving makes you tap the wrong row.** After a
fling the list keeps decelerating for a while, and a fixed pause isn't enough:
`tree()` rereads until two reads match, and only then returns. If a tap didn't
do what it should, **this is still suspect number one**. The check is to look
at where you ended up, not to trust the return value of `tap_label`, which only
says it tapped something.

**Swipe duration is the gesture, not the speed.** ~0.1 s is a fling and sends
the list to the bottom; 0.5 s is a drag of about four rows.

**Webviews are opaque.** A login in a webview only exposes the native button
that closes it: inside, the tree sees nothing. There you go back to coordinates
and captures.

## Typing text

**`idb ui text` is only safe for letters and digits.** It sends US key codes,
and a simulator with a different layout translates them into something else:
with the Italian layout `@` arrives as `”`.

`s.type_text('...')` splits the text: the safe runs go through `idb ui text`,
every other character is tapped on the on-screen keyboard, which has the real
layout. Then it **reads the field back and raises an error if the value doesn't
match**. The labels of the keys that switch keyboards depend on the simulator
language: set them with `SIM_KEY_SYMBOLS` and `SIM_KEY_LETTERS`.

Tap the **visible** centre of the field first, not the centre of its
accessibility frame: that frame includes the caption too, and its centre can
land on the border and leave focus on the previous field.

## Before the build

- **Sweep the `._*` files** if the repo lives on an ExFAT or network volume.
- **Check whether the project has mandatory local changes** to run on the
  simulator: they're in the project docs, usually a "DO NOT PUSH" stash.
- Flavor and target are in `.vscode/launch.json` or in the project docs.
- **Profile and release don't run on the iOS simulator**: to measure jank or
  timings in AOT you need a real device.

If you need the `flutter run` logs, don't use `simctl terminate`/`launch` to
restart: they detach the session. Restart with `flutter run`.

## Leave things as you found them

If you changed some real state to test (a consent, an address, a preference),
**put it back as it was** and check it, even on a test account. And say so in
the report.

**Don't uninstall the app** to be sure of the build: it takes session and data
with it. `flutter run` reinstalls on top.

## What else idb can do

`set-location` (fake GPS), `send-notification` (fake push), `record` and `video`
(record the session), `focus` (bring the simulator to the front when needed),
`log`, `add-media`.
