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
import fonts.sans36 as sans36
import fonts.sans28 as sans28
import fonts.sans24 as sans24
import fonts.sans18 as sans18

# TODO: move somewhere else?
# TODO: fix bad color
clock_bg = (
    b'\x02'
    b'\xf0\xd6'
    b'?\xb0@\xc1A?\xafB?\xaeC?\xadD?\xab'
    b'F?\xaaG?\xa9H?\xa8I?\xa7J?\xa6K'
    b'?\xa5L?\xa4M?\xa2O?\xa1P?\xa0Q?'
    b'\x9fR?\x9eS?\x9dT?\x9cU?\x9bV?\x99'
    b'X?\x98Y?\x97Z?\x96[?\x95\\?\x94]'
    b'?\x93^?\x92_?\x91`?\x8fb?\x8ec?'
    b'\x8dd?\x8ce?\x8bf?\x8ag?\x89h?\x88'
    b'i?\x86k?\x85l?\x84m?\x83n?\x82o'
    b'?\x81p?\x80q?\x7fr?}t?|u?'
    b'{v?zw?yx?xy?wz?v'
    b'{?t}?s~?r\x7f\x00?q\x7f\x01?'
    b'p\x7f\x02?o\x7f\x03?n\x7f\x04?m\x7f\x05?'
    b'k\x7f\x07?j\x7f\x08?i\x7f\t?h\x7f\n?'
    b'g\x7f\x0b?f\x7f\x0c?e\x7f\r?d\x7f\x0e?'
    b'c\x7f\x0f?a\x7f\x11?`\x7f\x12?_\x7f\x13?'
    b'^\x7f\x14?]\x7f\x15?\\\x7f\x16?[\x7f\x17?'
    b'Z\x7f\x18?X\x7f\x1a?W\x7f\x1b?V\x7f\x1c?'
    b'U\x7f\x1d?\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
    b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
    b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
    b'\xff\xff\xff\xff\xff\xff\xe9\x7f[?\x16\x7f\\?\x15\x7f'
    b']?\x14\x7f^?\x13\x7f_?\x12\x7f`?\x11\x7f'
    b'a?\x0f\x7fc?\x0e\x7fd?\r\x7fe?\x0c\x7f'
    b'f?\x0b\x7fg?\n\x7fh?\t\x7fi?\x08\x7f'
    b'j?\x07\x7fk?\x05\x7fm?\x04\x7fn?\x03\x7f'
    b'o?\x02\x7fp?\x01\x7fq?\x00\x7fr>\x7fs'
    b'=\x7ft;\x7fv:\x7fw9\x7fx8\x7fy7'
    b'\x7fz6\x7f{5\x7f|4\x7f}2\x7f\x7f1\x7f'
    b'\x800\x7f\x81/\x7f\x82.\x7f\x83-\x7f\x84,\x7f\x85'
    b"+\x7f\x86)\x7f\x88(\x7f\x89'\x7f\x8a&\x7f\x8b%"
    b'\x7f\x8c$\x7f\x8d#\x7f\x8e"\x7f\x8f \x7f\x91\x1f\x7f'
    b'\x92\x1e\x7f\x93\x1d\x7f\x94\x1c\x7f\x95\x1b\x7f\x96\x1a\x7f\x97'
    b'\x19\x7f\x98\x18\x7f\x99\x16\x7f\x9b\x15\x7f\x9c\x14\x7f\x9d\x13'
    b'\x7f\x9e\x12\x7f\x9f\x11\x7f\xa0\x10\x7f\xa1\x0f\x7f\xa2\r\x7f'
    b'\xa4\x0c\x7f\xa5\x0b\x7f\xa6\n\x7f\xa7\t\x7f\xa8\x08\x7f\xa9'
    b'\x07\x7f\xaa\x06\x7f\xab\x04\x7f\xad\x03\x7f\xae\x02\x7f\xaf\x01'
    b'\x7f\xff\xa1'
)

class ChronoApp():
    """Simple analogue clock application.
    """
    NAME = 'Chrono'

    def __init__(self):
        self.__battery = -1
        self.__battery_step = -1
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
        battery = int(80 / 100 * 239) # TODO: remove

        if not redraw and self.__ss == now[5] and self.__battery == battery and self.__battery_step == -1:
            return

        if abs(battery - self.__battery) > 20:
            redraw = True

        if redraw:
            # Clear the display
            draw.fill()

            # Initial triangle draw; this is quite expensive
            # TODO: try generating a matrix and blit?
            # for x in range(240):
            #     xx = 239 - x
            #     if xx > battery:
            #         draw.line(xx, 213, 239, 0, 1, ui)
            #     else:
            #         draw.line(xx, 213, 239, 0, 1, mid)

            # Temporary alternative -----------------------------

            # Draw battery background (need to fix color)
            draw.blit(clock_bg, 0, 0)

            # Draw current battery line
            x = battery + int(((213-136) * (239-battery)) / 213)
            draw.line(battery, 213, x, 136, 1, mid)
            x = battery + int(((213-81) * (239-battery)) / 213)
            draw.line(x, 81, 239, 0, 1, mid)

            # Trigger battery filling (in multiple steps)
            self.__battery_step = 0
            self.__battery_steps = int(battery / 10)
            self.__battery_target = battery

            # see code related to __battery_step below too
            # ---------------------------------------------------

            # Prepare clock
            # draw.fill(0, 0, 82, 240, 54)
            draw.set_color(mid)
            draw.set_font(sans36)
            draw.string(':', 84, 91, 18)

            # Prepare heart rate/steps
            # TODO: fix bad colors
            draw.blit(icons.wf_heart, 4, 219, mid)
            draw.blit(icons.wf_steps, 217, 218, ui)

            # Reset cached values to force redraw
            self.__hh = -1
            self.__mm = -1
            self.__ss = -1
            self.__dd = -1
            self.__st = -1
            self.__hr = -2

        else:
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

        if self.__battery_step > -1:
            for i in range(0, self.__battery_target, self.__battery_steps):
                xx = i + self.__battery_step
                if xx >= 0 and xx < battery:
                    x = xx + int(((213-136) * (239-xx)) / 213)
                    draw.line(xx, 213, x, 136, 1, mid)
                    x = xx + int(((213-81) * (239-xx)) / 213)
                    draw.line(x, 81, 239, 0, 1, mid)

            if self.__battery_step == self.__battery_steps:
                self.__battery_step = -1
            else:
                self.__battery_step += 1

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
