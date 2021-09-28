# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Heart rate monitor
~~~~~~~~~~~~~~~~~~~~~

A graphing heart rate monitor using a PPG sensor.

.. figure:: res/HeartApp.png
    :width: 179

This program also implements some (entirely optional) debug features to
store the raw heart data to the filesystem so that the samples can be used
to further refine the heart rate detection algorithm.

To enable the logging feature select the heart rate application using the
watch UI and then run the following command via wasptool:

.. code-block:: sh

    ./tools/wasptool --eval 'wasp.system.app.debug = True'

Once debug has been enabled then the watch will automatically log heart
rate data whenever the heart rate application is running (and only
when it is running). Setting the debug flag to False will disable the
logging when the heart rate monitor next exits.

Finally to download the logs for analysis try:

.. code-block:: sh

    ./tools/wasptool --pull hrs.data
"""

import wasp
import machine
import ppg

# 2-bit RLE, 64x64, generated from ./res/heart_icon.png, 399 bytes
icon = (
    b'\x02'
    b'@@'
    b'?\xff\xff\x13@\xc6H\x10H H\x10H\x1cD\x08'
    b'D\x08D\x08D\x18D\x08D\x08D\x08D\x16B\x04'
    b'\x80\xc1\x88\x04B\x04B\x04\x88\x04B\x14B\x04\x88\x04'
    b'B\x04B\x04\x88\x04B\x12B\x02\x90\x02D\x02\x90\x02'
    b'B\x10B\x02\x90\x02D\x02\x90\x02B\x10B\x02\x92\x04'
    b'\x92\x02B\x10B\x02\x92\x04\x92\x02B\x0eB\x02\xac\x02'
    b'B\x0cB\x02\x97\x04\x91\x02B\x0cB\x02\x97\x04\x91\x02'
    b'B\x0cB\x02\x96\x06\x90\x02B\x0cB\x02\x96\x02\xc2\x02'
    b'\x90\x02B\x0cB\x02\x95\x03\xc2\x03\x8f\x02B\x0cB\x02'
    b'\x95\x02\xc4\x02\x8f\x02B\x0cB\x02\x94\x03\xc4\x02\x8f\x02'
    b'B\x0cB\x02\x94\x02\xc5\x03\x8e\x02B\x0cB\x02\x94\x02'
    b'\xc6\x02\x8e\x02B\x0eB\x02\x91\x02\xc3\x01\xc3\x02\x8c\x02'
    b'B\x10B\x02\x91\x02\xc2\x02\xc3\x03\x8b\x02B\x10B\x02'
    b'\x90\x02\xc3\x03\xc3\x02\x8b\x02B&\xc2\x04\xc3\x02\x822'
    b'\xc3\x05\xc2\x02\x82\x1b\xd9\x03\x81\x02\xc2\x05\xce\x0c\xd9\x02'
    b"\x82\x02\xc3\x04\xce'\x82\x03\xc2\x03\xc32\x84\x02\xc2\x03"
    b'\xc2\x1fB\x02\x94\x02\xc3\x01\xc3\x05B\x18B\x02\x94\x03'
    b'\xc2\x01\xc2\x03\x81\x02B\x18B\x02\x95\x02\xc5\x02\x82\x02'
    b'B\x1aB\x02\x93\x02\xc4\x05B\x1cB\x02\x94\x02\xc3\x02'
    b'\x81\x02B\x1eB\x02\x92\x02\xc2\x04B B\x02\x93\x07'
    b'B"B\x02\x91\x05B$B\x02\x94\x02B&B\x02'
    b'\x90\x02B(B\x02\x90\x02B*B\x02\x8c\x02B,'
    b'B\x02\x8c\x02B.B\x02\x88\x02B0B\x02\x88\x02'
    b'B2B\x02\x84\x02B4B\x02\x84\x02B6B\x04'
    b'B8B\x04B:D<D?\xff '
)

class HeartApp():
    """Heart rate monitor application."""
    NAME = 'Heart'
    ICON = icon

    def __init__(self):
        self._debug = False
        self._hrdata = None

    def foreground(self):
        """Activate the application."""
        wasp.watch.hrs.enable()

        # There is no delay after the enable because the redraw should
        # take long enough it is not needed
        draw = wasp.watch.drawable
        draw.fill()
        draw.set_color(wasp.system.theme('bright'))
        draw.string('PPG graph', 0, 6, width=240)

        wasp.system.request_tick(1000 // 8)

        self._hrdata = ppg.PPG(wasp.watch.hrs.read_hrs())
        if self._debug:
            self._hrdata.enable_debug()
        self._x = 0

    def background(self):
        wasp.watch.hrs.disable()
        self._hrdata = None

    def _subtick(self, ticks):
        """Notify the application that its periodic tick is due."""
        draw = wasp.watch.drawable

        spl = self._hrdata.preprocess(wasp.watch.hrs.read_hrs())

        if len(self._hrdata.data) >= 240:
            draw.set_color(wasp.system.theme('bright'))
            draw.string('{} bpm'.format(self._hrdata.get_heart_rate()),
                        0, 6, width=240)

        # Graph is orange by default...
        color = wasp.system.theme('spot1')

        # If the maths goes wrong lets show it in the chart!
        if spl > 100 or spl < -100:
            color = 0xffff
        if spl > 104 or spl < -104:
            spl = 0
        spl += 104

        x = self._x
        draw.fill(0, x, 32, 1, 208-spl)
        draw.fill(color, x, 239-spl, 1, spl)
        if x < 238:
            draw.fill(0, x + 1, 32, 2, 208)
        x += 2
        if x >= 240:
            x = 0
        self._x = x

    def tick(self, ticks):
        """This is an outrageous hack but, at present, the RTC can only
        wake us up every 125ms so we implement sub-ticks using a regular
        timer to ensure we can read the sensor at 24Hz.
        """
        t = machine.Timer(id=1, period=8000000)
        t.start()
        self._subtick(1)
        wasp.system.keep_awake()

        while t.time() < 41666:
            pass
        self._subtick(1)

        while t.time() < 83332:
            pass
        self._subtick(1)

        t.stop()
        del t

    @property
    def debug(self):
        return self._debug

    @debug.setter
    def debug(self, value):
        self._debug = value
        if value and self._hrdata:
            self._hrdata.enable_debug()
