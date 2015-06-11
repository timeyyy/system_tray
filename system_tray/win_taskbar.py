'''
Lower level api, for windows
Used for hiding and adding a window to the taskbar
'''
#http://stackoverflow.com/questions/19425038/hide-window-from-ms-windows-taskbar
#http://stackoverflow.com/questions/2157712/remove-application-from-taskbar-with-c-sharp-wrapper
	#http://nullege.com/codes/show/src@e@n@enso-portable-HEAD@enso@commands@win_tools.py/653/win32gui.SetWindowLong
	#http://bcbjournal.org/articles/vol4/0004/Changing_window_styles_on_the_fly.htm?PHPSESSID=9955d9b4954478bdf0de6e32daa1ff63
import win32gui
from win32con import *
import win32ui

def find_window(name):
    try:
        return win32gui.FindWindow(None, name)
    except win32gui.error:
        print("Error while finding the window")
        return None

def add_to_taskbar(hw):
    try:
        #~ win32gui.ShowWindow(hw, SW_HIDE)
        win32gui.SetWindowLong(hw, GWL_EXSTYLE,WS_EX_APPWINDOW)
        #~ win32gui.SetWindowLong(hw, GWL_EXSTYLE,win32gui.GetWindowLong(hw, GWL_EXSTYLE)| WS_EX_TOOLWINDOW);
        #~ win32gui.ShowWindow(hw, SW_SHOW);
    except win32gui.error:
        print("Error while hiding the window")
        return None	

#~ @staticmethod   
def hide_from_taskbar(hw):
    try:
        win32gui.ShowWindow(hw, SW_HIDE)
        #~ win32gui.SetWindowLong(hw, GWL_EXSTYLE,win32gui.GetWindowLong(hw, GWL_EXSTYLE)| WS_EX_TOOLWINDOW)
        win32gui.SetWindowLong(hw, GWL_EXSTYLE, WS_EX_TOOLWINDOW)
        #~ win32gui.ShowWindow(hw, SW_SHOW)
    except win32gui.error:
        print("Error while hiding the window")
        return None

#~ @staticmethod
def set_topmost(hw):
    try:
          win32gui.SetWindowPos(hw, HWND_TOPMOST, 0,0,0,0, SWP_NOMOVE | SWP_NOSIZE)
    except win32gui.error:
        print("Error while move window on top")

if __name__ == '__main__':	
	import tkinter as tk	
	def do(root):
		#~ hwnd = find_window('tims')
		#~ print(hwnd)
		hwnd=int(root.wm_frame(),0)
		print(hwnd)
		hide_from_taskbar(hwnd)
		   
	def do2(root):
		hwnd=int(root.wm_frame(),0)
		style=win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)	#remove style from bar
		style &=  ~win32con.WS_EX_APPWINDOW
		print(style)
		win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, style)
		style = win32gui.GetWindowLong(hwnd,  win32con.GWL_EXSTYLE)	#add correct style
		style |= win32con.WS_EX_TOOLWINDOW
		win32gui.SetWindowLong(hwnd,win32con.GWL_EXSTYLE, style)
	
	root = tk.Tk()
	root.title('tims')
	root.after(1,do,root)
	root.mainloop()
#http://stackoverflow.com/questions/10675305/how-to-get-the-hwnd-of-window-instance
#~ Window window = Window.GetWindow(this);
#~ var wih = new WindowInteropHelper(window);
#~ IntPtr hWnd = wih.Handle;

