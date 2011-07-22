# -*- coding: utf-8 -*-
#   Author:Meng Zhuo <mengzhuo1203@gmail.com>
#   version 0.1.3
#   Release under WTFPL Version 2.0
'''
DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
   Version 2, December 2004
Copyright (C) 2004 Sam Hocevar <sam@hocevar.net>
Everyone is permitted to copy and distribute verbatim or modified
copies of this license document, and changing it is allowed as long
as the name is changed.

            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE

   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

  0. You just DO WHAT THE FUCK YOU WANT TO.
'''
#FIXME maybe add i18n in next version
import rb,dbus,commands
from dbus.mainloop.glib import DBusGMainLoop
from gtk import icon_theme_get_default
from gtk.gdk import pixbuf_new_from_file as pnff


class EarPhone (rb.Plugin):
    def __init__(self):
        rb.Plugin.__init__(self)
        
    def activate(self, shell):
        print "Earphone Event Plugin activated."
        self.shell = shell
        
        #get icons
        icon = icon_theme_get_default()
        warning_icon = icon.lookup_icon("dialog-warning",48, 0)
        warning_icon_url = warning_icon.get_filename()
        self.warning_img_buf = pnff(warning_icon_url)
        
        crying_icon = icon.lookup_icon("face-crying",48, 0)
        crying_icon_url = crying_icon.get_filename()
        #crying_icon_img_buf = pnff(crying_icon_url)
        
        #init notify
        session_bus = dbus.SessionBus()
        notify_obj = session_bus.get_object('org.freedesktop.Notifications','/org/freedesktop/Notifications')
        self.notify_interface = dbus.Interface(notify_obj,'org.freedesktop.Notifications')
        
        #check whether HAL is running
        HAL_id = commands.getoutput("pidof hald")
        
        #get Rhythmbox PID
        #self.rb_pid = commands.getoutput("pidof rhythmbox")
        
        if not HAL_id.isdigit():
            #do No HAL notify
          try:
            self.notify_interface.Notify('rhythmbox',0,crying_icon_url,'Ow..No HAL daemon',"Rhythmbox won't respond while Earphone status got changed",'',{'x-canonical-append':'allowed'},-1)
          except:
            print "Can't notify the system"
            #self.shell.notify_custom(2,'Ow..No HAL daemon',"Rhythmbox won't respond while Earphone status got changed",crying_icon_img_buf,False)
            
        dbus_loop = DBusGMainLoop()
        
        self.system_bus = dbus.SystemBus(mainloop=dbus_loop)
        self.system_bus.add_signal_receiver(self.EarPhoneChange, dbus_interface = "org.freedesktop.Hal.Device", signal_name = "Condition")
        
    def deactivate(self, shell):
        print "Earphone Event Plugin Deactivating..."
        del self.system_bus,self.shell,self.warning_icon_url,self.notify_interface
        
    def EarPhoneChange(self,cond_name,cond_details):
    
        # it's wired that str.find return a FALSE while it find the string...
        if not cond_details.find('headphone_insert'):
            self.shell.props.shell_player.playpause(0)
            '''
            warning_notify_hints={'urgency':2,
                          'category':'device',
                          'desktop-entry':'rhythmbox',
                          'x-canonical-append':'allowed'
                          }
            self.notify_interface.CloseNotification
            self.notify_interface.Notify('rhythmbox',0,self.warning_icon_url,'Earphone status had been changed','','',warning_notify_hints,-1)
            '''
            try:
               self.shell.notify_custom(2,'Earphone status had been changed','',self.warning_img_buf,False)
            except:
               try:
                  self.shell.notify_custom(2,'Earphone status had been changed','',crying_icon_url,False)
               except:
                  print "Can't not notify"
