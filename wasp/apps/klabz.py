# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2021 Rudy Geslin

"""Custom watchface
~~~~~~~~~~~~~~~~~

Shows the time as a traditional watch face together with a battery meter.

.. figure:: res/KLabzApp.png
    :width: 179

    Screenshot of the custom watchface
"""

import math
import wasp
import icons
import micropython
import fonts.sans36 as sans36
import fonts.sans28 as sans28
import fonts.sans24 as sans24
import fonts.sans18 as sans18

@micropython.viper
def _fill(mv, color: int, count: int, offset: int):
    p = ptr16(mv)
    color = (color >> 8) + ((color & 0xff) << 8)

    for x in range(offset, offset+count):
        p[x] = color

class KLabzApp():
    """Custom watch face with some style
    """
    NAME = 'KLabz'

    def __init__(self):
        self.__battery = -1
        self.__hh = -1
        self.__mm = -1
        self.__ss = -1
        self.__dd = -1
        self.__st = -1
        self.__hr = -2
        self.__bluetooth = False
        self.__plug = False

    def foreground(self):
        """Activate the application.

        Redraw the display and request a periodic tick callback every second.
        """
        # wasp.system.bar.clock = False
        self._draw(True)
        wasp.system.request_tick(1000)

    def sleep(self):
        """Prepare to enter the low power mode.

        :returns: True, which tells the system manager not to automatically
                  switch to the default application before sleeping.
        """
        return True

    def wake(self):
        """Return from low power mode.

        Time will have changes whilst we have been asleep so we must
        udpate the display (but there is no need for a full redraw because
        the display RAM is preserved during a sleep.
        """
        self._draw()

    def tick(self, ticks):
        """Periodic callback to update the display."""
        self._draw()

    def preview(self):
        """Provide a preview for the watch face selection."""
        wasp.system.bar.clock = False
        self._draw(True)

    def _draw(self, redraw=False):
        """Draw or lazily update the display.

        The updates are as lazy by default and avoid spending time redrawing
        if the time on display has not changed. However if redraw is set to
        True then a full redraw is be performed.
        """
        draw = wasp.watch.drawable
        hi = wasp.system.theme('bright')
        mid = wasp.system.theme('mid')
        ui = wasp.system.theme('ui')

        now = wasp.watch.rtc.get_localtime()
        battery = int(wasp.watch.battery.level() / 100 * 239)
        hr = -1 # TODO: fetch heart rate somehow..

        # Try to avoid some crashes on startup..
        try:
            plug = wasp.watch.battery.charging()
        except:
            plug = False

        # Try to avoid some crashes on startup..
        try:
            bluetooth = wasp.watch.connected()
        except:
            bluetooth = False

        # try/except is necessary if StepCounterApp is not launched
        try:
            st = wasp.watch.accel.steps
        except:
            st = 0

        if redraw:
            # Clear the display
            draw.fill()

            # Prepare heart rate/steps
            draw.blit(icons.wf_heart, 4, 219, mid)
            draw.blit(icons.wf_steps, 217, 218, ui)

            # Prepare clock
            draw.set_color(mid)
            draw.set_font(sans36)
            draw.string(':', 85, 91, 18)

            # Reset cached values to force redraw
            self.__battery = -1
            self.__bluetooth = -1
            self.__plug = -1
            self.__dd = -1
            self.__hh = -1
            self.__mm = -1
            self.__ss = -1
            self.__st = -1
            self.__hr = -2

        if self.__battery != battery:
            # Optimized way of drawing the triangles
            display = draw._display

            # Top "half" -- part with date
            display.set_window(180, 0, 60, 24)
            display.quick_start()
            for i in range(0, 24):
                buf = display.linebuffer[0:60*2]
                bg_len = math.floor((i*240) / 214)
                bg_pos = 60 - bg_len
                bar_len = math.floor((i*battery) / 214)
                _fill(buf, 0, bg_pos, 0)
                _fill(buf, mid, bar_len, bg_pos)
                _fill(buf, ui, bg_len - bar_len, bg_pos + bar_len)
                display.quick_write(buf)
            display.quick_end()

            # Top "half" -- rest
            display.set_window(80, 24, 160, 82 - 24)
            display.quick_start()
            for i in range(0, 82 - 24):
                buf = display.linebuffer[0:160*2]
                bg_len = math.floor(((i+24)*240) / 214)
                bg_pos = 160 - bg_len
                bar_len = math.floor(((i+24)*battery) / 214)
                _fill(buf, 0, bg_pos, 0)
                _fill(buf, mid, bar_len, bg_pos)
                _fill(buf, ui, bg_len - bar_len, bg_pos + bar_len)
                display.quick_write(buf)
            display.quick_end()

            # Bottom "half"
            display.set_window(0, 136, 240, 214 - 136)
            display.quick_start()
            for i in range(0, 214 - 136):
                buf = display.linebuffer
                bg_len = math.floor(((i+136)*240) / 214)
                bg_pos = 240 - bg_len
                bar_len = math.floor(((i+136)*battery) / 214)
                _fill(buf, 0, bg_pos, 0)
                _fill(buf, mid, bar_len, bg_pos)
                _fill(buf, ui, bg_len - bar_len, bg_pos + bar_len)
                display.quick_write(buf)
            display.quick_end()

        if self.__dd != now[2]:
            days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
            draw.set_color(hi)
            draw.set_font(sans24)
            day = days[now[6]]
            draw.string(day, 6, 6)
            draw.set_color(mid)
            draw.string('{}'.format(now[2]), 10 + draw.bounding_box(day)[0], 6)

        if self.__plug != plug:
            if plug:
                draw.blit(icons.wf_plug, 6, 28, mid)
            else:
                # Clear bluetooth icon too if any
                draw.fill(0, 6, 28, 32, 18)

        if self.__plug != plug or self.__bluetooth != bluetooth:
            if bluetooth:
                if plug:
                    draw.blit(icons.wf_bluetooth, 28, 28, mid)
                else:
                    draw.blit(icons.wf_bluetooth, 6, 28, mid)
            else:
                if plug:
                    draw.fill(0, 28, 28, 10, 18)
                else:
                    draw.fill(0, 6, 28, 10, 18)

        if self.__hh != now[3]:
            draw.set_color(hi)
            draw.set_font(sans36)
            if now[3] < 10:
                draw.string('0{}'.format(now[3]), 18, 91, 72)
            else:
                draw.string('{}'.format(now[3]), 18, 91, 72)
            draw.set_color(0)

        if self.__mm != now[4]:
            draw.set_color(hi)
            draw.set_font(sans36)
            if now[4] < 10:
                draw.string('0{}'.format(now[4]), 98, 91, 72)
            else:
                draw.string('{}'.format(now[4]), 98, 91, 72)

        if self.__ss != now[5]:
            draw.set_color(mid)
            draw.set_font(sans28)
            if now[5] < 10:
                draw.string('0{}'.format(now[5]), 167, 99, 56)
            else:
                draw.string('{}'.format(now[5]), 167, 99, 56)

        if self.__hr != hr:
            draw.set_color(mid)
            draw.set_font(sans18)
            draw.fill(0, 25, 219, 80, 18)
            if hr == -1:
                draw.string('-', 25, 219)
            else:
                draw.string('{}'.format(hr), 25, 219)

        if self.__st != st:
            draw.set_color(ui)
            draw.set_font(sans18)
            draw.string('{}'.format(st), 133, 219, 80, True)

        # Update references
        self.__battery = battery
        self.__bluetooth = bluetooth
        self.__plug = plug
        self.__dd = now[2]
        self.__hh = now[3]
        self.__mm = now[4]
        self.__ss = now[5]
        self.__hr = hr
        self.__st = st
