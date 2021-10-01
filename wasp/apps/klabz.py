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
import fonts.sans36 as sans36
import fonts.sans28 as sans28
import fonts.sans24 as sans24
import fonts.sans18 as sans18

from draw565 import _fill

# 2-bit RLE, 18x16, generated from res/watch-heart.png, 250 bytes
icon_heart = (
    b'\x02'
    b'\x12\x10'
    b'\x01\x01@TA\x80\xa2\x81\xc0\xc6\xc1\x81@xA\x01'
    b'\x02\x80$\x81A\xc0\xa2\xc1@\xc6A\xc1\x80T\x81\x01'
    b'\x01\x01\xc1E\xc1\xc0*\xc1\xc1AE@\xa2A\x01\x81'
    b'\x80\xc6\x85AA\x81\x81\x87\xc0T\xc1A\x85@NA'
    b'\x80*\x81\xc0\xc6\xc9@\xa2A\xc1\xc4\xc1\x01\x01A\xc8'
    b'\xc1A\xc4A\x01\x01\x80x\x81\xc1\xc1\xc0N\xc1A@'
    b'\xc6D\x80\xa2\x81\xc0x\xc1D\xc1@$A\x80N\x81'
    b'\x81\xc0\xc6\xc1@xA\x01\x81\xc4A\x80$\x81D\xc0'
    b'*\xc1@NA\x80x\x81\x01\xc0\xc6\xc1A\x01\x01\x81'
    b'\x83\x01\x05\x01\x81@\xa2A\x01A\x01\x81\x80*\x81\x07'
    b'\xc0N\xc1@\xc6AD\x81\x81\x01\x80\xa2\x81BA\xc1'
    b'\x05\xc1AC\xc0T\xc1\x01@*A\x80\xc6\x82\x81\xc0'
    b'N\xc1\x07\xc1\x81\x82@\xa2A\x01\x80T\x81\xc0\xc6\xc1'
    b'\xc1@NA\tA\xc1\xc1\xc1A\x80\xa2\x81\xc1A\x0b'
    b'\xc0*\xc1@\xc6ABA\xc1\r\xc1AA\xc1\x0f\xc1'
    b'\xc1\x08'
)

# 2-bit RLE, 23x19, generated from res/watch-steps.png, 301 bytes
icon_steps = (
    b'\x02'
    b'\x17\x13'
    b'\n\x01@NA\x80x\x81\xc0\x9c\xc1@\x9dB\xc1\x81'
    b'\x80$\x81\t\xc0N\xc1@\x9cAA\x01\x80\x9d\x81\xc0'
    b'\xc1\xc1\xc7\xc1\x81@NA\x06\x80*\x81\xc1\xc1\xc1\x01'
    b'\xcb\xc1\xc0x\xc1\x05\xc1@\xc1BA\x01LA\x81\x04'
    b'\x80N\x81BA\x01M\xc1\x05\xc1A\xc0\x9d\xc1\x01A'
    b'AK@rA\n\x01\x80x\x81\xc0\xc1\xc1\xc8@\x9c'
    b'A\x01\x0c\x01\x81\xc1\xc1\xc2\xc1A\x80N\x81\x11\x01\xc0'
    b'$\xc1\x01%@*A\x80x\x81\xc0\x9c\xc1\xc1\x81@'
    b'NA\x01\x0e\x80*\x81\xc0\x9d\xc1@\xc1AEA\x80'
    b'x\x81\x07\xc0N\xc1\x81@*A\xc1\x81\x80\x9d\x81\xc0'
    b'\xc1\xc1\xc9@\x9cA\x05\x80x\x81\xc2\x81A\xcc\xc1\x05'
    b'\xc1\xc2\x81A\xcc\xc1\x05\xc1\xc2\x81A\xcc\xc0r\xc1\x05'
    b'@NA\x80\xc1\x81\x81\xc0x\xc1@\x9cA\x8a\x81\xc1'
    b'\x07\x01\x80*\x81\x01\xc0$\xc1@xA\x80\x9d\x81\xc0'
    b'\xc1\xc1\xc4\xc1\x81A@$A\x0fA\x80N\x81\x81\xc0'
    b'*\xc1\x01\n'
)

# 2-bit RLE, 18x18, generated from res/wp_plug.png, 207 bytes
icon_plug = (
    b'\x02'
    b'\x12\x12'
    b'\x0b@TA\x80\xa2\x81\xc0N\xc1\x0eA@\xc6B\x80'
    b'x\x81\n\x01\x02\xc0T\xc1BA@*A\t\xc1\x81'
    b'\x01\xc1\x80\xc6\x82\x81A\t\xc1\x82\xc0\xa2\xc1\x82\x81A'
    b'\x03A@xA\x80N\x81\x03\xc0*\xc1@\xc6AD'
    b'A\xc1\x03\xc1AA\x80\xa2\x81\x03\x81E\x81\x01\x02\xc1'
    b'AB\xc0T\xc1\x02@$A\x80\xc6\x87\xc0x\xc1\x01'
    b'@*A\x81\x82\x80T\x81\x03\xc0N\xc1@\xc6H\x80'
    b'\xa2\x81AB\xc0T\xc1\x04@NA\x80\xc6\x8b\xc1\x05'
    b'\xc0*\xc1\x8a@\xa2A\x01\x06A\x8a\x80x\x81\x01\x05'
    b'\x81\xc0\xc6\xca@TA\x05\x80N\x81\xc1\xc8\xc1A\x05'
    b'\x81\xc1\xc1\xc1\xc0x\xc1@\xa2A\x80\xc6\x84A\xc0*'
    b'\xc1\x05@NA\x81\x81\x81A\x02\xc1\xc1A\x80$\x81'
    b'\x07\xc0\xc6\xc1\xc1\xc1A\x0e\xc1\xc1A\x0f'
)

