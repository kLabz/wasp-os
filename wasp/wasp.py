import sys

import watch as wasp_Watch
import gc
import micropython


class wasp_app_IApplication:
    pass


class wasp_app_BaseApplication:

    def foreground(self):
        pass

    def background(self):
        pass

    def sleep(self):
        return False

    def wake(self):
        pass

    def tick(self,ticks):
        pass

    def touch(self,event):
        pass

    def swipe(self,event):
        return True

    def press(self,eventType,state):
        return True



class TorchApp(wasp_app_BaseApplication):

    def __init__(self):
        self.brightness = None
        self.NAME = "Torch"
        self.ICON = TorchApp.icon
        self.activated = False

    def foreground(self):
        self.brightness = Wasp.system.brightness
        self.draw()
        Wasp.system.requestTick(1000)
        Wasp.system.requestEvent(9)

    def background(self):
        self.activated = False
        Wasp.system.set_brightness(self.brightness)

    def tick(self,_):
        Wasp.system.keepAwake()

    def touch(self,_):
        self.activated = (not self.activated)
        self.draw()

    def press(self,_,state):
        self.activated = (not self.activated)
        self.draw()
        return False

    def draw(self):
        if self.activated:
            wasp_Watch.drawable.fill(65535)
            self.drawTorch(0,0)
            Wasp.system.set_brightness(3)
        else:
            wasp_Watch.drawable.fill()
            self.drawTorch(wasp__Theme_Theme_Impl_.get(Wasp.system.theme,6),65535)
            Wasp.system.set_brightness(self.brightness)

    def drawTorch(self,torch,light):
        draw = wasp_Watch.drawable
        draw.fill(torch,108,107,24,9)
        draw.line(109,116,130,116,1,torch)
        draw.line(110,117,129,117,1,torch)
        draw.line(111,118,128,118,1,torch)
        draw.line(112,119,127,119,1,torch)
        draw.line(113,120,126,120,1,torch)
        draw.line(114,121,125,121,1,torch)
        draw.line(115,122,124,122,1,torch)
        draw.fill(torch,116,123,8,15)
        draw.line(105,94,113,102,2,light)
        draw.line(125,102,133,94,2,light)
        draw.line(119,89,119,100,2,light)



class haxe_iterators_ArrayIterator:

    def __init__(self,array):
        self.current = 0
        self.array = array

    def hasNext(self):
        return (self.current < len(self.array))

    def next(self):
        def _hx_local_3():
            def _hx_local_2():
                _hx_local_0 = self
                _hx_local_1 = _hx_local_0.current
                _hx_local_0.current = (_hx_local_1 + 1)
                return _hx_local_1
            return self.array[_hx_local_2()]
        return _hx_local_3()



class python_internal_ArrayImpl:

    @staticmethod
    def remove(x,e):
        try:
            x.remove(e)
            return True
        except BaseException as _g:
            return False

    @staticmethod
    def _set(x,idx,v):
        l = len(x)
        while (l < idx):
            x.append(None)
            l = (l + 1)
        if (l == idx):
            x.append(v)
        else:
            x[idx] = v
        return v


class HxOverrides:

    @staticmethod
    def stringOrNull(s):
        if (s is None):
            return "null"
        else:
            return s


class python_internal_MethodClosure:

    def __init__(self,obj,func):
        self.obj = obj
        self.func = func

    def __call__(self,*args):
        return self.func(self.obj,*args)



