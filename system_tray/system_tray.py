'''
System Tray
===========

cross platform system tray tool support 2 and 3
also provides methos for the taskbar

Pretty much a wrapper on other code that has been floating around

callbacks can be handled in two ways.
The first lets the SystemTray run them automatically from the thread.
In cases where this is a problem i.e in Guis where things have to be 
run from the mainthread.

you can pass a callback function in, all callbacks will be passed 
to this function and you can pass them along into the main thread

What would be cool is the ability to have the correct open and
close functions for each platform and each toolkit
tktiner, gtk, qt, wxpython etc

on function call an event gets passed along, in gtk this is the menuitem

'''
from __future__ import print_function
from __future__ import absolute_import

import queue
import _thread as thread
import os
import time
import logging
from functools import partial

if os.name == 'nt':
    import pywintypes
    from . import wintray
    from . import taskbar
else:
    from gi.repository import Gtk as gtk
    from gi.repository import AppIndicator3 as appindicator
    from gi.repository import Gdk, GLib

from timstools import ignored

def raise_error(error):
    '''used to pass errors from a child thread to parent thread'''
    print('raising da error')
    raise error

class FormBuilder:
    # Returns values as one would expects, an interface for easier unpacking and len methods on results
    # Used by custom form and toolbar

    # First of all recognizes the need (or my lack of knowlegde on unpacking)
    # So if it is a single row will use that way to unpack, otherwise another
    # way for multilple row items

    # Encompasses two different build methods

    # The coloum is always returned (so that multiple items in rows can be
    # grided)

    def __init__(self, form):
        self.form = form

    def __iter__(self):
        for h, item in enumerate(self.form):
            if not isinstance(item[0], tuple):        # Single Row
                try:                                    # first way
                    # not sure why its not unpacking item properly.. have to
                    # put it in a list wf
                    for text, icon, command in ([item]):
                        yield(h, 0, text, icon, command)
                except ValueError as err:               # second way
                    for funct, text, dict_name, where, config in ([item]):
                        yield(h, 0, funct, text, dict_name, where, config)
            elif isinstance(item[0], tuple):  # Multi
                for j, *sub_items in enumerate(item):  # going over sub items
                    try:  # first way
                        for text, icon, command in sub_items:
                            yield(h, j, text, icon, command)
                    except ValueError as e:  # second way
                        if not 'too many' in str(e):
                            raise e
                        for funct, text, dict_name, where, config in sub_items:
                            yield(h, j, funct, text, dict_name, where, config)

# TBD see here.. http://stackoverflow.com/questions/11040098/cannot-pass-arguments-from-the-tkinter-widget-after-function#_=_
def named_partial(func, *args, **kwargs):
        # attribute error because there is no
        # __name__ method found when using functools.partial,this resolves that
        name = func.__name__
        function = partial(func, *args, **kwargs)
        function.__name__ = name
        return function
