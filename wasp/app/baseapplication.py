class BaseApplication:

    def __init__(self):
        self.ID = None
        self.ICON = None
        self.NAME = None

    def foreground(self):
        pass

    def background(self):
        pass

    def registered(self,quickRing):
        pass

    def unregistered(self):
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