class wasp_Manager:

    def __init__(self):
        self.button = None
        self.launcher = None
        self.bar = None
        self.eventMask = 0
        self.sleepAt = 0
        self.tickExpiry = 0
        self.tickPeriodMs = 0
        self.scheduling = False
        self.scheduled = False
        self.charging = True
        self.nfylev_ms = 40
        self.nfyLevels = [0, 40, 80]
        self.notifyLevel = 2
        self.brightness = 2
        self.blankAfter = 15
        self.theme = (
            b'\x7b\xef'
            b'\x7b\xef'
            b'\x7b\xef'
            b'\xe7\x3c'
            b'\x7b\xef'
            b'\xff\xff'
            b'\xfe\x20'
            b'\xfb\x80'
            b'\xff\x00'
            b'\xdd\xd0'
            b'\x00\x0f'
        )
        self.units = "Metric"
        self.notifications = []
        self.launcherRing = []
        self.quickRing = []
        self.app = None
        self.nfylev_ms = self.nfyLevels[(self.notifyLevel - 1)]

    def init(self):
        if (self.bar is None):
            self.bar = wasp_widgets_StatusBar()
        if (self.launcher is None):
            self.launcher = LauncherApp()
        if (self.button is None):
            self.button = wasp_widgets_PinHandler(wasp_Watch.button)

    def secondaryInit(self):
        if (self.app is None):
            if (len(self.quickRing) == 0):
                self.registerDefaults()
            wasp_Watch.display.poweron()
            wasp_Watch.display.mute(True)
            wasp_Watch.backlight.set(self.brightness)
            self.sleepAt = (wasp_Watch.rtc.uptime + 90)
            if (wasp_Watch.free > 0):
                gc.collect()
                gc.mem_free()
            self.switchApp(self.quickRing[0])

    def registerDefaults(self):
        self.register(TorchApp,True,True,True)

    def register(self,cls,quickRing,watchFace,noExcept):
        app = cls()
        if watchFace:
            python_internal_ArrayImpl._set(self.quickRing, 0, app)
        elif quickRing:
            self.quickRing.append(app)
        else:
            self.launcherRing.append(app)
            self.launcherRing.sort(key = self.appSort)

    def unregister(self,cls):
        inst = cls()
        _g = 0
        _g1 = self.launcherRing
        while (_g < len(_g1)):
            app = _g1[_g]
            _g = (_g + 1)
            if (app.NAME == inst.NAME):
                python_internal_ArrayImpl.remove(self.launcherRing,app)
                break

    def requestTick(self,ticks,periodMs = None):
        if (periodMs is None):
            periodMs = 0
        self.tickPeriodMs = periodMs
        self.tickExpiry = (wasp_Watch.rtc.get_uptime_ms() + periodMs)

    def requestEvent(self,event):
        _hx_local_0 = self
        _hx_local_1 = _hx_local_0.eventMask
        _hx_local_0.eventMask = (_hx_local_1 | event)
        _hx_local_0.eventMask

    def keepAwake(self):
        self.sleepAt = (wasp_Watch.rtc.uptime + self.blankAfter)

    def sleep(self):
        wasp_Watch.backlight.set(0)
        if (not self.app.sleep()):
            self.switchApp(self.quickRing[0])
            self.app.sleep()
        wasp_Watch.display.poweroff()
        wasp_Watch.touch.sleep()
        self.charging = wasp_Watch.battery.charging()
        self.sleepAt = None

    def wake(self):
        if (self.sleepAt <= 0):
            wasp_Watch.display.poweron()
            self.app.wake()
            wasp_Watch.backlight.set(self.brightness)
            wasp_Watch.touch.wake()
        self.keepAwake()

    def print(self,s):
        print(s)

    def run(self,noExcept = None):
        if (noExcept is None):
            noExcept = True
        if self.scheduling:
            print("Watch already running in the background")
            return
        self.secondaryInit()
        print("Watch is running, use Ctrl-C to stop")
        while True:
            if (noExcept != noExcept):
                pass
            try:
                self.tick()
                
            except KeyboardInterrupt:
                raise
                
            except MemoryError:
                raise
                
            except Exception as e:
                raise

    def tick(self):
        update = wasp_Watch.rtc.update()
        if (self.sleepAt > 0):
            if (update and ((self.tickExpiry > 0))):
                now = wasp_Watch.rtc.get_uptime_ms()
                if (self.tickExpiry <= now):
                    ticks = (0 if ((self.tickPeriodMs == 0)) else -(-((now - self.tickExpiry)) // self.tickPeriodMs))
                    self.app.tick(ticks)
            state = self.button.get_event()
            if (state is not None):
                self.handleButton(state)
            event = wasp_Watch.touch.get_event()
            if (event is not None):
                self.handleTouch(event)
            if ((self.sleepAt > 0) and ((wasp_Watch.rtc.uptime > self.sleepAt))):
                self.sleep()
            gc.collect()
        elif (self.button.get_event() or ((self.charging != wasp_Watch.battery.charging()))):
            self.wake()

    def work(self):
        self.scheduled = False
        if (self.scheduled != self.scheduled):
            pass
        try:
            self.tick()
            
        except MemoryError:
            raise
            
        except Exception as e:
            raise

    def schedule(self,enable = None):
        if (enable is None):
            enable = True
        self.secondaryInit()
        if enable:
            wasp_Watch.schedule = self._schedule
        else:
            wasp_Watch.schedule = wasp_Watch.nop
        self.scheduling = enable

    def _schedule(self):
        if (not self.scheduled):
            self.scheduled = True
            micropython.schedule(self.work,self)

    def handleButton(self,state):
        print("handle button")
        self.keepAwake()
        if (((self.eventMask & 8)) > 0):
            if (not self.app.press(255,state)):
                return
        if state:
            self.navigate(255)

    def handleTouch(self,event):
        print("handle touch")
        self.keepAwake()
        if (event[0] == 253):
            if ((((self.eventMask & 16)) > 0) and (not self.app.swipe(event))):
                event[0] = 0
            else:
                event[0] = 4
        if (event[0] < 5):
            updown = ((event[0] == 1) or ((event[0] == 2)))
            if (((((self.eventMask & 4)) > 0) and updown) or (((((self.eventMask & 2)) > 0) and (not updown)))):
                if self.app.swipe(event):
                    self.navigate(event[0])
            else:
                self.navigate(event[0])
        elif ((event[0] == 5) and ((((self.eventMask & 1)) > 0))):
            self.app.touch(event)
        wasp_Watch.touch.reset_touch_data()

    def switchApp(self,app):
        if (self.app is not None):
            try:
                app.background()
            except BaseException as _g:
                pass
        self.eventMask = 0
        self.tickPeriodMs = 0
        self.tickExpiry = None
        self.app = app
        wasp_Watch.display.mute(True)
        wasp_Watch.drawable.reset()
        app.foreground()
        wasp_Watch.display.mute(False)

    def navigate(self,direction):
        pass

    def set_brightness(self,b):
        self.brightness = b
        wasp_Watch.backlight.set(b)
        return b

    def set_notifyLevel(self,level):
        self.notifyLevel = level
        self.nfylev_ms = self.nfyLevels[(level - 1)]
        return level

    def appSort(self,app):
        return app.NAME



class wasp_Notification:

    pass


class wasp__Theme_Theme_Impl_:
    ble = None
    scrollIndicator = None
    battery = None
    statusClock = None
    notifyIcon = None
    bright = None
    mid = None
    ui = None
    spot1 = None
    spot2 = None
    contrast = None

    @staticmethod
    def get_ble(this1):
        return wasp__Theme_Theme_Impl_.get(this1,0)

    @staticmethod
    def get_scrollIndicator(this1):
        return wasp__Theme_Theme_Impl_.get(this1,1)

    @staticmethod
    def get_battery(this1):
        return wasp__Theme_Theme_Impl_.get(this1,2)

    @staticmethod
    def get_statusClock(this1):
        return wasp__Theme_Theme_Impl_.get(this1,3)

    @staticmethod
    def get_notifyIcon(this1):
        return wasp__Theme_Theme_Impl_.get(this1,4)

    @staticmethod
    def get_bright(this1):
        return wasp__Theme_Theme_Impl_.get(this1,5)

    @staticmethod
    def get_mid(this1):
        return wasp__Theme_Theme_Impl_.get(this1,6)

    @staticmethod
    def get_ui(this1):
        return wasp__Theme_Theme_Impl_.get(this1,7)

    @staticmethod
    def get_spot1(this1):
        return wasp__Theme_Theme_Impl_.get(this1,8)

    @staticmethod
    def get_spot2(this1):
        return wasp__Theme_Theme_Impl_.get(this1,9)

    @staticmethod
    def get_contrast(this1):
        return wasp__Theme_Theme_Impl_.get(this1,10)

    @staticmethod
    def get(this1,index):
        return ((this1[(index * 2)] << 8) | this1[((index * 2) + 1)])


class Wasp:
    system = None

    @staticmethod
    def init():
        if (Wasp.system is None):
            Wasp.system = wasp_Manager()
            Wasp.system.init()

    @staticmethod
    def start():
        Wasp.init()
        Wasp.system.schedule()


class LauncherApp(wasp_app_BaseApplication):

    def __init__(self):
        self.numPages = None
        self.NAME = "Launcher"
        self.ICON = LauncherApp.icon
        self.scroll = wasp_widgets_ScrollIndicator(None,6)
        self.page = 0

    def get_numPages(self):
        return ((len(Wasp.system.launcherRing) + 8) // 9)

    def foreground(self):
        self.page = 0
        self.draw()
        Wasp.system.requestEvent(5)

    def background(self):
        pass

    def swipe(self,event):
        i = self.page
        n = self.get_numPages()
        if (event[0] == 2):
            i = (i + 1)
            if (i >= n):
                wasp_Watch.vibrator.pulse()
                return False
        else:
            i = (i - 1)
            if (i < 0):
                Wasp.system.switchApp(Wasp.system.quickRing[0])
                return False
        self.page = i
        self.draw()
        return False

    def touch(self,event):
        app = self.getPage(self.page)[((3 * (event[2] // 74)) + (event[1] // 74))]
        if (app is not None):
            Wasp.system.switchApp(app)
        else:
            wasp_Watch.vibrator.pulse()

    def getPage(self,i):
        ret = Wasp.system.launcherRing[(9 * i):(9 * ((i + 1)))]
        while (len(ret) < 9):
            ret.append(None)
        return ret

    def draw(self):
        pageNum = self.page
        page = self.getPage(pageNum)
        wasp_Watch.drawable.fill()
        self.drawApp(page[0],0,0)
        self.drawApp(page[1],74,0)
        self.drawApp(page[2],148,0)
        self.drawApp(page[3],0,74)
        self.drawApp(page[4],74,74)
        self.drawApp(page[5],148,74)
        self.drawApp(page[6],0,148)
        self.drawApp(page[7],74,148)
        self.drawApp(page[8],148,148)
        self.scroll.up = (pageNum > 0)
        tmp = (self.get_numPages() - 1)
        self.scroll.down = (pageNum < tmp)
        self.scroll.draw()

    def drawApp(self,app,x,y):
        if (app is None):
            return
        wasp_Watch.drawable.blit((wasp_icon__AppIcon_AppIcon_Fields_.AppIcon if ((app.ICON is None)) else app.ICON),(x + 14),(y + 14),wasp__Theme_Theme_Impl_.get(Wasp.system.theme,5),wasp__Theme_Theme_Impl_.get(Wasp.system.theme,6),wasp__Theme_Theme_Impl_.get(Wasp.system.theme,7),True)



class wasp_icon__AppIcon_AppIcon_Fields_:
    pass


class Icons:
    pass


class wasp_icon__BleStatusIcon_BleStatusIcon_Fields_:
    pass


class wasp_icon__CheckboxIcon_CheckboxIcon_Fields_:
    pass


class wasp_icon__DownArrow_DownArrow_Fields_:
    pass


class wasp_icon__Knob_Knob_Fields_:
    pass


class wasp_icon__NotificationIcon_NotificationIcon_Fields_:
    pass


class wasp_icon__UpArrow_UpArrow_Fields_:
    pass


class wasp_widgets_IWidget:
    pass


class wasp_widgets_BatteryMeter:

    def __init__(self):
        self.level = -2
        self.update()

    def draw(self):
        self.level = -2
        self.update()

    def update(self):
        draw = wasp_Watch.drawable
        if wasp_Watch.battery.charging():
            if (self.level != -1):
                draw.blit(Icons.BatteryIcon,(239 - Icons.BatteryIcon[1]),0,wasp__Theme_Theme_Impl_.get(Wasp.system.theme,2))
                self.level = -1
        else:
            level = wasp_Watch.battery.level()
            if (level == self.level):
                return
            green = (level // 3)
            if (green > 31):
                green = 31
            rgb = ((((31 - green) << 11)) + ((green << 6)))
            if ((self.level < 0) or (((level > 5) != ((self.level > 5))))):
                if (level > 5):
                    draw.blit(Icons.BatteryIcon,(239 - Icons.BatteryIcon[1]),0,wasp__Theme_Theme_Impl_.get(Wasp.system.theme,2))
                else:
                    rgb = 63488
                    draw.blit(Icons.BatteryIcon,(239 - Icons.BatteryIcon[1]),0,63488)
            w = (Icons.BatteryIcon[1] - 10)
            x = (234 - w)
            h = ((2 * level) // 11)
            if (h > 18):
                draw.fill(0,x,9,w,(18 - h))
            else:
                draw.fill(rgb,x,(27 - h),w,h)
            self.level = level



class wasp_widgets_Button:

    def __init__(self,x,y,w,h,label):
        self.data = (x, y, w, h, label)

    def draw(self):
        self.update(wasp_Watch.drawable.darken(wasp__Theme_Theme_Impl_.get(Wasp.system.theme,7)),wasp__Theme_Theme_Impl_.get(Wasp.system.theme,6),wasp__Theme_Theme_Impl_.get(Wasp.system.theme,5))

    def touch(self,event):
        x1 = (self.data[0] - 10)
        y1 = (self.data[1] - 10)
        if (((self.data[0] >= x1) and ((self.data[0] < (((x1 + self.data[2]) + 20))))) and ((self.data[1] >= y1))):
            return (self.data[1] < (((y1 + self.data[3]) + 20)))
        else:
            return False

    def update(self,bg,frame,txt):
        draw = wasp_Watch.drawable
        draw.fill(bg,self.data[0],self.data[1],self.data[2],self.data[3])
        draw.set_color(txt,bg)
        draw.set_font(fonts.sans24)
        draw.string(self.data[4],self.data[0],((self.data[1] + (self.data[3] // 2)) - 12),self.data[2])
        draw.fill(frame,self.data[0],self.data[1],self.data[2],2)
        draw.fill(frame,self.data[0],((self.data[1] + self.data[3]) - 2),self.data[2],2)
        draw.fill(frame,self.data[0],self.data[1],2,self.data[3])
        draw.fill(frame,((self.data[0] + self.data[2]) - 2),self.data[1],2,self.data[3])



class wasp_widgets_Checkbox:

    def __init__(self,x,y,label):
        self.data = (x, y, label)
        self.state = False

    def draw(self):
        if (self.data[2] is not None):
            draw = wasp_Watch.drawable
            draw.set_color(wasp__Theme_Theme_Impl_.get(Wasp.system.theme,5))
            draw.set_font(fonts.sans24)
            draw.string(self.data[2],self.data[0],(self.data[1] + 6))
        self.update()

    def touch(self,event):
        if (((((self.data[2] is not None) or (((self.data[0] <= event[1]) and ((event[1] < ((self.data[0] + 40)))))))) and ((self.data[1] <= event[2]))) and ((event[2] < ((self.data[1] + 40))))):
            self.state = (not self.state)
            self.update()
            return True
        return False

    def update(self):
        draw = wasp_Watch.drawable
        c1 = 0
        c2 = 0
        fg = wasp__Theme_Theme_Impl_.get(Wasp.system.theme,6)
        if self.state:
            c1 = wasp__Theme_Theme_Impl_.get(Wasp.system.theme,7)
            c2 = draw.lighten(c1,wasp__Theme_Theme_Impl_.get(Wasp.system.theme,10))
            fg = c2
        draw.blit(wasp_icon__CheckboxIcon_CheckboxIcon_Fields_.CheckboxIcon,(203 if ((self.data[2] is not None)) else self.data[0]),self.data[1],fg,c1,c2)



class wasp_widgets_Clock:

    def __init__(self,enabled = None):
        if (enabled is None):
            enabled = True
        self.enabled = enabled
        self.displayedTime = None

    def draw(self):
        self.displayedTime = None
        self.update()

    def update(self):
        now = wasp_Watch.rtc.get_localtime()
        if (((self.displayedTime is not None) and ((self.displayedTime[0] == now[3]))) and ((self.displayedTime[1] == now[4]))):
            return None
        if (self.enabled and ((((self.displayedTime is None) or ((self.displayedTime[0] != now[3]))) or ((self.displayedTime[1] != now[4]))))):
            this1 = [now[3], now[4]]
            t = "{:02}:{02}".format(*this1)
            wasp_Watch.drawable.set_font(fonts.sans28)
            wasp_Watch.drawable.set_color(wasp__Theme_Theme_Impl_.get(Wasp.system.theme,3))
            wasp_Watch.drawable.string(t,52,4,138)
        self.displayedTime = (now[3], now[4])
        return now



class wasp_widgets_ConfirmationView:

    def __init__(self):
        self.active = False
        self.value = False
        self.yesButton = wasp_widgets_Button(20,140,90,45,"Yes")
        self.noButton = wasp_widgets_Button(130,140,90,45,"No")

    def draw(self,message):
        draw = wasp_Watch.drawable
        wasp_Watch.display.mute(True)
        draw.set_color(wasp__Theme_Theme_Impl_.get(Wasp.system.theme,5))
        draw.set_font(fonts.sans24)
        draw.fill()
        draw.string(message,0,60)
        self.yesButton.draw()
        self.noButton.draw()
        wasp_Watch.display.mute(False)
        self.active = True

    def touch(self,event):
        if (not self.active):
            return False
        if self.yesButton.touch(event):
            self.active = False
            self.value = True
            return True
        if self.noButton.touch(event):
            self.active = False
            self.value = False
            return True
        return False



class wasp_widgets_GfxButton:

    def __init__(self,x,y,gfx):
        self.pos = (x, y)
        self.gfx = gfx

    def draw(self):
        wasp_Watch.drawable.blit(self.gfx,self.pos[0],self.pos[1])

    def touch(self,event):
        x1 = (self.pos[0] - 10)
        y1 = (self.pos[1] - 10)
        if (((event[1] >= x1) and ((event[1] < (((x1 + self.gfx[1]) + 20))))) and ((event[2] >= y1))):
            return (event[2] < (((y1 + self.gfx[2]) + 20)))
        else:
            return False



class wasp_widgets_NotificationBar:

    def __init__(self,x = None,y = None):
        if (x is None):
            x = 0
        if (y is None):
            y = 0
        self.pos = (x, y)

    def draw(self):
        self.update()

    def update(self):
        draw = wasp_Watch.drawable
        if wasp_Watch.connected():
            draw.blit(wasp_icon__BleStatusIcon_BleStatusIcon_Fields_.BleStatusIcon,self.pos[0],self.pos[1],wasp__Theme_Theme_Impl_.get(Wasp.system.theme,0))
            if (len(Wasp.system.notifications) > 0):
                draw.blit(wasp_icon__NotificationIcon_NotificationIcon_Fields_.NotificationIcon,(self.pos[0] + 22),self.pos[1],wasp__Theme_Theme_Impl_.get(Wasp.system.theme,4))
            else:
                draw.fill(0,(self.pos[0] + 22),self.pos[1],30,32)
        elif (len(Wasp.system.notifications) > 0):
            draw.blit(wasp_icon__NotificationIcon_NotificationIcon_Fields_.NotificationIcon,self.pos[0],self.pos[1],wasp__Theme_Theme_Impl_.get(Wasp.system.theme,4))
            draw.fill(0,(self.pos[0] + 30),self.pos[1],22,32)
        else:
            draw.fill(0,self.pos[0],self.pos[1],52,32)



class wasp_widgets_PinHandler:

    def __init__(self,pin):
        self.pin = pin
        self.value = pin.value()

    def get_event(self):
        newValue = self.pin.value()
        if (self.value == newValue):
            return None
        self.value = newValue
        return newValue



class wasp_widgets_ScrollIndicator:

    def __init__(self,x = None,y = None):
        if (x is None):
            x = 222
        if (y is None):
            y = 216
        self.pos = (x, y)
        self.up = True
        self.down = True

    def draw(self):
        self.update()

    def update(self):
        color = wasp__Theme_Theme_Impl_.get(Wasp.system.theme,1)
        if self.up:
            wasp_Watch.drawable.blit(wasp_icon__UpArrow_UpArrow_Fields_.UpArrow,self.pos[0],self.pos[1],color)
        if self.down:
            wasp_Watch.drawable.blit(wasp_icon__DownArrow_DownArrow_Fields_.DownArrow,self.pos[0],(self.pos[1] + 13),color)



class wasp_widgets_Slider:

    def __init__(self,steps,x = None,y = None,color = None):
        if (x is None):
            x = 10
        if (y is None):
            y = 90
        self.value = 0
        self.steps = steps
        self.stepSize = (180 / ((steps - 1)))
        self.x = x
        self.y = y
        self.color = color
        self.lowLight = None

    def draw(self):
        draw = wasp_Watch.drawable
        if (self.color is None):
            self.color = wasp__Theme_Theme_Impl_.get(Wasp.system.theme,7)
        if (self.lowLight is None):
            self.lowLight = draw.lighten(self.color,wasp__Theme_Theme_Impl_.get(Wasp.system.theme,10))
        knobX = (self.x + ((180 * self.value) // (self.steps - 1)))
        draw.blit(wasp_icon__Knob_Knob_Fields_.Knob,knobX,self.y,self.color)
        w = (knobX - self.x)
        if (w > 0):
            draw.fill(0,self.x,self.y,w,16)
            if (w > 20):
                draw.fill(0,self.x,(self.y + 16),20,8)
                draw.fill(self.color,(self.x + 20),(self.y + 16),(w - 20),8)
            else:
                draw.fill(0,self.x,(self.y + 16),w,8)
            draw.fill(0,self.x,(self.y + 24),w,16)
        sx = (knobX + 40)
        w = (180 - w)
        if (w > 0):
            draw.fill(0,sx,self.y,w,16)
            if (w > 20):
                draw.fill(0,((sx + w) - 20),(self.y + 16),20,8)
                draw.fill(self.lowLight,sx,(self.y + 16),(w - 20),8)
            else:
                draw.fill(0,sx,(self.y + 16),w,8)
            draw.fill(0,sx,(self.y + 24),w,16)

    def update(self):
        self.draw()

    def touch(self,event):
        v = ((event[1] - (((self.x + 20) - ((self.stepSize / 2))))) // self.stepSize)
        if (v < 0):
            v = 0
        elif (v >= self.steps):
            v = (self.steps - 1)
        self.value = v



class wasp_widgets_Spinner:

    def __init__(self,x,y,mn,mx,field = None):
        if (field is None):
            field = 1
        self.data = (x, y, mn, mx, field)
        self.value = mn

    def draw(self):
        draw = wasp_Watch.drawable
        fg = draw.lighten(wasp__Theme_Theme_Impl_.get(Wasp.system.theme,7),wasp__Theme_Theme_Impl_.get(Wasp.system.theme,10))
        draw.blit(wasp_icon__UpArrow_UpArrow_Fields_.UpArrow,((self.data[0] + 30) - 8),(self.data[1] + 20),fg)
        draw.blit(wasp_icon__DownArrow_DownArrow_Fields_.DownArrow,((self.data[0] + 30) - 8),(((self.data[1] + 120) - 20) - 9),fg)
        self.update()

    def update(self):
        draw = wasp_Watch.drawable
        draw.set_color(wasp__Theme_Theme_Impl_.get(Wasp.system.theme,5))
        draw.set_font(fonts.sans28)
        s = ("" + str(self.value))
        while (len(s) < self.data[4]):
            s = ("0" + ("null" if s is None else s))
        draw.string(s,self.data[0],((self.data[1] + 60) - 14),60)

    def touch(self,event):
        if ((((event[1] >= self.data[0]) and ((event[1] < ((self.data[0] + 60))))) and ((event[2] >= self.data[1]))) and ((event[2] < ((self.data[1] + 120))))):
            if (event[2] < ((self.data[1] + 60))):
                _hx_local_0 = self
                _hx_local_1 = _hx_local_0.value
                _hx_local_0.value = (_hx_local_1 + 1)
                _hx_local_1
                if (self.value > self.data[3]):
                    self.value = self.data[2]
            else:
                _hx_local_2 = self
                _hx_local_3 = _hx_local_2.value
                _hx_local_2.value = (_hx_local_3 - 1)
                _hx_local_3
                if (self.value < self.data[2]):
                    self.value = self.data[3]
            self.update()
            return True
        return False



class wasp_widgets_StatusBar:

    def __init__(self):
        self.clock = wasp_widgets_Clock()
        self.meter = wasp_widgets_BatteryMeter()
        self.notif = wasp_widgets_NotificationBar()

    def get_displayClock(self):
        return self.clock.enabled

    def set_displayClock(self,v):
        def _hx_local_1():
            def _hx_local_0():
                self.clock.enabled = v
                return self.clock.enabled
            return _hx_local_0()
        return _hx_local_1()

    def draw(self):
        self.clock.draw()
        self.meter.draw()
        self.notif.draw()

    def update(self):
        now = self.clock.update()
        if (now is not None):
            self.meter.update()
            self.notif.update()
        return now



class wasp_widgets_StopWatch:

    def __init__(self,y):
        self.started = None
        self.lastCount = None
        self.count = None
        self.startedAt = None
        self.y = y
        self.reset()

    def get_started(self):
        return (self.startedAt > 0)

    def start(self):
        self.startedAt = ((wasp_Watch.rtc.get_uptime_ms() // 10) - self.count)

    def stop(self):
        self.startedAt = 0

    def reset(self):
        self.count = 0
        self.startedAt = 0
        self.lastCount = -1

    def draw(self):
        self.lastCount = -1
        self.update()

    def update(self):
        if (self.startedAt > 0):
            self.count = ((wasp_Watch.rtc.get_uptime_ms() // 10) - self.startedAt)
            if (self.count > 5994000):
                self.reset()
        if (self.lastCount != self.count):
            centisecs = self.count
            secs = (centisecs // 100)
            centisecs = HxOverrides.mod(centisecs, 100)
            minutes = (secs // 60)
            secs = HxOverrides.mod(secs, 60)
            t1 = "{}:{:02}".format(*[minutes, secs])
            t2 = "{:02}".format(*[centisecs])
            draw = wasp_Watch.drawable
            draw.set_font(fonts.sans36)
            draw.set_color(draw.lighten(wasp__Theme_Theme_Impl_.get(Wasp.system.theme,7),wasp__Theme_Theme_Impl_.get(Wasp.system.theme,10)))
            w = fonts.width(fonts.sans36,t1)
            draw.string(t1,(180 - w),self.y)
            draw.fill(0,0,self.y,(180 - w),36)
            draw.set_font(fonts.sans24)
            draw.string(t2,180,(self.y + 18),46)
            self.lastCount = self.count



class wasp_widgets_ToggleButton(wasp_widgets_Button):

    def __init__(self,x,y,w,h,label):
        self.state = None
        super().__init__(x,y,w,h,label)
        self.state = False

    def draw(self):
        self.update(wasp_Watch.drawable.darken((wasp__Theme_Theme_Impl_.get(Wasp.system.theme,7) if (self.state) else wasp__Theme_Theme_Impl_.get(Wasp.system.theme,6))),wasp__Theme_Theme_Impl_.get(Wasp.system.theme,6),wasp__Theme_Theme_Impl_.get(Wasp.system.theme,5))

    def touch(self,event):
        ret = super().touch(event)
        if ret:
            self.state = (not self.state)
            self.draw()
        return ret



TorchApp.icon = (
        b'\x02'
        b'`@'
        b'?\xff\xff\xff\xff\xff\xff\xff&\xc6\x0c@\xd4B?\n'
        b'\xca\tD?\x08\xc4\x06\xc2\x07F?\x07\xc3\x07\xc2\x06'
        b'H?\x06\xc2\n\xc1\x04G\xc2A8\xc5\x08\xc2\t\xc2'
        b'\x02F\xc3C7\xc7\x06\xc2\x0b\xc1F\xc2F\x1e\xe8\n'
        b'\xc2C\xc3H\x1d\xe8\x0c\xc1N\x1d\xc2%\xc1\x0b\xc2N'
        b'\x1d\xc2%\xc1\x0c\xc1N\x1d\xc2\x04\x9d\x04\xc1\x0b\xc2N'
        b'\x1d\xc2\x06\x81\x03\x81\x03\x81\x03\x81\x03\x81\x03\x81\x03\x81'
        b'\x06\xc1\x0c\xc1N\x1d\xc2\x04\x9d\x04\xc1\x0b\xc2C\xcaA'
        b'\x1d\xc2\x06\x81\x03\x81\x03\x81\x03\x81\x03\x81\x03\x81\x03\x81'
        b'\x06\xc1\x0c\xc1N\x1d\xc2\x04\x9d\x04\xc1\x0b\xc2N\x1d\xc2'
        b'%\xc1\x0c\xc1N\x1d\xc2%\xc1\x0b\xc2N\x1d\xe8\x0c\xc1'
        b'N\x1e\xe8\n\xc2C\xc3H?\x05\xc2\x0b\xc1F\xc2F'
        b'?\x06\xc2\t\xc2\x02F\xc3C?\x06\xc2\n\xc1\x04G'
        b'\xc2A?\x07\xc3\x07\xc2\x06H?\x08\xc4\x06\xc2\x07F'
        b'?\n\xca\tD?\r\xc6\x0cB?\xff\xff\xff\xff\xff'
        b'\xff\x95'
    )
LauncherApp.icon = (
        b'\x02'
        b'@@'
        b'?\xff\x88@\xc1t\x0cA2A\x0cA2A\x0cA'
        b'2A\x0cA2A\x0cA2A\x0cA2A\x0cA'
        b'2A\x0cA2A\x0cA2A\x0cA2A\x0cA'
        b'2A\x0cA2A\x0cA2A\x0cA\x03\x80\xc6\xac'
        b'\x03A\x0cA2A\x0cA2A\x0cA2A\x0cA'
        b'2A\x0cA\x04\xc9\x03\xc5\x04\xc6\x07\xc5\x07A\x0cA'
        b'\x04\xc9\x02\xc7\x03\xc8\x04\xc7\x06A\x0cA\x07\xc3\x05\xc3'
        b'\x01\xc3\x03\xc3\x02\xc3\x04\xc3\x01\xc3\x06A\x0cA\x07\xc3'
        b'\x04\xc3\x03\xc3\x02\xc3\x03\xc3\x02\xc3\x03\xc3\x05A\x0cA'
        b'\x07\xc3\x04\xc3\x03\xc3\x02\xc3\x03\xc3\x02\xc3\x03\xc3\x05A'
        b'\x0cA\x07\xc3\x04\xc3\x03\xc3\x02\xc3\x03\xc3\x02\xc3\x03\xc3'
        b'\x05A\x0cA\x07\xc3\x04\xc3\x03\xc3\x02\xc3\x03\xc3\x02\xc3'
        b'\x03\xc3\x05A\x0cA\x07\xc3\x04\xc3\x03\xc3\x02\xc3\x03\xc3'
        b'\x02\xc3\x03\xc3\x05A\x0cA\x07\xc3\x04\xc3\x03\xc3\x02\xc3'
        b'\x03\xc3\x02\xc3\x03\xc3\x05A\x0cA\x07\xc3\x04\xc3\x03\xc3'
        b'\x02\xc3\x03\xc3\x02\xc3\x03\xc3\x05A\x0cA\x07\xc3\x05\xc3'
        b'\x01\xc3\x03\xc3\x02\xc3\x04\xc3\x01\xc3\x06A\x0cA\x07\xc3'
        b'\x05\xc7\x03\xc8\x04\xc7\x06A\x0cA\x07\xc3\x06\xc5\x04\xc6'
        b'\x07\xc5\x07A\x0cA2A\x0cA2A\x0cA2A'
        b'\x0cA2A\x0cA\x03\xac\x03A\x0cA2A\x0cA'
        b'2A\x0cA2A\x0cA2A\x0cA2A\x0cA'
        b'2A\x0cA2A\x0cA2A\x0cA2A\x0cA'
        b'2A\x0cA2A\x0cA2A\x0cA2A\x0cA'
        b'2A\x0ct?\xff\x08'
    )
wasp_icon__AppIcon_AppIcon_Fields_.AppIcon = (
        b'\x02'
        b'@@'
        b'?\xff\x88@\xc1t\x0cA2A\x0cA2A\x0cA'
        b'2A\x0cA2A\x0cA2A\x0cA2A\x0cA'
        b'2A\x0cA2A\x0cA2A\x0cA2A\x0cA'
        b'2A\x0cA2A\x0cA2A\x0cA\x03\x80\xc6\xac'
        b'\x03A\x0cA2A\x0cA2A\x0cA2A\x0cA'
        b'2A\x0cA\x04\xc9\x03\xc5\x04\xc6\x07\xc5\x07A\x0cA'
        b'\x04\xc9\x02\xc7\x03\xc8\x04\xc7\x06A\x0cA\x07\xc3\x05\xc3'
        b'\x01\xc3\x03\xc3\x02\xc3\x04\xc3\x01\xc3\x06A\x0cA\x07\xc3'
        b'\x04\xc3\x03\xc3\x02\xc3\x03\xc3\x02\xc3\x03\xc3\x05A\x0cA'
        b'\x07\xc3\x04\xc3\x03\xc3\x02\xc3\x03\xc3\x02\xc3\x03\xc3\x05A'
        b'\x0cA\x07\xc3\x04\xc3\x03\xc3\x02\xc3\x03\xc3\x02\xc3\x03\xc3'
        b'\x05A\x0cA\x07\xc3\x04\xc3\x03\xc3\x02\xc3\x03\xc3\x02\xc3'
        b'\x03\xc3\x05A\x0cA\x07\xc3\x04\xc3\x03\xc3\x02\xc3\x03\xc3'
        b'\x02\xc3\x03\xc3\x05A\x0cA\x07\xc3\x04\xc3\x03\xc3\x02\xc3'
        b'\x03\xc3\x02\xc3\x03\xc3\x05A\x0cA\x07\xc3\x04\xc3\x03\xc3'
        b'\x02\xc3\x03\xc3\x02\xc3\x03\xc3\x05A\x0cA\x07\xc3\x05\xc3'
        b'\x01\xc3\x03\xc3\x02\xc3\x04\xc3\x01\xc3\x06A\x0cA\x07\xc3'
        b'\x05\xc7\x03\xc8\x04\xc7\x06A\x0cA\x07\xc3\x06\xc5\x04\xc6'
        b'\x07\xc5\x07A\x0cA2A\x0cA2A\x0cA2A'
        b'\x0cA2A\x0cA\x03\xac\x03A\x0cA2A\x0cA'
        b'2A\x0cA2A\x0cA2A\x0cA2A\x0cA'
        b'2A\x0cA2A\x0cA2A\x0cA2A\x0cA'
        b'2A\x0cA2A\x0cA2A\x0cA2A\x0cA'
        b'2A\x0ct?\xff\x08'
    )
Icons.BatteryIcon = (
        b'\x02'
        b'\x18 '
        b'\x04\x01\x02\xca\x0c\xce\n\xce\t\xd0\x04\xc8\x08\xd0\x08\xd0'
        b'\x08\xd0\x08\xcc\x04\x08\x04\xc8\x10\xc8\t\xc3\x04\xc8\x08\xc4'
        b'\x04\xc8\x07\xc5\x04\xc8\x06\xc5\x05\xc8\x05\xc5\x06\xc8\x04\xc5'
        b'\x01@\xfcA\x05\xc8\x03\xcb\x02\xc8\x02\xcc\x02\xc8\x02\xcc'
        b'\x02\xc8\x02\xcb\x03\xc8\x05\x01\x01\xc5\x04\xc8\x06\xc5\x05\xc8'
        b'\x05\xc5\x06\xc8\x04\xc5\x07\xc8\x04\xc4\x08\xc8\x04\xc3\t\xc8'
        b'\x10\xc8P\xff%'
    )
wasp_icon__BleStatusIcon_BleStatusIcon_Fields_.BleStatusIcon = (
        b'\x02'
        b'\x16 '
        b'\x07\xc1\x15\xc2\x14\xc3\x13\xc4\x12\xc5\x11\xc6\x10\xc7\x0f\xc3'
        b'\x01\xc4\x08\xc2\x04\xc3\x02\xc4\x06\xc4\x03\xc3\x03\xc4\x06\xc4'
        b'\x02\xc3\x02\xc4\x08\xc4\x01\xc3\x01\xc4\n\xcb\x0c\xc9\x0e\xc7'
        b'\x10\xc5\x11\xc5\x10\xc7\x0e\xc9\x0c\xcb\n\xc4\x01\xc3\x01\xc4'
        b'\x08\xc4\x02\xc3\x02\xc4\x06\xc4\x03\xc3\x03\xc4\x06\xc2\x04\xc3'
        b'\x02\xc4\r\xc3\x01\xc4\x0e\xc7\x0f\xc6\x10\xc5\x11\xc4\x12\xc3'
        b'\x13\xc2\x14\xc1\x0e'
    )
wasp_icon__CheckboxIcon_CheckboxIcon_Fields_.CheckboxIcon = (
        b'\x02'
        b'  '
        b'\x02\xdc\x03\xde\x01\xe4X\xc7Z\xc6Z\xc6Z\xc6T\x82'
        b'D\xc6S\x84C\xc6R\x86B\xc6Q\x86C\xc6P\x86'
        b'D\xc6O\x86E\xc6N\x86F\xc6M\x86G\xc6L\x86'
        b'H\xc6D\x82E\x86I\xc6C\x84C\x86J\xc6B\x86'
        b'A\x86K\xc6C\x8bL\xc6D\x89M\xc6E\x87N\xc6'
        b'F\x85O\xc6G\x83P\xc6H\x81Q\xc6Z\xc6Z\xc6'
        b'Z\xc7X\xe4\x01\xde\x03\xdc\x02'
    )
wasp_icon__DownArrow_DownArrow_Fields_.DownArrow = (
        b'\x02'
        b'\x10\t'
        b'\xe0\x01\xce\x03\xcc\x05\xca\x07\xc8\t\xc6\x0b\xc4\r\xc2\x07'
    )
wasp_icon__Knob_Knob_Fields_.Knob = (
        b'\x02'
        b'(('
        b'\x10\xc8\x1c\xd0\x16\xd4\x13\xd6\x10\xda\r\xdc\x0b\xde\t\xe0'
        b'\x08\xe0\x07\xe2\x05\xe4\x04\xe4\x03\xe6\x02\xe6\x02\xe6\x02\xe6'
        b'\x01\xff\xff\x02\x01\xe6\x02\xe6\x02\xe6\x02\xe6\x03\xe4\x04\xe4'
        b'\x05\xe2\x07\xe0\x08\xe0\t\xde\x0b\xdc\r\xda\x10\xd6\x13\xd4'
        b'\x16\xd0\x1c\xc8\x10'
    )
wasp_icon__NotificationIcon_NotificationIcon_Fields_.NotificationIcon = (
        b'\x02'
        b'\x1e '
        b'\x0e\xc2\x1b\xc4\x1a\xc4\x18\xc8\x14\xcc\x11\xce\x0f\xd0\x0e\xc5'
        b'\x06\xc5\r\xc4\n\xc4\x0c\xc4\n\xc4\x0b\xc4\x0c\xc4\n\xc4'
        b'\x0c\xc4\n\xc4\x0c\xc4\n\xc3\r\xc4\t\xc4\x0e\xc3\t\xc4'
        b'\x0e\xc4\x08\xc4\x0e\xc4\x08\xc4\x0e\xc4\x08\xc4\x0e\xc4\x08\xc3'
        b'\x0f\xc4\x07\xc4\x10\xc4\x06\xc4\x10\xc4\x06\xc4\x10\xc4\x05\xc5'
        b'\x10\xc4\x05\xc4\x12\xc4\x03\xc5\x12\xc5\x02\xdc\x01\xfc\x01\xdc'
        b'\x0e\xc4\x1b\xc2\x0e'
    )
wasp_icon__UpArrow_UpArrow_Fields_.UpArrow = (
        b'\x02'
        b'\x10\t'
        b'\x07\xc2\r\xc4\x0b\xc6\t\xc8\x07\xca\x05\xcc\x03\xce\x01\xe0'
    )
wasp_widgets_Slider.KNOB_DIAMETER = 40
wasp_widgets_Slider.KNOB_RADIUS = 20
wasp_widgets_Slider.WIDTH = 220
wasp_widgets_Slider.TRACK = 180
wasp_widgets_Slider.TRACK_HEIGHT = 8
wasp_widgets_Slider.TRACK_Y1 = 16
wasp_widgets_Slider.TRACK_Y2 = 24