class SystemTray():
    '''
    hi
    '''
    def __init__(self,
                 icon_file=None,
                 tooltip=None,
                 menu_options=None,
                 windows_lib='win32',
                 linux_lib='gtk',
                 gui_lib='tkinter',
                 error_on_no_icon=True,
                 consumer=None,
                 app=None
                 ):
        
        self.icon_file = icon_file
        self.tooltip = tooltip
        self.menu_options = menu_options
        self.error_on_no_icon = error_on_no_icon    # TBD this is fucking wtf
        self.consumer = consumer
        self.app = app
        
        self.start()
        
        self.tray_queue = queue.Queue()
        self._setup_tray()
        self._tray_consumer()
        
    def start(self):
        '''set variables here'''
        
    def _setup_tray(self):
        if os.name == 'nt':
            def _start_tray():
                try:
                    logging.info('Starting the tray for windows!')
                    wintray.SysTrayIcon(
                        self.icon_file,
                        self.tooltip,
                        self.menu_options,
                        on_quit=lambda event: self.tray_queue.put(self.shutdown),
                        default_menu_index=None,
                        window_class_name=None,
                        #~ error_on_no_icon=self.error_on_no_icon,  #WTF I DON"T GET IT IT HATES THIS LINE HERE i cannot pass in variables???
                        )
                except Exception as err:
                    # handle all errors that are thrown in the thread in the main thread
                    self.tray_queue.put(lambda err=err: self.tray_queue.put(lambda:raise_error(err)))
        else:
            def _start_tray():
                # TBD FIX THE TRAY FOR UBUNTU after compile throws this error..
                try:
                    aind = appindicator.Indicator.new(
                        'tim',
                        self.icon_file,
                        appindicator.IndicatorCategory.APPLICATION_STATUS)
                    aind.set_status(appindicator.IndicatorStatus.ACTIVE)
                    gtkmenu = gtk.Menu()
                    
                    if hasattr(self, 'shutdown'):
                        quitter = ('Quit', None, lambda e: self.shutdown()),
                        self.menu_options += quitter

                    gtk_menu_items = []
                    self.menu_options = FormBuilder(self.menu_options)
                    for row, col, text, icon, command in self.menu_options: 
                        item = gtk.MenuItem(text)
                        gtk_menu_items.append(item)
                    
                    for item in gtk_menu_items:
                        gtkmenu.append(item)
                    
                    aind.set_menu(gtkmenu)
                    
                    for item in gtk_menu_items:
                        item.show()

                    for item, options in zip(gtk_menu_items, self.menu_options):
                        self._connect_item(item, options[-1])
                    while True:
                        gtk.main()
                        Gdk.threads_leave()
                except TypeError:
                    pass
        thread.start_new_thread(_start_tray, ())

    def _connect_item(self, item, command):
        def func(menu_item):
            self.tray_queue.put(named_partial(command, menu_item))
        item.connect('activate', func)
    
    def _tray_consumer(self):
        def threaded_consumer(): 
            if callable(self.consumer):
                while 1:
                    try:
                        data = self.tray_queue.get(block=False)
                    except queue.Empty:
                        pass
                    else:
                        thread.start_new_thread(self.consumer, (data,))
            else:
                while 1:
                    try:
                        data = self.tray_queue.get(block=False)
                    except queue.Empty:
                        pass
                    else:
                        thread.start_new_thread(data, (),)
                time.sleep(0.01)
        thread.start_new_thread(threaded_consumer, ())

class SystemTaskbar():
    @staticmethod
    def taskbar_remove(root):
        import taskbar
        if os.name == 'nt':
            hwnd = int(root.wm_frame(), 0)
            taskbar.hide_from_taskbar(hwnd)
            # saving a hwnd reference so we can check if we still open later on
            #~ with open (self.check_file,'a') as f:
            #~ f.write(str(hwnd))
            #~ logging.info('adding hwnd to running info from taskbar remove :'+str(hwnd))
            #~ logging.debug('this is hwnd and then type -> %s %s' % (hwnd,type(hwnd)))

if __name__ == '__main__':
    import platform
    
    def setup_logger(log_file):
        '''One function call to set up logging with some nice logs about the machine'''
        
        logging.basicConfig(filename=log_file,
                            filemode='w',
                            level=logging.DEBUG,
                            format='%(asctime)s:%(levelname)s: %(message)s')    # one run

    setup_logger('system_tray.log')

    ICON_FILE = os.path.join(os.getcwd(), 'mario.ico')      # on windows doesn't ahve to be with getcwd(), but on linux yes...
    TOOLTIP = 'testing_tooltip'
    
    def dodo():
        time.sleep(5)
        print('done')
    MENU_OPTIONS = (('ass', None, lambda menu_item: print(menu_item)),
                    ('do', None, lambda menu_item: print(menu_item)),
                    ('aa', None, lambda menu_item: dodo()))

    def consumer(callback):
        print('custom consumer', callback)
        callback()

    sys_tray = SystemTray(
        ICON_FILE,
        TOOLTIP,
        menu_options=MENU_OPTIONS,
        consumer=consumer,
        error_on_no_icon=True)

    while True:
        pass

