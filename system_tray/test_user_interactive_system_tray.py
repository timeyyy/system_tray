'''
Tests that normally require you to close the tray icons etc
'''
from __future__ import print_function
from __future__ import absolute_import

import os
import time
import queue

import pytest

from system_tray import SystemTray
import tray

ICON_FILE = os.path.join(os.getcwd(), 'Heineken2.ico')
TOOLTIP = 'testing_tooltip'
TEST_QUEUE = queue.Queue()

def test_windows_lower_api():
	'''Tests the lower api on windows you have to quit to continue'''
	
	if os.name == 'posix':
		return
	
	import itertools
	import glob
	
	icons = itertools.cycle(glob.glob('*.ico'))
	hover_text = "SysTrayIcon.py Demo"
	
	def hello(sysTrayIcon):
		print("Hello World.")
		
	def simon(sysTrayIcon):
		print("Hello Simon.")
		
	def switch_icon(sysTrayIcon):
		sysTrayIcon.icon = next(icons)
		sysTrayIcon.refresh_icon()
		
	menu_options = (('Say Hello', next(icons), hello),
					('Switch Icon', None, switch_icon),
					('A sub-menu', next(icons), (('Say Hello to Simon', next(icons), simon),
												  ('Switch Icon', next(icons), switch_icon),
												 ))
				   )
	def bye(sysTrayIcon): print('Bye, then.')
	
	tray.SysTrayIcon(next(icons), hover_text, menu_options, on_quit=bye, default_menu_index=1)
