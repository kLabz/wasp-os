# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson
# Copyright (C) 2020 Carlos Gil

"""Music Player for GadgetBridge
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. figure:: res/MusicApp.png
        :width: 179

        Screenshot of the Music Player application

Music Player Controller:

* Touch: play/pause
* Swipe UPDOWN: Volume down/up
* Swipe LEFTRIGHT: next/previous
"""

import wasp

import icons
import time

from micropython import const

# 2-bit RLE, 64x64, generated from ./res/music_icon.png, 512 bytes
icon = (
    b'\x02'
    b'@@'
    b'?\xff\xa1@\xc6B>B>B>B:B\x02B'
    b':B\x02B:B\x02B&B\x12B\x02B&B'
    b'\x12B\x02B&B\x02\x80\xc1\x82\x0eB\x02B&B'
    b'\x02\x82\x0eB\x02B&B\x02\x82\x0eB\x02B\x02\x82'
    b'\x0e\x82\x12B\x02\x82\x0eB\x02B\x02\x82\x0e\x82\x12B'
    b'\x02\x82\x02\x82\x06\x82\x02B\x02B\x02\x82\x0e\x82\x12B'
    b'\x02\x82\x02\x82\x06\x82\x02B\x02B\x02\x82\x0e\x82\x12B'
    b'\x02\x82\x02\x82\x06\x82\x02B\x02B\x02\x82\x02\x82\n\x82'
    b'\x02\x82\x0eB\x02\x82\x02\x82\x06\x82\x02B\x02B\x02\x82'
    b'\x02\x82\n\x82\x02\x82\x0eB\x02\x82\x02\x82\x02\x82\x02\x82'
    b'\x02B\x02B\x02\x82\x02\x82\x02\x82\x06\x82\x02\x82\x0eB'
    b'\x02\x82\x02\x82\x02\x82\x02\x82\x02B\x02B\x02\x82\x02\x82'
    b'\x02\x82\x06\x82\x02\x82\x0eB\x02\x82\x02\x82\x02\x82\x02\x82'
    b'\x02B\x02B\x02\x82\x02\x82\x02\x82\x02\x82\x02\x82\x02\x82'
    b'\x0eB\x02\x82\x02\x82\x02\x82\x02\x82\x02B\x02B\x02\x82'
    b'\x02\x82\x02\x82\x02\x82\x02\x82\x02\x82\x0eB\x02\x82\x02\x82'
    b'\x02\x82\x02\x82\x02B\x02B\x02\x82\x02\x82\x02\x82\x06\x82'
    b'\x02\x82\x0eB\x02\x82\x02\x82\x02\x82\x02\x82\x02B\x02B'
    b'\x02\x82\x02\x82\x02\x82\x06\x82\x02\x82\x0eB\x02\x82\x02\x82'
    b'\x06\x82\x02B\x02B\x02\x82\x02\x82\n\x82\x02\x82\x0eB'
    b'\x02\x82\x02\x82\x06\x82\x02B\x02B\x02\x82\x02\x82\n\x82'
    b'\x02\x82\x0eB\x02\x82\x02\x82\x06\x82\x02B\x02B\x02\x82'
    b'\x0e\x82\x12B\x02\x82\x02\x82\x06\x82\x02B\x02B\x02\x82'
    b'\x0e\x82\x12B\x02\x82\x0eB\x02B\x02\x82\x0e\x82\x12B'
    b'\x02\x82\x0eB\x02B\x02\x82\x0e\x82\x12B\x02\x82\x0eB'
    b'\x02B&B\x02\x82\x0eB\x02B&B\x12B\x02B'
    b'\x0b\xc7\x14B\x12B\x02B\t\xcb&B\x02B\x08\xcd'
    b"%B\x02B\x07\xcf$B\x02B\x06\xd1'B\x05\xc8"
    b'\x01\xca&B\x05\xc8\x02\xc9&B\x04\xc9\x03\xc9%B'
    b'\x04\xc9\x04\xc8+\xc9\x05\xc7+\xc9\x06\xc6+\xc9\x05\xc7'
    b'+\xc9\x04\xc8+\xc9\x03\xc9,\xc8\x02\xc9-\xc8\x01\xca'
    b'.\xd10\xcf2\xcd4\xcb7\xc7?\xff\x0f'
)