# References
# Taskbar Https://bbs.archlinux.org/viewtopic.php?id=121303
# http://standards.freedesktop.org/systemtray-spec/systemtray-spec-0.2.html
# http://www.perlmonks.org/?node_id=626617
# Gdk.threads_enter()
# GLib.threads_init()
# Gdk.threads_init()
# Gdk.threads_enter()

'''
    def traySetup(self):
        if os.name != 'posix':
            def mer():
                # TBD FIX THE TRAY FOR UBUNTU after compile throws this error..
                with ignored(TypeError):
                    a = appindicator.Indicator.new(
                        'tim',
                        os.getcwd() +
                        '/' +
                        self.imgdir +
                        'firebird.gif',
                        appindicator.IndicatorCategory.APPLICATION_STATUS)
                    a.set_status(appindicator.IndicatorStatus.ACTIVE)
                    m = gtk.Menu()
                    try:
                        oi = gtk.MenuItem('Open ' + APP_NAME)
                    except:
                        pass
                    #~ ci = gtk.MenuItem('Currently Opened')
                    #~ ri = gtk.MenuItem('Recently Opened')
                    qi = gtk.MenuItem('Quit')
                    m.append(oi)
                    #~ m.append(ci)
                    #~ m.append(ri)
                    m.append(qi)
                    a.set_menu(m)
                    oi.show()
                    #~ ci.show()
                    #~ ri.show()
                    qi.show()
                    oi.connect(
                        'activate',
                        lambda e: self.trayQueue.put(
                            self.root.deiconify))
                    #~ ci.connect('activate', lambda: 0)
                    #~ ri.connect('activate', lambda: 0)

                    def quit(item):
                        gtk.main_quit()
                        self.trayQueue.put(lambda: gui_base.quitter(self))
                    qi.connect('activate', quit)
                    while True:
                        #~ print('first')
                        #~ Gdk.threads_enter()
                        gtk.main()
                        Gdk.threads_leave()
                        #~ print('here')
            #~ GLib.threads_init()
            #~ Gdk.threads_init()
            #~ Gdk.threads_enter()
            #~ print('here')

            thread.start_new_thread(mer, ())
            #~ print('not here')
        elif os.name == 'nt':
            def open():
                hwnd = int(self.root.wm_frame(), 0)
                taskbar.add_to_taskbar(hwnd)
                self.root.deiconify()

            #~ def shutdown(systrayinstance):
                #~ print(systrayinstance)
                #~ print(type(systrayinstance))
                #~ self.trayQueue.put(sys.exit)
                #~ sys.exit()

            #~ menu_options = (('Open Uncrumpled', None, lambda e: self.trayQueue.put(open)),
                #~ ('Opended Notes', None, lambda:0),
                #~ ('Recently Opened', None, (('Say Hello to Simon', None, lambda e:print('shit')),
                #~ ('Switch Icon', None, lambda e:print('shit')),
                #~ )))
            menu_options = (
                ('Open Uncrumpled',
                 None,
                 lambda e: self.trayQueue.put(open)),
            )

            def mer():
                img_file = os.path.join(
                    os.getcwd(),
                    self.imgdir,
                    "firebird.ico")
                tray.SysTrayIcon(
                    img_file,
                    "Uncrumpled Smart Overlay",
                    menu_options,
                    on_quit=lambda e: self.tray_queue.put(
                        self.shutdown))
            thread.start_new_thread(mer, ())

    def tray_consumer(self):
        try:
            data = self.trayQueue.get(block=False)
        except queue.Empty:
            pass
        else:
            data()
        self.root.after(250, self.tray_consumer)
    '''
