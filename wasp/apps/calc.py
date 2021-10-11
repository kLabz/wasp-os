# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Johannes Wache
"""Calculator
~~~~~~~~~~~~~

This is a simple calculator app that uses the build-in eval() function to
compute the solution.

.. figure:: res/CalcApp.png
    :width: 179
"""

import wasp, fonts

# 2-bit RLE, 64x64, generated from ./res/calc_icon.png, 301 bytes
icon = (
    b'\x02'
    b'@@'
    b'?\xff\x89@\xacW\x04\x97\rY\x02\x99\x0cY\x02\x99'
    b'\x0cY\x02\x99\x0cY\x02\x99\x0cK\x03K\x02\x99\x0cK'
    b'\x03K\x02\x99\x0cK\x03K\x02\x99\x0cK\x03K\x02\x99'
    b'\x0cK\x03K\x02\x99\x0cK\x03K\x02\x99\x0cE\x0fE'
    b'\x02\x85\x0f\x85\x0cE\x0fE\x02\x85\x0f\x85\x0cE\x0fE'
    b'\x02\x85\x0f\x85\x0cK\x03K\x02\x99\x0cK\x03K\x02\x99'
    b'\x0cK\x03K\x02\x99\x0cK\x03K\x02\x99\x0cK\x03K'
    b'\x02\x99\x0cK\x03K\x02\x99\x0cY\x02\x99\x0cY\x02\x99'
    b'\x0cY\x02\x99\x0cY\x02\x99\rW\x04\x97?O\x97\x04'
    b'\xd7\r\x99\x02\xd9\x0c\x99\x02\xd9\x0c\x99\x02\xd9\x0c\x99\x02'
    b'\xd9\x0c\x99\x02\xd9\x0c\x86\x02\x88\x02\x87\x02\xd9\x0c\x86\x03'
    b'\x86\x03\x87\x02\xd9\x0c\x87\x03\x84\x03\x88\x02\xc5\x0f\xc5\x0c'
    b'\x88\x03\x82\x03\x89\x02\xc5\x0f\xc5\x0c\x89\x06\x8a\x02\xc5\x0f'
    b'\xc5\x0c\x8a\x04\x8b\x02\xd9\x0c\x8a\x04\x8b\x02\xd9\x0c\x89\x06'
    b'\x8a\x02\xd9\x0c\x88\x03\x82\x03\x89\x02\xc5\x0f\xc5\x0c\x87\x03'
    b'\x84\x03\x88\x02\xc5\x0f\xc5\x0c\x86\x03\x86\x03\x87\x02\xc5\x0f'
    b'\xc5\x0c\x86\x02\x88\x02\x87\x02\xd9\x0c\x99\x02\xd9\x0c\x99\x02'
    b'\xd9\x0c\x99\x02\xd9\x0c\x99\x02\xd9\x0c\x99\x02\xd9\x0c\x99\x02'
    b'\xd9\r\x97\x04\xd7?\xff\t'
)

fields = ( '789+('
           '456-)'
           '123*^'
           'C0./=' )

class CalculatorApp():
    NAME = 'Calc'
    ICON = icon

    def __init__(self):
        self.output = ""

    def foreground(self):
        self._draw()
        self._update()
        wasp.system.request_event(wasp.EventMask.TOUCH)

    def touch(self, event):
        if (event[2] < 48):
            if (event[1] > 200): # undo button pressed
                if (self.output != ""):
                    self.output = self.output[:-1]
        else:
            x = event[1] // 47
            y = (event[2] // 48) - 1

            # Error handling for touching at the border
            if x > 4:
                x = 4
            if y > 3:
                y = 3
            button_pressed = fields[x + 5*y]
            if (button_pressed == "C"):
                self.output = ""
            elif (button_pressed == "="):
                try:
                    self.output = str(eval(self.output.replace('^', '**')))[:12]
                except:
                    wasp.watch.vibrator.pulse()
            else:
                self.output +=  button_pressed
        self._update()

    def _draw(self):
        draw = wasp.watch.drawable

        hi = wasp.system.theme('bright')
        lo = wasp.system.theme('mid')
        mid = draw.lighten(lo, 2)
        bg = draw.darken(wasp.system.theme('ui'), wasp.system.theme('contrast'))
        bg2 = draw.darken(bg, 2)

        # Draw the background
        draw.fill(0, 0, 0, 239, 47)
        draw.fill(0, 236, 239, 3)
        draw.fill(bg, 141, 48, 239-141, 235-48)
        draw.fill(bg2, 0, 48, 140, 235-48)

        # Make grid:
        draw.set_color(lo)
        for i in range(4):
            # horizontal lines
            draw.line(x0=0,y0=(i+1)*47,x1=239,y1=(i+1)*47)
            # vertical lines
            draw.line(x0=(i+1)*47,y0=47,x1=(i+1)*47,y1=235)
        draw.line(x0=0, y0=47, x1=0, y1=236)
        draw.line(x0=239, y0=47, x1=239, y1=236)
        draw.line(x0=0, y0=236, x1=239, y1=236)

        # Draw button labels
        draw.set_color(hi, bg2)
        for x in range(5):
            if x == 3:
                draw.set_color(mid, bg)
            for y in range(4):
                label = fields[x + 5*y]
                if (x == 0):
                    draw.string(label, x*47+14, y*47+60)
                else:
                    draw.string(label, x*47+16, y*47+60)
        draw.set_color(hi)
        draw.string("<", 215, 10)

    def _update(self):
        output = self.output if len(self.output) < 12 else self.output[len(self.output)-12:]
        wasp.watch.drawable.string(output, 0, 14, width=200, right=True)
