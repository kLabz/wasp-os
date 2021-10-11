# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson
# Copyright (C) 2020 Carlos Gil

"""Weather for GadgetBridge and wasp-os companion
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. figure:: res/WeatherApp.png
        :width: 179

        Screenshot of the Weather application

"""

import wasp

import icons
import time
import fonts.sans36

# 2-bit RLE, 64x64, generated from ./res/weather_icon.png, 174 bytes
icon = (
    b'\x02'
    b'@@'
    b'?\xff\xff\xff_\xc1>\xc3=\xc3=\xc3/\xc1\r\xc3'
    b'\r\xc1 \xc3\x0c\xc3\x0c\xc3 \xc3\x0b\xc3\x0b\xc3"\xc3'
    b'\n\xc3\n\xc3$\xc3\x15\xc3&\xc3\x13\xc3(\xc3\x05@'
    b'\xacG\x05\xc3*\xc1\x04K\x04\xc1/M2O0Q'
    b'.S-S,U!\xc8\x02U\x02\xc8\x16\xc9\x02U'
    b'\t\xc2\x16\xc8\x02R.Q\x05\x87#O\x04\x8d!M'
    b'\x03\x91\x1fI\x06\x93\x1fF\x07\x95\x1fD\x04\x99 B'
    b'\x03\x9c\x1b\xc1\x07\x9d\x1a\xc3\x05\x9e\x19\xc3\x05\x9f\x18\xc3'
    b'\x05\xa1\x16\xc3\x06\xa2\x14\xc3\x07\xa3\x12\xc3\x08\xa4\x12\xc1'
    b'\t\xa4\x1c\xa3\x1e\x8e\x01\x92 \x8d\x02\x90"\x8b\x04\x8d'
    b'%\x89\x07\x87+\x85?\xff\xe1'
)

class WeatherApp(object):
    """ Weather application."""
    NAME = 'Weather'
    ICON = icon

    def __init__(self):
        self._temp = -1
        self._hum = 0
        self._txt = ''
        self._wind = 0
        self._loc = ''
        self._temp_changed = True
        self._hum_changed = True
        self._txt_changed = True
        self._wind_changed = True
        self._loc_changed = True

    def foreground(self):
        """Activate the application."""
        temp = wasp.system.weatherinfo.get('temp')
        hum = wasp.system.weatherinfo.get('hum')
        txt = wasp.system.weatherinfo.get('txt')
        wind = wasp.system.weatherinfo.get('wind')
        loc = wasp.system.weatherinfo.get('loc')
        if temp:
            self._temp = temp
        if hum:
            self._hum = hum
        if txt:
            self._txt = txt
        if wind:
            self._wind = wind
        if loc:
            self._loc = loc
        wasp.watch.drawable.fill()
        self.draw()
        wasp.system.request_tick(1000)

    def background(self):
        """De-activate the application (without losing state)."""
        self._temp_changed = True
        self._hum_changed = True
        self._txt_changed = True
        self._wind_changed = True
        self._loc_changed = True

    def tick(self, ticks):
        wasp.system.keep_awake()
        temp_now = wasp.system.weatherinfo.get('temp')
        hum_now = wasp.system.weatherinfo.get('hum')
        txt_now = wasp.system.weatherinfo.get('txt')
        wind_now = wasp.system.weatherinfo.get('wind')
        loc_now = wasp.system.weatherinfo.get('loc')
        if temp_now:
            if temp_now != self._temp:
                self._temp = temp_now
                self._temp_changed = True
        else:
            self._temp_changed = False
        if hum_now:
            if hum_now != self._hum:
                self._hum = hum_now
                self._hum_changed = True
        else:
            self._hum_changed = False
        if txt_now:
            if txt_now != self._txt:
                self._txt = txt_now
                self._txt_changed = True
        else:
            self._txt_changed = False
        if wind_now:
            if wind_now != self._wind:
                self._wind = wind_now
                self._wind_changed = True
        else:
            self._wind_changed = False
        if loc_now:
            if loc_now != self._loc:
                self._loc = loc_now
                self._loc_changed = True
        else:
            self._loc_changed = False
        wasp.system.weatherinfo = {}
        self._update()

    def draw(self):
        """Redraw the display from scratch."""
        self._draw()

    def _draw(self):
        """Redraw the updated zones."""
        draw = wasp.watch.drawable
        if self._temp != -1:
            units = wasp.system.units
            temp = self._temp - 273.15
            wind = self._wind
            wind_units = "km/h"
            if units == "Imperial":
                temp = (temp * 1.8) + 32
                wind = wind / 1.609
                wind_units = "mph"
            temp = round(temp)
            wind = round(wind)
            if self._temp_changed:
                self._draw_label(str(temp), 54, 36)
            if self._hum_changed:
                self._draw_label("Humidity: {}%".format(self._hum), 160)
            if self._txt_changed:
                self._draw_label(self._txt, 12)
            if self._wind_changed:
                self._draw_label("Wind: {}{}".format(wind, wind_units), 120)
            if self._loc_changed:
                self._draw_label(self._loc, 200)
        else:
            if self._temp_changed:
                draw.fill()
                self._draw_label("No weather data.", 120)

    def _draw_label(self, label, pos, size = 24):
        """Redraw label info"""
        if label:
            draw = wasp.watch.drawable
            draw.reset()
            if size == 36:
                draw.set_font(fonts.sans36)

            draw.string(label, 0, pos, 240)

    def _update(self):
        self._draw()

    def update(self):
        pass
