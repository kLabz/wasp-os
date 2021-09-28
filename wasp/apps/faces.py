# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson
"""Watch Face Chooser
~~~~~~~~~~~~~~~~~~~~~

A tool to select a suitable watch face.

.. figure:: res/FacesApp.png
    :width: 179

The app is intended to be enabled by default and has, therefore, been carefully
structured to minimize memory usage when the app is not active.
"""

import wasp

# # 2-bit RLE, 96x64, generated from res/clock_icon.png, 419 bytes
# icon = (
#     b'\x02'
#     b'`@'
#     b'\x1e@\x81d<d<d;f?X\xec2\xf0/'
#     b'\xf2-\xf4,\xc3.\xc3,\xc3.\xc3,\xc3.\xc3,'
#     b'\xc3.\xc3,\xc3.\xc3,\xc3.\xc3,\xc3.\xc3,'
#     b'\xc3.\xc3,\xc3.\xc3,\xc3.\xc3,\xc3.\xc3,'
#     b'\xc3.\xc3,\xc3.\xc3,\xc3\x02\x01\x02\x80\xeb\x84\x04'
#     b'\xc4\x0e\x82\x06\xc3\x04\xc3,\xc3\x02\x01\x01\x81\x03\x82\x03'
#     b'\xc1\x02\xc1\rA\x01\x81\x05\xc1\x07\xc3,\xc3\x02\x01\x06'
#     b'\x81\x02\xc1\x04\xc1\x0e\x81\x04\xc1\x08\xc3,\xc3\x02\x01\x06'
#     b'\x81\x02\xc1\x04\xc1\x05\x81\x08\x81\x04\xc1\x01\xc3\x04\xc3,'
#     b'\xc3\x02\x01\x05\x82\x02\xc1\x04\xc1\x05\x81\x08\x81\x04\xc2\x02'
#     b'\xc2\x03\xc3+\xc4\x02\x01\x04\x82\x03\xc1\x04\xc1\x0e\x81\x04'
#     b'\xc2\x03\xc1\x03\xc3*\xc5\x02\x01\x03\x82\x04\xc1\x04\xc1\x0e'
#     b'\x81\x04\xc1\x04\xc1\x03\xc3*\xc5\x02\x01\x02\x82\x05\xc1\x04'
#     b'\xc1\x0e\x81\x04\xc1\x04\xc1\x03\xc3*\xc5\x02\x01\x01\x82\x07'
#     b'\xc1\x02\xc2\x05\x81\x08\x81\x04\xc2\x02\xc2\x03\xc3*\xc5\x02'
#     b'\x01\x01\x86\x03\xc4\x06\x81\x06\x85\x03\xc4\x04\xc3*\xc5\x02'
#     b'\x01+\xc3*\xc5\x02\x01+\xc3*\xc5\x02\x01+\xc3+'
#     b'\xc4\x02\x01+\xc3,\xc3\x02\x01+\xc3,\xc3\x02\x01+'
#     b'\xc3,\xc3\x02\x01+\xc3,\xc3\x02\x01\x07\xc2\x05\xc2\x08'
#     b'\xc2\x01\xc2\x0e\xc3,\xc3\x02\x01\n\xc1\xc1\x02\xc1\x01\xc1'
#     b'\x02\xc2\x0b\xc1\xc1\xc1\x08\xc3,\xc3\x02\x01\x0e\xc1\xc1\xc1'
#     b'\x03\xc1\x03\xc1\x03\xc1\x01\xc1\x0c\xc3,\xc3.\xc3,\xc3'
#     b'.\xc3,\xc3.\xc3,\xc3.\xc3,\xc3.\xc3,\xc3'
#     b'.\xc3,\xc3.\xc3,\xc3.\xc3,\xc3.\xc3,\xc3'
#     b'.\xc3,\xc3.\xc3,\xc3.\xc3,\xc3.\xc3,\xf4'
#     b'-\xf2/\xf02\xec?Xf;d<d<d\x1e'
# )

class FacesApp():
    """Choose a default watch face."""
    NAME = 'Faces'
    # ICON = icon

    def foreground(self):
        """Activate the application."""
        choices = []
        choices.append(('clock', 'Clock'))
        choices.append(('chrono', 'Chrono'))
        choices.append(('klabz', 'KLabz'))
        # choices.append(('dual_clock', 'DualClock'))
        # choices.append(('fibonacci_clock', 'FibonacciClock'))
        # choices.append(('word_clock', 'WordClock'))

        self.choices = choices
        self.choice = 0
        self.si = wasp.widgets.ScrollIndicator()

        self._update()
        wasp.system.request_event(wasp.EventMask.SWIPE_UPDOWN)

    def background(self):
        self.choices = None
        del self.choices
        self.choice = None
        del self.choice
        self.si = None
        del self.si

        # When the watch face redraws then the change to the scrolling indicator
        # is a little subtle. Let's provide some haptic feedback too so the user
        # knows something has happened.
        wasp.watch.vibrator.pulse()

    def swipe(self, event):
        """Notify the application of a touchscreen swipe event."""
        choice = self.choice
        if event[0] == wasp.EventType.DOWN:
            choice = choice - 1 if choice > 0 else len(self.choices)-1
        if event[0] == wasp.EventType.UP:
            choice = choice + 1 if choice < len(self.choices)-1 else 0
        self.choice = choice

        mute = wasp.watch.display.mute
        mute(True)
        self._update()
        mute(False)

    def _update(self):
        """Draw the display from scratch."""
        wasp.watch.drawable.fill()
        (module, label) = self.choices[self.choice]
        wasp.system.register('apps.{}.{}App'.format(module, label), watch_face=True)
        wasp.system.quick_ring[0].preview()
        self.si.draw()