# 2-bit RLE, 10x18, generated from res/wp_bluetooth.png, 176 bytes
icon_bluetooth = (
    b'\x02'
    b'\n\x12'
    b'\x04@NA\x01\x08\x80x\x81\xc0\xa2\xc1\x01\x07\x81@'
    b'\xc6A\xc1\x01\x06\x81AA\xc1\x01\x01\x01\x81\x01\x01\x81'
    b'A\x80*\x81A\xc1\x01\xc0N\xc1A@\xa2A\x01\x80'
    b'x\x81\xc0\xc6\xc1\x01\x81\xc1\x81\x01@NA\xc1\x80\xa2'
    b'\x81\xc0x\xc1@\xc6A\x80N\x81A\xc0\xa2\xc1\x01\x02'
    b'\x81AAAA\xc1\x01\x04\x81AA\xc1\x01\x05\x81A'
    b'A\xc1\x01\x04\x81BAA\xc1\x01\x02\x81A\xc1@x'
    b'A\x80\xc6\x81\xc0N\xc1\x81@\xa2A\x01\x80*\x81\xc0'
    b'\xc6\xc1A\x01@xA\xc1\x01A\xc1A\x01A\x01\x01'
    b'A\xc1\x81\xc1\x80\xa2\x81\x01\x04A\xc1\xc1\x81\x01\x05A'
    b'\xc1\x81\x01\x06A\x81\x01\x07\xc0N\xc1\x01\x04'
)

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
        self.__st = -2
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
        battery_level = wasp.watch.battery.level()
        battery = int(battery_level / 100 * 239)
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
            st = -1

        if redraw:
            # Clear the display
            draw.fill()

            # Prepare heart rate/steps
            draw.blit(icon_heart, 4, 219, mid)
            draw.blit(icon_steps, 217, 218, ui)

            # Prepare clock
            draw.set_color(mid)
            draw.set_font(sans36)
            draw.string(':', 85, 91, 18)

            # Reset cached values to force redraw
            self.__battery = -1
            self.__bluetooth = False
            self.__plug = False
            self.__dd = -1
            self.__hh = -1
            self.__mm = -1
            self.__ss = -1
            self.__st = -2
            self.__hr = -2

        if self.__battery != battery:
            # Optimized way of drawing the triangles
            display = draw._display

            # Top "half" -- part with date
            display.set_window(210, 0, 30, 26)
            display.quick_start()
            for i in range(0, 26):
                buf = display.linebuffer
                bg_len = math.floor((i*240) / 214)
                bg_pos = 30 - bg_len
                bar_len = math.floor((i*battery) / 214)
                _fill(buf, 0, bg_pos, 0)
                _fill(buf, mid, bar_len, bg_pos)
                _fill(buf, ui, bg_len - bar_len, bg_pos + bar_len)
                display.quick_write(buf[0:30*2])
            display.quick_end()

            # Top "half" -- rest
            display.set_window(80, 26, 160, 82 - 26)
            display.quick_start()
            for i in range(0, 82 - 26):
                buf = display.linebuffer
                bg_len = math.floor(((i+26)*240) / 214)
                bg_pos = 160 - bg_len
                bar_len = math.floor(((i+26)*battery) / 214)
                _fill(buf, 0, bg_pos, 0)
                _fill(buf, mid, bar_len, bg_pos)
                _fill(buf, ui, bg_len - bar_len, bg_pos + bar_len)
                display.quick_write(buf[0:160*2])
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
                display.quick_write(buf[0:240*2])
            display.quick_end()

            if battery < 194:
                draw.set_color(mid, ui)
                draw.set_font(sans18)
                draw.string('{}%'.format(battery_level), 194, 196, 44, True)

        if self.__dd != now[2]:
            days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
            draw.fill(0, 6, 6, 204, 20)
            draw.set_color(hi)
            draw.set_font(sans24)
            day = days[now[6]]
            draw.string(day, 6, 6)
            draw.set_color(mid)
            draw.string('{}'.format(now[2]), 10 + draw.bounding_box(day)[0], 6)

        if self.__plug != plug:
            if plug:
                draw.blit(icon_plug, 6, 28, mid)
            else:
                # Clear bluetooth icon too if any
                draw.fill(0, 6, 28, 32, 18)

        if self.__plug != plug or self.__bluetooth != bluetooth:
            if bluetooth:
                if plug:
                    draw.blit(icon_bluetooth, 28, 28, mid)
                else:
                    draw.blit(icon_bluetooth, 6, 28, mid)
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
            if st == -1:
                draw.string('-', 133, 219, 80, True)
            else:
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
