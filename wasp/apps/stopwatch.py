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
    b'?\xff\xdd@\xc1J6J6J9D<D<D'
    b'<D9J\x08\xc2)P\x05\xc3&T\x04\xc3#G'
    b'\nG\x03\xc3!E\x10E\x03\xc3\x1fD\t\x80\xc6\x85'
    b'\x06D\x03\xc3\x1dC\x0b\x88\x05C\x03\xc3\x1bC\x0c\x8a'
    b'\x04C\x03\xc3\x19C\r\x8b\x04C\x03\xc2\x18C\x03\xc2'
    b'\t\x8c\x04C\x1bC\x04\xc3\x08\x8d\x04C\x1aC\x05\xc3'
    b'\x07\x8e\x03C\x19C\x07\xc3\x06\x8f\x03C\x18C\x08\xc2'
    b'\x06\x90\x02C\x17C\x11\x90\x03C\x16C\x11\x91\x02C'
    b'\x16C\x11\x91\x02C\x15C\x12\x91\x03C\x14C\x12\x92'
    b'\x02C\x14C\x12\x92\x02C\x14C\x02\xc6\n\x92\x02C'
    b'\x14C\x02\xc6\n\x92\x02C\x14C\x13\x91\x02C\x14C'
    b'\x14\x90\x02C\x14C\x15\x8f\x02C\x14C\x16\x8d\x03C'
    b'\x15C\x16\x8c\x02C\x16C\x17\x8b\x02C\x16C\t\xc2'
    b'\r\x89\x03C\x17C\x07\xc3\x0e\x88\x02C\x18C\x06\xc3'
    b'\x10\x86\x03C\x19C\x04\xc3\x12\x84\x03C\x1aC\x04\xc2'
    b'\t\xc2\t\x82\x04C\x1bC\x0e\xc2\x0eC\x1dC\r\xc2'
    b'\rC\x1fC\x0c\xc2\x0cC!C\x0b\xc2\x0bC#D'
    b"\t\xc2\tD%E\x10E'G\nG*T.P"
    b'3J?\xff]'
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
