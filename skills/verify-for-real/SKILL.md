---
name: verify-for-real
description: The rituals that find real defects. Break the fix to watch the test fail, inject the fault instead of deducing it, count instead of estimating. Use before saying anything is fixed or verified.
---

# Verifying for real

It doesn't automate anything. It's the difference between "I fixed it" and
"I verified it", and in practice it disproves more deductions than it confirms.

## 1. Break the fix and watch the test fail

A test that also passes on broken code is worth nothing. For every fix: `cp`
the file, put the old behaviour back, run the tests, **watch them fail**,
restore. Thirty seconds.

Tests really do pass for the wrong reason: the fixture lacked the field the
filter needs, so it counted zero items and the assertion was true by accident.

## 2. Inject the fault, don't deduce it

When the conclusion is "if the network drops, X happens", don't stop at the
code: replace the response with an error, rebuild, and look.

It costs one build and it changes the conclusion. A real case: the code
suggested "the old profile stays"; injecting the error showed that three
downstream loads **never started at all**, and that pull-to-refresh didn't
recover. In other words, there was no way out of that state without closing the app.

**A counter that fails only the first attempt** (`static int _n; if (++_n == 1) return Error(...)`)
also shows the recovery, and it's what you need for screens you have to demo.

Once the probe is gone, check nothing was left behind: `grep` for the marker.

## 3. Count, don't estimate

"It looks like it fires two or three times" is not a measurement. Count them.

Watch out for double counting: network loggers print **request and response**,
so two lines per call. A real case: it looked like 2-3 call chains, counted per
endpoint it was **one**, and the fix about to be written wasn't needed.

## 4. Cross-check with an external source

A screen consistent with itself proves nothing. Compare it with something
outside the app: the simulator plist, the network log, the Figma node, the
backend response. The mismatches there are the real defects.

## 5. Enumerate the states, don't fix the symptom

If you get the same boundary wrong twice, you're fixing the case you just saw.
Open the states file and cover all of them: the right question isn't "is this
case covered?" but "what are all the cases?".
