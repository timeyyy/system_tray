import queue

from system_tray import SystemTray

ICON_FILE = 'Heineken2.ico'
TOOLTIP = 'testing_tooltip'

MENU_OPTIONS = (('a label', None, lambda event: print('ass')),)

def consumer(callback):
	print('custom consumer')
	callback()

sys_tray = SystemTray(
	ICON_FILE,
	TOOLTIP,
	menu_options=MENU_OPTIONS,
	consumer=consumer,
	error_on_no_icon=True)

while True:
	try:
		func = sys_tray.tray_queue.get(block=False)
	except queue.Empty:
		pass
	else:	
		func() 
