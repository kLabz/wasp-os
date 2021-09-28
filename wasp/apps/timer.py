# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Wolfgang Ginolas
"""Timer Application
~~~~~~~~~~~~~~~~~~~~

An application to set a vibration in a specified amount of time. Like a kitchen timer.

    .. figure:: res/TimerApp.png
        :width: 179

        Screenshot of the Timer Application

"""

import wasp
import fonts
import time
import widgets
import math
from micropython import const

# 2-bit RLE, 64x64, generated from ./res/timer_icon.png, 247 bytes
icon = (
    b'\x02'
    b'@@'
    b"?\xff\xff\x15@\xc1\\%Z'B\x14B(A\x16"
    b"A'A\x18A&A\x18A%A\x1aA$A\x1a"
    b'A$A\x1aA$A\x1aA$A\x1aA$A\x1a'
    b'A$A\x02\x80\xc6\x96\x02A%A\x01\x96\x01A&'
    b"A\x02\x94\x02A'A\x02\x92\x02A)A\x03\x8e\x03"
    b'A+B\x03\x8a\x03B.B\x02\x88\x02B2A\x02'
    b'\x86\x02A5A\x02\x84\x02A7A\x02\x82\x02A9'
    b'A\x01\x82\x01A:A\x04A;A\x02A;A\x04'
    b'A:A\x04A9A\x02\xc1\x03A7A\x08A5'
    b'A\x05\xc1\x04A2B\x0cB.B\x07\xc1\x08B+'
    b"A\x14A)A\x16A'A\x0c\xc1\x0bA&A\x18"
    b'A%A\x1aA$A\x1aA$A\r\x81\x0cA$'
    b'A\x0c\x83\x0bA$A\x0b\x85\nA$A\t\x88\t'
    b'A$A\x06\x8c\x08A%A\x02\x94\x02A&A\x02'
    b"\x94\x02A'A\x02\x92\x02A(B\x14B'Z%"
    b'\\?\xffT'
)

_STOPPED = const(0)
_RUNNING = const(1)
_RINGING = const(2)

_BUTTON_Y = const(200)

class TimerApp():
    """Allows the user to set a vibration alarm.
    """
    NAME = 'Timer'
    ICON = icon

    def __init__(self):
        """Initialize the application."""
        self.minutes = widgets.Spinner(50, 60, 0, 99, 2)
        self.seconds = widgets.Spinner(130, 60, 0, 59, 2)
        self.current_alarm = None

        self.minutes.value = 10
        self.state = _STOPPED

    def foreground(self):
        """Activate the application."""
        self._draw()
        wasp.system.request_event(wasp.EventMask.TOUCH)
        wasp.system.request_tick(1000)

    def background(self):
        """De-activate the application."""
        if self.state == _RINGING:
            self.state = _STOPPED

    def tick(self, ticks):
        """Notify the application that its periodic tick is due."""
        if self.state == _RINGING:
            wasp.watch.vibrator.pulse(duty=50, ms=500)
            wasp.system.keep_awake()
        self._update()

    def touch(self, event):
        """Notify the application of a touchscreen touch event."""
        if self.state == _RINGING:
            mute = wasp.watch.display.mute
            mute(True)
            self._stop()
            mute(False)
        elif self.state == _RUNNING:
            self._stop()
        else:  # _STOPPED
            if self.minutes.touch(event) or self.seconds.touch(event):
                pass
            else:
                y = event[2]
                if y >= _BUTTON_Y:
                    self._start()


    def _start(self):
        self.state = _RUNNING
        now = wasp.watch.rtc.time()
        self.current_alarm = now + self.minutes.value * 60 + self.seconds.value
        wasp.system.set_alarm(self.current_alarm, self._alert)
        self._draw()

    def _stop(self):
        self.state = _STOPPED
        wasp.system.cancel_alarm(self.current_alarm, self._alert)
        self._draw()

    def _draw(self):
        """Draw the display from scratch."""
        draw = wasp.watch.drawable
        draw.fill()
        sbar = wasp.system.bar
        sbar.clock = True
        sbar.draw()

        if self.state == _RINGING:
            draw.set_font(fonts.sans24)
            draw.string(self.NAME, 0, 150, width=240)
            draw.blit(icon, 73, 50)
        elif self.state == _RUNNING:
            self._draw_stop(104, _BUTTON_Y)
            draw.string(':', 110, 120-14, width=20)
            self._update()
        else:  # _STOPPED
            draw.set_font(fonts.sans28)
            draw.string(':', 110, 120-14, width=20)

            self.minutes.draw()
            self.seconds.draw()

            self._draw_play(114, _BUTTON_Y)

    def _update(self):
        wasp.system.bar.update()
        draw = wasp.watch.drawable
        if self.state == _RUNNING:
            now = wasp.watch.rtc.time()
            s = self.current_alarm - now
            if s<0:
                s = 0
            m = str(math.floor(s // 60))
            s = str(math.floor(s) % 60)
            if len(m) < 2:
                m = '0' + m
            if len(s) < 2:
                s = '0' + s
            draw.set_font(fonts.sans28)
            draw.string(m, 50, 120-14, width=60)
            draw.string(s, 130, 120-14, width=60)

    def _draw_play(self, x, y):
        draw = wasp.watch.drawable
        for i in range(0,20):
            draw.fill(0xffff, x+i, y+i, 1, 40 - 2*i)

    def _draw_stop(self, x, y):
        wasp.watch.drawable.fill(0xffff, x, y, 40, 40)

    def _alert(self):
        self.state = _RINGING
        wasp.system.wake()
        wasp.system.switch(self)
