import os
from .system_tray import *

if os.name == 'nt':
	from .win_taskbar import *
	from .wintray import *
