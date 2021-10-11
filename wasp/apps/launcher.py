# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Application launcher
~~~~~~~~~~~~~~~~~~~~~~~

.. figure:: res/LauncherApp.png
    :width: 179
"""

import wasp
import icons
import fonts.sans18 as sans18

class LauncherApp():
    """An application launcher application."""
    NAME = 'Launcher'
    ICON = icons.app

    def __init__(self):
        self._scroll = wasp.widgets.ScrollIndicator(y=6)

    def foreground(self):
        """Activate the application."""
        self._page = 0
        self._draw()
        wasp.system.request_event(wasp.EventMask.TOUCH |
                                  wasp.EventMask.SWIPE_UPDOWN)

    def swipe(self, event):
        i = self._page
        n = self._num_pages
        if event[0] == wasp.EventType.UP:
            i += 1
            if i >= n:
                i -= 1
                wasp.watch.vibrator.pulse()
                return
        else:
            i -= 1
            if i < 0:
                wasp.system.switch(wasp.system.quick_ring[0])
                return

        self._page = i
        wasp.watch.display.mute(True)
        self._draw()
        wasp.watch.display.mute(False)

    def touch(self, event):
        page = self._get_page(self._page)
        x = event[1]
        y = event[2]
        app = page[3 * (y // 74) + (x // 74)]
        if app:
            wasp.system.switch(app)
        else:
            wasp.watch.vibrator.pulse()

    @property
    def _num_pages(self):
        """Work out what the highest possible pages it."""
        num_apps = len(wasp.system.launcher_ring)
        return (num_apps + 8) // 9

    def _get_page(self, i):
        apps = wasp.system.launcher_ring
        page = apps[9*i: 9*(i+1)]
        while len(page) < 9:
            page.append(None)
        return page

    def _draw(self):
        """Redraw the display from scratch."""
        def draw_app(app, x, y):
            if not app:
                return
            draw.blit(app.ICON if 'ICON' in dir(app) else icons.app, x+14, y+14,
                    wasp.system.theme('bright'), wasp.system.theme('mid'),
                    wasp.system.theme('ui'), True)
            draw.set_font(sans18)
            draw.set_color(wasp.system.theme('mid'))

        draw = wasp.watch.drawable
        page_num = self._page
        page = self._get_page(page_num)

        draw.fill()
        draw_app(page[0],   0,   0)
        draw_app(page[1],  74,   0)
        draw_app(page[2], 148,   0)
        draw_app(page[3],   0,  74)
        draw_app(page[4],  74,  74)
        draw_app(page[5], 148,  74)
        draw_app(page[6],   0, 148)
        draw_app(page[7],  74, 148)
        draw_app(page[8], 148, 148)

        scroll = self._scroll
        scroll.up = page_num > 0
        scroll.down = page_num < (self._num_pages-1)
        scroll.draw()
