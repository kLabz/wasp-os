# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Analogue clock
~~~~~~~~~~~~~~~~~

Shows the time as a traditional watch face together with a battery meter.

.. figure:: res/ChronoApp.png
    :width: 179

    Screenshot of the analogue clock application
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

class ChronoApp():
    """Simple analogue clock application.
    """
    NAME = 'Chrono'

    def __init__(self):
        self.__battery = -1
        self.__hh = -1
        self.__mm = -1
        self.__ss = -1
        self.__dd = -1
        self.__st = -1
        self.__hr = -2

    def foreground(self):
        """Activate the application.

        Configure the status bar, redraw the display and request a periodic
        tick callback every second.
        """
        wasp.system.bar.clock = False
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

        if not redraw and self.__ss == now[5] and self.__battery == battery:
            return

        redraw_triangles = False
        if abs(battery - self.__battery) > 15:
            redraw_triangles = True

        if redraw:
            # Clear the display
            draw.fill()
            redraw_triangles = True

            # Prepare heart rate/steps
            # TODO: fix bad colors
            draw.blit(icons.wf_heart, 4, 219, mid)
            draw.blit(icons.wf_steps, 217, 218, ui)

            # Prepare clock
            draw.set_color(mid)
            draw.set_font(sans36)
            draw.string(':', 84, 91, 18)

            # Reset cached values to force redraw
            self.__dd = -1
            self.__hh = -1
            self.__mm = -1
            self.__ss = -1
            self.__st = -1
            self.__hr = -2

        if redraw_triangles:
            # Optimized way of drawing the triangles
            display = draw._display
            display.quick_start()

            # Top "half" -- part with date
            display.set_window(160, 0, 80, 24)
            for i in range(0, 24):
                buf = display.linebuffer[0:80*2]
                bg_len = math.floor((i*240) / 214)
                bg_pos = 80 - bg_len
                bar_len = math.floor((i*battery) / 214)
                _fill(buf, 0, bg_pos, 0)
                _fill(buf, mid, bar_len, bg_pos)
                _fill(buf, ui, bg_len - bar_len, bg_pos + bar_len)
                display.quick_write(buf)

            # Top "half" -- rest
            display.set_window(0, 24, 240, 82 - 24)
            for i in range(0, 82 - 24):
                buf = display.linebuffer
                bg_len = math.floor(((i+24)*240) / 214)
                bg_pos = 240 - bg_len
                bar_len = math.floor(((i+24)*battery) / 214)
                _fill(buf, 0, bg_pos, 0)
                _fill(buf, mid, bar_len, bg_pos)
                _fill(buf, ui, bg_len - bar_len, bg_pos + bar_len)
                display.quick_write(buf)

            # Bottom "half"
            display.set_window(0, 136, 240, 214 - 136)
            for i in range(0, 214 - 136):
                buf = display.linebuffer
                bg_len = math.floor(((i+136)*240) / 214)
                bg_pos = 240 - bg_len
                bar_len = math.floor(((i+136)*battery) / 214)
                _fill(buf, mid, bar_len, bg_pos)
                _fill(buf, ui, bg_len - bar_len, bg_pos + bar_len)
                display.quick_write(buf)

            display.quick_end()

        else:
            # "Animated" battery state change
            if self.__battery != battery:
                maxBattery = min(239, max(battery, self.__battery) + 2)
                minBattery = max(0, min(battery, self.__battery) - 2)

                for i in range(maxBattery, min(battery + 1, 239), -1):
                    x = i + int(((213-136) * (239-i)) / 213)
                    draw.line(i, 213, x, 136, 1, ui)
                    x = i + int(((213-81) * (239-i)) / 213)
                    draw.line(x, 81, 239, 0, 1, ui)

                for i in range(minBattery, battery):
                    x = i + int(((213-136) * (239-i)) / 213)
                    draw.line(i, 213, x, 136, 1, mid)
                    x = i + int(((213-81) * (239-i)) / 213)
                    draw.line(x, 81, 239, 0, 1, mid)

        if self.__dd != now[2]:
            dyear = now[0]
            dmonth = now[1] - 2
            if dmonth <= 0:
                dmonth += 12
                dyear -= 1
            c = math.floor(dyear / 100)
            dyear = dyear - (c * 100)
            wd = (now[2] + math.floor(2.6 * dmonth - 0.2) - 2 * c + dyear + math.floor(dyear/4) + math.floor(c/4)) % 7
            days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]

            draw.set_color(hi)
            draw.set_font(sans24)
            day = days[wd - 1]
            draw.string(day, 6, 6)
            draw.set_color(mid)
            draw.string('{}'.format(now[2]), 10 + draw.bounding_box(day)[0], 6)

        if self.__hh != now[3]:
            draw.set_color(hi)
            draw.set_font(sans36)
            draw.string('{}'.format(now[3]).zfill(2), 17, 91, 72)
            draw.set_color(0)

        if self.__mm != now[4]:
            draw.set_color(hi)
            draw.set_font(sans36)
            draw.string('{}'.format(now[4]).zfill(2), 97, 91, 72)

        if self.__ss != now[5]:
            draw.set_color(mid)
            draw.set_font(sans28)
            draw.string('{}'.format(now[5]).zfill(2), 167, 99, 56)

        hr = -1 # TODO: get heart rate somehow
        if self.__hr != hr:
            draw.set_color(mid)
            draw.set_font(sans18)
            draw.fill(25, 219, 80, 18, 0)
            if hr == -1:
                draw.string('-', 25, 219)
            else:
                draw.string('{}'.format(hr), 25, 219)

        st = wasp.watch.accel.steps
        if self.__st != st:
            draw.set_color(ui)
            draw.set_font(sans18)
            draw.string('{}'.format(st), 133, 219, 80, True)

        # Update references
        self.__battery = battery
        self.__dd = now[2]
        self.__hh = now[3]
        self.__mm = now[4]
        self.__ss = now[5]
        self.__hr = hr
        self.__st = st
