# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Stopwatch
~~~~~~~~~~~~

Simple stop/start watch with support for split times.

.. figure:: res/StopclockApp.png
    :width: 179
"""
import wasp
import fonts

# 2-bit RLE, 64x64, generated from ./res/stopwatch_icon.png, 296 bytes
icon = (
    b'\x02'
    b'@@'
    b'?\xff\xdd\x8a6\x8a6\x8a9\x84<\x84<\x84<\x84'
    b'9\x8a\x08\xc2)\x90\x05\xc3&\x94\x04\xc3#\x87\n\x87'
    b'\x03\xc3!\x85\x10\x85\x03\xc3\x1f\x84\t@\xacE\x06\x84'
    b'\x03\xc3\x1d\x83\x0bH\x05\x83\x03\xc3\x1b\x83\x0cJ\x04\x83'
    b'\x03\xc3\x19\x83\rK\x04\x83\x03\xc2\x18\x83\x03\xc2\tL'
    b'\x04\x83\x1b\x83\x04\xc3\x08M\x04\x83\x1a\x83\x05\xc3\x07N'
    b'\x03\x83\x19\x83\x07\xc3\x06O\x03\x83\x18\x83\x08\xc2\x06P'
    b'\x02\x83\x17\x83\x11P\x03\x83\x16\x83\x11Q\x02\x83\x16\x83'
    b'\x11Q\x02\x83\x15\x83\x12Q\x03\x83\x14\x83\x12R\x02\x83'
    b'\x14\x83\x12R\x02\x83\x14\x83\x02\xc6\nR\x02\x83\x14\x83'
    b'\x02\xc6\nR\x02\x83\x14\x83\x13Q\x02\x83\x14\x83\x14P'
    b'\x02\x83\x14\x83\x15O\x02\x83\x14\x83\x16M\x03\x83\x15\x83'
    b'\x16L\x02\x83\x16\x83\x17K\x02\x83\x16\x83\t\xc2\rI'
    b'\x03\x83\x17\x83\x07\xc3\x0eH\x02\x83\x18\x83\x06\xc3\x10F'
    b'\x03\x83\x19\x83\x04\xc3\x12D\x03\x83\x1a\x83\x04\xc2\t\xc2'
    b'\tB\x04\x83\x1b\x83\x0e\xc2\x0e\x83\x1d\x83\r\xc2\r\x83'
    b'\x1f\x83\x0c\xc2\x0c\x83!\x83\x0b\xc2\x0b\x83#\x84\t\xc2'
    b"\t\x84%\x85\x10\x85'\x87\n\x87*\x94.\x903\x8a"
    b'?\xff]'
)

class StopwatchApp():
    """Stopwatch application."""
    # Stopwatch requires too many pixels to fit into the launcher

    NAME = 'Stopclock'
    ICON = icon

    def __init__(self):
        self._timer = wasp.widgets.Stopwatch(120-36)
        self._reset()

    def foreground(self):
        """Activate the application."""
        wasp.system.bar.clock = True
        self._draw()
        wasp.system.request_tick(97)
        wasp.system.request_event(wasp.EventMask.TOUCH |
                                  wasp.EventMask.BUTTON |
                                  wasp.EventMask.NEXT)

    def sleep(self):
        return True

    def wake(self):
        self._update()

    def swipe(self, event):
        """Handle NEXT events by augmenting the default processing by resetting
        the count if we are not currently timing something.

        No other swipe event is possible for this application.
        """
        if not self._started_at:
            self._reset()
        return True     # Request system default handling

    def press(self, button, state):
        if not state:
            return

        if self._timer.started:
            self._timer.stop()
        else:
            self._timer.start()

    def touch(self, event):
        if self._timer.started:
            self._splits.insert(0, self._timer.count)
            del self._splits[4:]
            self._nsplits += 1
        else:
            self._reset()

        self._update()
        self._draw_splits()

    def tick(self, ticks):
        self._update()

    def _reset(self):
        self._timer.reset()
        self._splits = []
        self._nsplits = 0

    def _draw_splits(self):
        draw = wasp.watch.drawable
        splits = self._splits
        if 0 == len(splits):
            draw.fill(0, 0, 120, 240, 120)
            return
        y = 240 - 6 - (len(splits) * 24)

        draw.set_font(fonts.sans24)
        draw.set_color(wasp.system.theme('mid'))

        n = self._nsplits
        for i, s in enumerate(splits):
            centisecs = s
            secs = centisecs // 100
            centisecs %= 100
            minutes = secs // 60
            secs %= 60

            t = '# {}   {:02}:{:02}.{:02}'.format(n, minutes, secs, centisecs)
            n -= 1

            w = fonts.width(fonts.sans24, t)
            draw.string(t, 0, y + (i*24), 240)

    def _draw(self):
        """Draw the display from scratch."""
        draw = wasp.watch.drawable
        draw.fill()

        wasp.system.bar.draw()
        self._timer.draw()
        self._draw_splits()

    def _update(self):
        wasp.system.bar.update()
        self._timer.update()
