# -*- coding: utf-8 -*-
#   Author:Meng Zhuo <mengzhuo1203@gmail.com>
#   version 0.1.4
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
#  FURTRUE
#  1.maybe add i18n in next version

import rb,dbus,commands,gconf,gtk,gettext
from dbus.mainloop.glib import DBusGMainLoop
from gtk import icon_theme_get_default
from gtk.gdk import pixbuf_new_from_file as pnff


#DEBUG
#import traceback
i18n_mo_name = 'rhythmbox-plugin-earphone'
gettext.textdomain(i18n_mo_name)
_ = gettext.gettext


class EarPhone (rb.Plugin):
    #rb_plugin_is_configurable()
    def __init__(self):
        rb.Plugin.__init__(self)

        
    def activate(self, shell):
        print "Earphone Event Plugin activated."
        self.shell = shell
        self.gconf_keys = {
        'showNotification' : '/apps/rhythmbox/plugins/EarPhone/showNotification',
        'firstTime' : '/apps/rhythmbox/plugins/EarPhone/firstTime'
        }
        self.gconf = gconf.client_get_default()
        firstTime = self.gconf.get_bool(self.gconf_keys['firstTime'])
        
        #FIXME Can't Find another way to get a non-exist Gconf Boolean key
        if not firstTime:
            self.showNotify = True
            self.gconf.set_bool(self.gconf_keys['showNotification'],self.showNotify)
            self.gconf.set_bool(self.gconf_keys['firstTime'],True)
        else:
            self.showNotify = self.gconf.get_bool(self.gconf_keys['showNotification'])
        
        
        #get icons
        icon = icon_theme_get_default()
        warning_icon = icon.lookup_icon("dialog-warning",48, 0)
        self.warning_icon_url = warning_icon.get_filename()
        self.warning_img_buf = pnff(self.warning_icon_url)
        
        crying_icon = icon.lookup_icon("face-crying",48, 0)
        crying_icon_url = crying_icon.get_filename()
        #crying_icon_img_buf = pnff(crying_icon_url)
        
        #init notify
        session_bus = dbus.SessionBus()
        notify_obj = session_bus.get_object('org.freedesktop.Notifications','/org/freedesktop/Notifications')
        self.notify_interface = dbus.Interface(notify_obj,'org.freedesktop.Notifications')
        
        #check whether HAL is running
        HAL_id = commands.getoutput("pidof hald")
        
        if not HAL_id.isdigit() and self.showNotify:
          No_HAL_title = _('Ow..No HAL daemon')
          No_HAL_content = _('Rhythmbox won`t respond while Earphone status got changed')
          #do No HAL notify
          try:
            print "Got to tell you No Hal exits."
            #FIXME Can't Notify...
            #self.shell.notify_custom(2,No_HAL_title,No_HAL_content,crying_icon_img_buf,False)
            self.notify_interface.Notify('rhythmbox',0,crying_icon_url,No_HAL_title,No_HAL_content,'',{'x-canonical-append':'allowed'},-1)
          except:
            print "Ah...New Version Rhythmbox"
            self.shell.notify_custom(2,No_HAL_title,No_HAL_content,crying_icon_url,False)
            
        dbus_loop = DBusGMainLoop()
        
        self.system_bus = dbus.SystemBus(mainloop=dbus_loop)
        self.system_bus.add_signal_receiver(self.EarPhoneChange, dbus_interface = "org.freedesktop.Hal.Device", signal_name = "Condition")
        
    def deactivate(self, shell):
        print "Earphone Event Plugin Deactivating..."
        try:
            del self.system_bus,self.shell,self.warning_icon_url,self.notify_interface
            print "Earphone Event Plugin Deactivated"
        except:
            print "DEL ERROR"
    
    def create_configure_dialog(self):

         self.builder = gtk.Builder()
         ui_file_url = self.find_file("EarPhone.glade")
         self.builder.add_from_file(ui_file_url)
         self.builder.set_translation_domain(i18n_mo_name)

         self.showNotifyObj = self.builder.get_object('showNotify')
         self.showNotifyObj.set_active(self.showNotify)
         self.showNotifyObj.connect('toggled',self.showNotification_changed)
         
         self.showNotifyDialog = self.builder.get_object("EPDialog")
         self.showNotifyDialog.connect('response',self.notify_response)
         self.showNotifyDialog.present()
         
         return self.showNotifyDialog
         
    def showNotification_changed(self,toggle):
         self.showNotify = self.showNotifyObj.get_active()
         self.gconf.set_bool(self.gconf_keys['showNotification'],self.showNotify)
    
    def notify_response(self,dialog, response):
         dialog.hide()

    def EarPhoneChange(self,cond_name,cond_details):
    
        if not cond_details.find('headphone_insert'):
            self.shell.props.shell_player.playpause(0)
            if self.showNotify:
               ESHBC = _('Earphone status had been changed')
               try:
                  self.shell.notify_custom(2,ESHBC,'',self.warning_img_buf,False)
               except:
                  self.shell.notify_custom(2,ESHBC,'',self.warning_icon_url,False)