DISPLAY_WIDTH = const(240)
ICON_SIZE = const(72)
CENTER_AT = const((DISPLAY_WIDTH - ICON_SIZE) // 2)

class MusicPlayerApp(object):
    """ Music Player Controller application."""
    NAME = 'Music'
    ICON = icon

    def __init__(self):
        self._pauseplay = wasp.widgets.GfxButton(CENTER_AT, CENTER_AT, icons.play)
        self._back = wasp.widgets.GfxButton(0, 120-12, icons.back)
        self._fwd = wasp.widgets.GfxButton(240-48, 120-12, icons.fwd)
        self._play_state = False
        self._musicstate = 'pause'
        self._artist = ''
        self._track = ''
        self._state_changed = True
        self._track_changed = True
        self._artist_changed = True

    def _send_cmd(self, cmd):
        print('\r')
        for i in range(1):
            for i in range(0, len(cmd), 20):
                print(cmd[i: i + 20], end='')
                time.sleep(0.2)
            print(' ')
        print(' ')

    def _fill_space(self, key):
        if key == 'top':
            wasp.watch.drawable.fill(
                x=0, y=0, w=DISPLAY_WIDTH, h=CENTER_AT)
        elif key == 'down':
            wasp.watch.drawable.fill(x=0, y=CENTER_AT + ICON_SIZE,
                                     w=DISPLAY_WIDTH,
                            h=DISPLAY_WIDTH - (CENTER_AT + ICON_SIZE))

    def foreground(self):
        """Activate the application."""
        state = wasp.system.musicstate.get('state')
        artist = wasp.system.musicinfo.get('artist')
        track = wasp.system.musicinfo.get('track')
        if state:
            self._musicstate = state
            if self._musicstate == 'play':
                self._play_state = True
            elif self._musicstate == 'pause':
                self._play_state = False
        if artist:
            self._artist = artist
        if track:
            self._track = track
        wasp.watch.drawable.fill()
        self.draw()
        wasp.system.request_tick(1000)
        wasp.system.request_event(wasp.EventMask.SWIPE_UPDOWN |
                                  wasp.EventMask.TOUCH)

    def background(self):
        """De-activate the application (without losing state)."""
        self._state_changed = True
        self._track_changed = True
        self._artist_changed = True

    def tick(self, ticks):
        wasp.system.keep_awake()
        music_state_now = wasp.system.musicstate.get('state')
        music_artist_now = wasp.system.musicinfo.get('artist')
        music_track_now = wasp.system.musicinfo.get('track')
        if music_state_now:
            if music_state_now != self._musicstate:
                self._musicstate = music_state_now
                self._state_changed = True
        else:
            self._state_changed = False
        wasp.system.musicstate = {}
        if music_track_now:
            if music_track_now != self._track:
                self._track = music_track_now
                self._track_changed = True
        else:
            self._track_changed = False
        if music_artist_now:
            if music_artist_now != self._artist:
                self._artist = music_artist_now
                self._artist_changed = True
        else:
            self._artist_changed = False
        wasp.system.musicinfo = {}
        self._update()

    def swipe(self, event):
        """
        Notify the application of a touchscreen swipe event.
        """
        if event[0] == wasp.EventType.UP:
            self._send_cmd('{"t":"music", "n":"volumeup"} ')
        elif event[0] == wasp.EventType.DOWN:
            self._send_cmd('{"t":"music", "n":"volumedown"} ')

    def touch(self, event):
        if self._pauseplay.touch(event):
            self._play_state = not self._play_state
            if self._play_state:
                self._musicstate = 'play'
                self._pauseplay.gfx = icons.pause
                self._pauseplay.draw()
                self._send_cmd('{"t":"music", "n":"play"} ')
            else:
                self._musicstate = 'pause'
                self._pauseplay.gfx = icons.play
                self._pauseplay.draw()
                self._send_cmd('{"t":"music", "n":"pause"} ')
        elif self._back.touch(event):
            self._send_cmd('{"t":"music", "n":"previous"} ')
        elif self._fwd.touch(event):
            self._send_cmd('{"t":"music", "n":"next"} ')

    def draw(self):
        """Redraw the display from scratch."""
        self._draw()

    def _draw(self):
        """Redraw the updated zones."""
        if self._state_changed:
            self._pauseplay.draw()
        if self._track_changed:
            self._draw_label(self._track, 24 + 144)
        if self._artist_changed:
            self._draw_label(self._artist, 12)
        self._back.draw()
        self._fwd.draw()

    def _draw_label(self, label, pos):
        """Redraw label info"""
        if label:
            draw = wasp.watch.drawable
            chunks = draw.wrap(label, 240)
            self._fill_space(pos)
            for i in range(len(chunks)-1):
                sub = label[chunks[i]:chunks[i+1]].rstrip()
                draw.string(sub, 0, pos + 24 * i, 240)

    def _update(self):
        if self._musicstate == 'play':
            self._play_state = True
            self._pauseplay.gfx = icons.pause
        elif self._musicstate == 'pause':
            self._play_state = False
            self._pauseplay.gfx = icons.play
        self._draw()

    def update(self):
        pass
