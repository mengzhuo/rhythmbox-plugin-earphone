# -*- coding: utf-8 -*-
import rb,dbus,gobject
from dbus.mainloop.glib import DBusGMainLoop


class EarPhone (rb.Plugin):
    def __init__(self):
        rb.Plugin.__init__(self)
        
    def activate(self, shell):
        print "Earphone Event Plugin activated."
        dbus_loop = DBusGMainLoop()
        self.shell = shell
        self.system_bus = dbus.SystemBus(mainloop=dbus_loop)
        self.system_bus.add_signal_receiver(self.EarphoneChange, dbus_interface = "org.freedesktop.Hal.Device", signal_name = "Condition")
        
    def deactivate(self, shell):
        print "Earphone Event Plugin Deactivating..."
        del self.system_bus,self.shell
        
    def EarPhoneChange(self,cond_name,cond_details):
    
        #FIXME it's wired that str.find return a FALSE
        if not cond_details.find('headphone_insert'):
            self.shell.props.shell_player.playpause()
