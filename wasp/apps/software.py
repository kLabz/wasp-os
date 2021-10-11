# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson
"""Software
~~~~~~~~~~~

A tool to enable/disable applications.

.. figure:: res/SoftwareApp.png
    :width: 179

Most applications are disabled by default at boot in order to conserve
RAM (which is in short supply and very useful to anyone wanting to
write an application). This tools allows us to boot and conserve RAM
whilst still allowing users to activate so many awesome applications!
"""

import wasp
import os

# 2-bit RLE, 64x64, generated from ./res/software_icon.png, 298 bytes
icon = (
    b'\x02'
    b'@@'
    b'?\xff\x8b\x8a\x08\x8a"\x8e\x04\x8e\n\xc2\x14\x8e\x04\x8e'
    b'\t\xc4\x12\x90\x02\x90\x08\xc4\x12\x90\x02\x90\x08\xc4\x12\x90'
    b'\x02\x90\x08\xc4\x12\x90\x02\x90\x04\xcc\x0e\x90\x02\x90\x03\xce'
    b'\r\x90\x02\x90\x03\xce\r\x90\x02\x90\x04\xcc\x0e\x90\x02\x90'
    b'\x08\xc4\x12\x90\x02\x90\x08\xc4\x12\x90\x02\x90\x08\xc4\x13\x8e'
    b'\x04\x8e\t\xc4\x13\x8e\x04\x8e\n\xc2\x16\x8a\x08\x8a?e'
    b'@\xacJ\x08\x8a\x08\x8a\x10N\x04\x8e\x04\x8e\x0eN\x04'
    b'\x8e\x04\x8e\rP\x02\x90\x02\x90\x0cP\x02\x90\x02\x90\x0c'
    b'P\x02\x90\x02\x90\x0cP\x02\x90\x02\x90\x0cP\x02\x90\x02'
    b'\x90\x0cP\x02\x90\x02\x90\x0cP\x02\x90\x02\x90\x0cP\x02'
    b'\x90\x02\x90\x0cP\x02\x90\x02\x90\x0cP\x02\x90\x02\x90\r'
    b'N\x04\x8e\x04\x8e\x0eN\x04\x8e\x04\x8e\x10J\x08\x8a\x08'
    b'\x8a?SJ\x08J\x08\x8a\x10N\x04N\x04\x8e\x0eN'
    b'\x04N\x04\x8e\rP\x02P\x02\x90\x0cP\x02P\x02\x90'
    b'\x0cP\x02P\x02\x90\x0cP\x02P\x02\x90\x0cP\x02P'
    b'\x02\x90\x0cP\x02P\x02\x90\x0cP\x02P\x02\x90\x0cP'
    b'\x02P\x02\x90\x0cP\x02P\x02\x90\x0cP\x02P\x02\x90'
    b'\rN\x04N\x04\x8e\x0eN\x04N\x04\x8e\x10J\x08J'
    b'\x08\x8a?\xff\x0b'
)

class SoftwareApp():
    """Enable and disable applications."""
    NAME = 'Apps'
    ICON = icon

    def foreground(self):
        """Activate the application."""

        def factory(label):
            nonlocal y

            cb = wasp.widgets.Checkbox(0, y, label)
            y += 40
            if y > 160:
                y = 0
            return cb

        y = 0
        db = []
        # db.append(('alarm', factory('Alarm')))
        db.append(('calc', factory('Calculator')))
        db.append(('faces', factory('Faces')))
        # db.append(('gameoflife', factory('Game Of Life')))
        db.append(('musicplayer', factory('Music Player')))
        # db.append(('play2048', factory('Play 2048')))
        # db.append(('snake', factory('Snake Game')))
        # db.append(('sports', factory('Sports')))
        db.append(('stopwatch', factory('Stopwatch')))
        db.append(('heart', factory('Heart')))
        db.append(('steps', factory('Step Counter')))
        # db.append(('flashlight', factory('Torch')))
        db.append(('testapp', factory('Test')))
        db.append(('timer', factory('Timer')))
        db.append(('weather', factory('Weather')))

        # Handle user-loaded applications
        try:
            for app in os.listdir('apps'):
                name = None
                if app.endswith('.py'):
                    name = app[:-3]
                if app.endswith('.mpy'):
                    name = app[:-4]
                if name:
                    db.append((name, factory(name)))
        except OSError:
            # apps does not exist...
            pass

        # Get the initial state for the checkboxes
        for _, checkbox in db:
            label = checkbox.label.replace(' ', '')
            for app in wasp.system.launcher_ring:
                if type(app).__name__.startswith(label):
                    checkbox.state = True
                    break

        self.si = wasp.widgets.ScrollIndicator()
        self.page = 0
        self.db = db

        self._draw()
        wasp.system.request_event(wasp.EventMask.TOUCH |
                                  wasp.EventMask.SWIPE_UPDOWN)

    def background(self):
        self.si = None
        del self.si
        self.page = None
        del self.page
        self.db = None
        del self.db

    def get_page(self):
        i = self.page * 5
        return self.db[i:i+5]

    def swipe(self, event):
        """Notify the application of a touchscreen swipe event."""
        page = self.page
        pages = (len(self.db)-1) // 5
        if event[0] == wasp.EventType.DOWN:
            page = page - 1 if page > 0 else pages
        if event[0] == wasp.EventType.UP:
            page = page + 1 if page < pages else 0
        self.page = page

        mute = wasp.watch.display.mute
        mute(True)
        self._draw()
        mute(False)

    def touch(self, event):
        """Notify the application of a touchscreen touch event."""
        for module, checkbox in self.get_page():
            if checkbox.touch(event):
                label = checkbox.label.replace(' ', '')
                if checkbox.state:
                    wasp.system.register('apps.{}.{}App'.format(module, label))
                else:
                    for app in wasp.system.launcher_ring:
                        if type(app).__name__.startswith(label):
                            wasp.system.launcher_ring.remove(app)
                            break
                break

    def _draw(self):
        """Draw the display from scratch."""
        wasp.watch.drawable.fill()
        self.si.draw()
        for _, checkbox in self.get_page():
            checkbox.draw()
