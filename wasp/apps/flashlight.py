# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Flashlight
~~~~~~~~~~~~~

Shows a pure white screen with the backlight set to maximum.

.. figure:: res/TorchApp.png
    :width: 179
"""

import wasp

# 2-bit RLE, generated from res/torch_icon.png, 245 bytes
icon = (
    b'\x02'
    b'`@'
    b'?\xff\xff\xff\xff\xff\xff\xff&\xc6\x0c@\xd4B?\n'
    b'\xca\tD?\x08\xc4\x06\xc2\x07F?\x07\xc3\x07\xc2\x06'
    b'H?\x06\xc2\n\xc1\x04G\xc2A8\xc5\x08\xc2\t\xc2'
    b'\x02F\xc3C7\xc7\x06\xc2\x0b\xc1F\xc2F\x1e\xe8\n'
    b'\xc2C\xc3H\x1d\xe8\x0c\xc1N\x1d\xc2%\xc1\x0b\xc2N'
    b'\x1d\xc2%\xc1\x0c\xc1N\x1d\xc2\x04\x9d\x04\xc1\x0b\xc2N'
    b'\x1d\xc2\x06\x81\x03\x81\x03\x81\x03\x81\x03\x81\x03\x81\x03\x81'
    b'\x06\xc1\x0c\xc1N\x1d\xc2\x04\x9d\x04\xc1\x0b\xc2C\xcaA'
    b'\x1d\xc2\x06\x81\x03\x81\x03\x81\x03\x81\x03\x81\x03\x81\x03\x81'
    b'\x06\xc1\x0c\xc1N\x1d\xc2\x04\x9d\x04\xc1\x0b\xc2N\x1d\xc2'
    b'%\xc1\x0c\xc1N\x1d\xc2%\xc1\x0b\xc2N\x1d\xe8\x0c\xc1'
    b'N\x1e\xe8\n\xc2C\xc3H?\x05\xc2\x0b\xc1F\xc2F'
    b'?\x06\xc2\t\xc2\x02F\xc3C?\x06\xc2\n\xc1\x04G'
    b'\xc2A?\x07\xc3\x07\xc2\x06H?\x08\xc4\x06\xc2\x07F'
    b'?\n\xca\tD?\r\xc6\x0cB?\xff\xff\xff\xff\xff'
    b'\xff\x95'
)

class TorchApp(object):
    """Trivial flashlight application."""
    NAME = 'Torch'
    ICON = icon

    def __init__(self):
        self.__activated = False

    def foreground(self):
        """Activate the application."""
        self._brightness = wasp.system.brightness
        self.draw()
        wasp.system.request_tick(1000)
        wasp.system.request_event(wasp.EventMask.TOUCH | wasp.EventMask.BUTTON)

    def background(self):
        """De-activate the application (without losing state)."""
        self.__activated = False
        wasp.system.brightness = self._brightness

    def tick(self, ticks):
        wasp.system.keep_awake()

    def touch(self, event):
        self.__activated = not self.__activated
        self.draw()

    def press(self, button, state):
        if not state:
            return

        self.__activated = not self.__activated
        self.draw()

    def draw(self):
        """Redraw the display from scratch."""
        if self.__activated:
            wasp.watch.drawable.fill(0xffff)
            self.draw_torch(0, 0)
            wasp.system.brightness = 3
        else:
            wasp.watch.drawable.fill()
            self.draw_torch(wasp.system.theme('mid'), 0xffff)
            wasp.system.brightness = self._brightness

    def draw_torch(self, torch, light):
        draw = wasp.watch.drawable
        x = 108

        draw.fill(torch, x, 107, 24, 9)
        for i in range(1, 8):
            draw.line(x+i, 115+i, x+23-i, 115+i, color=torch)
        draw.fill(torch, x+8, 123, 8, 15)

        draw.line(x-3, 94, x+5, 102, 2, light)
        draw.line(x+17, 102, x+25, 94, 2, light)
        draw.line(x+11, 89, x+11, 100, 2, light)
