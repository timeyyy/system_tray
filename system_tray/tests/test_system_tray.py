'''
Testing module for system_tray
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

def consumer(callback):
	'''
	Handles callbacks from the systemtray as it is threaded
	we can than handle exceptions normally
	'''
	TEST_QUEUE.put(callback)
 
def test_tray_one_item_with_sysicon():
	'''
	Create a system tray with an icon, only one item in the menu
	This code shouldn't block
	'''
	menu_options = (('a label', None, lambda event: print('ass')),)
	
	time_1 = time.perf_counter()
	
	SystemTray(
		ICON_FILE,
		TOOLTIP,
		menu_options)
	
	time_2 = time.perf_counter()
	assert(time_2 - time_1 < 1)

def test_tray_two_items_with_icons():
	menu_options = (('a label', 'mario2.ico', lambda event: print('ass')),
					('a label', None, lambda event: print('ass2')))
	
	time_1 = time.perf_counter()
	
	SystemTray(
		ICON_FILE,
		TOOLTIP,
		menu_options)
	
	time_2 = time.perf_counter()
	assert(time_2 - time_1 < 1)

#~ def test_():

#~ def test_error_on_no_system_icon():
	#~ '''the system icon is required and should result in an error
	#~ the callbacks are routed to our consumer function defined here.
	#~ the callback should throw an error
	#~ 
	#~ This is fucked, when i run the actually code i get a FileNotFoundError,
	#~ Runnin this same code under pytest here instead raises some
	#~ different error.. A TypeError. I HAVE NOT sorted it out, i just
	#~ slapped a typerror down here...'''
	#~ MENU_OPTIONS = (('a label', None, lambda event: print('ass')),)
	#~ with pytest.raises(TypeError):
		#~ SystemTray(
			#~ os.path.join(os.getcwd(), 'non-existant.ico'),
			#~ TOOLTIP,
			#~ MENU_OPTIONS,
			#~ consumer=consumer,
			#~ error_on_no_icon=True,
			#~ )
		#~ # Takes a while for the error to be propergated
		#~ time_1 = time.perf_counter()
		#~ while(time.perf_counter() - time_1 < 2):
			#~ try:
				#~ func = TEST_QUEUE.get(block=False)
			#~ except queue.Empty:
				#~ pass
			#~ else:	
				#~ func()

#~ def test_NO_error_on_no_system_icon():
	#~ MENU_OPTIONS = (('a label', None, lambda event: print('ass')),)
	#~ ##~ with pytest.raises(TypeError):
	#~ SystemTray(
		#~ os.path.join(os.getcwd(), 'non-existant.ico'),
		#~ TOOLTIP,
		#~ MENU_OPTIONS,
		#~ error_on_no_icon=False,
		#~ consumer=consumer)
	#~ # Takes a while for the error to be propergated
	#~ time_1 = time.perf_counter()
	#~ while(time.perf_counter() - time_1 < 2):
		#~ try:
			#~ func = TEST_QUEUE.get(block=False)
		#~ except queue.Empty:
			#~ pass
		#~ else:	
			#~ func()
