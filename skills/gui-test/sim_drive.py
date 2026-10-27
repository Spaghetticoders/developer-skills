"""Drive the iOS simulator through idb.

    import sim_drive as s
    s.labels()                 # everything on screen
    s.tap_label('Settings')    # scrolls to find it, then taps
    s.shot('settings.png')

idb doesn't move the Mac's cursor and doesn't need the window in front, so the
simulator can stay behind other windows. Requires `idb_companion`.

The simulator is picked with SIM_UDID; without it, the first booted one is used.
"""
import json
import os
import subprocess
import time


def _booted_udid():
    out = subprocess.run(
        ['xcrun', 'simctl', 'list', 'devices', 'booted', '-j'],
        capture_output=True, text=True,
    ).stdout
    for devices in json.loads(out or '{}').get('devices', {}).values():
        for device in devices:
            if device.get('state') == 'Booted':
                return device['udid']
    raise RuntimeError('no booted simulator: boot one or set SIM_UDID')


UDID = os.environ.get('SIM_UDID') or _booted_udid()


def _idb(*args, timeout=60):
    return subprocess.run(
        ['idb', *args, '--udid', UDID],
        capture_output=True, text=True, timeout=timeout,
    )


def _read_tree():
    out = _idb('ui', 'describe-all').stdout
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return []


def tree(settle=0.35, tries=12):
    """The accessibility tree, read once the screen has settled.

    A decelerating list returns different frames on every read, and tapping on
    those numbers lands on the wrong row. So it rereads until two reads match.
    """
    previous = None
    for _ in range(tries):
        current = _read_tree()
        signature = [(e.get('AXLabel'), str(e.get('frame'))) for e in current]
        if previous is not None and signature == previous:
            return current
        previous = signature
        time.sleep(settle)
    return _read_tree()


def labels(limit=None):
    """The labels on screen, in the order the tree reports them."""
    found = [e.get('AXLabel') for e in tree() if e.get('AXLabel')]
    return found[:limit] if limit else found


def find(label, exact=False):
    """The first element whose label contains (or equals) `label`."""
    for element in tree():
        current = element.get('AXLabel') or ''
        if (current == label) if exact else (label in current):
            return element
    return None


def center(element):
    frame = element['frame']
    return int(frame['x'] + frame['width'] / 2), int(frame['y'] + frame['height'] / 2)


def tap(x, y):
    _idb('ui', 'tap', str(x), str(y))
    time.sleep(0.6)


def swipe(x1, y1, x2, y2, duration=0.4):
    """The duration is the gesture: ~0.1 s is a fling, ~0.5 s a drag."""
    _idb('ui', 'swipe', str(x1), str(y1), str(x2), str(y2), '--duration', str(duration))
    time.sleep(0.4)


def scroll_down(times=1, x=40):
    for _ in range(times):
        swipe(x, 760, x, 300, 0.45)


def scroll_up(times=1, x=40):
    for _ in range(times):
        swipe(x, 300, x, 760, 0.45)


def tap_label(label, exact=False, scrolls=8):
    """Scroll to find the label, then tap. Returns True if it tapped.

    Careful: True only says it tapped something. Where you ended up is checked
    by rereading the tree, not by trusting this value.
    """
    element = find(label, exact)
    if element:
        tap(*center(element))
        return True
    for _ in range(scrolls):
        scroll_down()
        element = find(label, exact)
        if element:
            tap(*center(element))
            return True
    scroll_up(scrolls)
    for _ in range(scrolls):
        element = find(label, exact)
        if element:
            tap(*center(element))
            return True
        scroll_up()
    return False


def describe_point(x, y):
    """What is at a point: for controls that have no label."""
    out = _idb('ui', 'describe-point', str(x), str(y)).stdout
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return None


def shot(path):
    subprocess.run(['xcrun', 'simctl', 'io', UDID, 'screenshot', path],
                   capture_output=True, text=True)
    return path


# `idb ui text` sends US-layout HID codes and the simulator maps them through
# the host keyboard layout, so only these characters are safe everywhere.
# Anything else goes through the on-screen keyboard, which has the real layout.
_SAFE_FOR_IDB_TEXT = set(
    'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.'
)

# Accessibility labels of the keys that switch the on-screen keyboard. They
# follow the simulator language: the defaults are for an Italian simulator.
_KEY_SYMBOLS = os.environ.get('SIM_KEY_SYMBOLS', 'cifre')
_KEY_LETTERS = os.environ.get('SIM_KEY_LETTERS', 'lettere')


def field_values():
    """`[(label, value)]` for every text field on screen.

    The label of an unfocused Flutter field often carries both its caption and
    its placeholder, separated by a newline.
    """
    return [((e.get('AXLabel') or '').strip(), e.get('AXValue'))
            for e in tree() if e.get('type') == 'TextField']


def _tap_key(label):
    """Tap an on-screen keyboard key by its accessibility label.

    Returns False when the key is not on the keyboard currently shown, so the
    caller can switch layout rather than tap a coordinate that moved.
    """
    for element in _read_tree():
        if element.get('type') == 'Button' and (element.get('AXLabel') or '').strip() == label:
            frame = element.get('frame') or {}
            if frame.get('width'):
                _idb('ui', 'tap',
                     str(int(frame['x'] + frame['width'] / 2)),
                     str(int(frame['y'] + frame['height'] / 2)))
                time.sleep(0.5)
                return True
    return False


def type_text(text, verify=True):
    """Type `text` into the focused field, and check that it arrived.

    Clipboard paste is not reliable on recent iOS simulators, and a helper that
    returns without reading the field back reports success on fields that stayed
    empty. So runs of safe characters go through `idb ui text`, every other
    character is tapped on the symbols keyboard, and the value is read back.

    Pass `verify=False` only for a masked field, such as a password, where there
    is nothing to compare against.

    Tap the **visible** centre of the field first, not the centre of its
    accessibility frame: that frame covers the caption as well, so its midpoint
    can land on the border and leave focus on the previous field.
    """
    on_symbols = False
    for chunk, special in _split_runs(text):
        if not special:
            if on_symbols:
                _tap_key(_KEY_LETTERS)
                on_symbols = False
            _idb('ui', 'text', chunk)
            time.sleep(0.4)
            continue
        if not on_symbols:
            if not _tap_key(_KEY_SYMBOLS):
                raise RuntimeError(
                    f"key {_KEY_SYMBOLS!r} not found: is the keyboard on screen? "
                    "If the simulator uses another language, set SIM_KEY_SYMBOLS"
                )
            on_symbols = True
        if not _tap_key(chunk):
            raise RuntimeError(
                f"character {chunk!r} is not on the symbols keyboard"
            )
    if on_symbols:
        _tap_key(_KEY_LETTERS)

    if not verify:
        return None
    seen = field_values()
    if not any(value == text for _, value in seen):
        raise AssertionError(
            f"typed {text!r} but the fields on screen hold {seen!r}"
        )
    return text


def _split_runs(text):
    """`text` as `(chunk, needs_keyboard)` pairs, safe runs kept together."""
    runs = []
    for character in text:
        special = character not in _SAFE_FOR_IDB_TEXT
        if runs and runs[-1][1] == special and not special:
            runs[-1] = (runs[-1][0] + character, special)
        else:
            runs.append((character, special))
    return runs
