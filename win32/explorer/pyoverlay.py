import os
from win32com.shell import shell, shellcon
import winerror

class NuxeoDriveIconOverlay:
  
  _reg_clsid_ = '{B4123171-F6D6-4FAD-9402-8F6B04E439C7}'
  _reg_progid_ = 'NuxeoDrive.PythonOverlayHandler'
  _reg_desc_ = 'Icon Overlay Handler for Nuxeo Drive'
  _public_methods_ = ['GetOverlayInfo', 'GetPriority', 'IsMemberOf']
  _com_interfaces_ = [shell.IID_IShellIconOverlayIdentifier]
  
  def GetOverlayInfo(self):
    return (r'C:\Drive\nuxeo-dm.ico', 0, shellcon.ISIOI_ICONFILE)
  
  def GetPriority(self):
    return 50
  
  def IsMemberOf(self, fname, attributes):
    if (fname.index("nuxeo")>=0) :
        return winerror.S_OK
    if os.path.exists (os.path.join (fname, "__init__.py")):
        return winerror.S_OK
    return winerror.E_FAIL

if __name__=='__main__':
  import win32api
  import win32con
  import win32com.server.register
  
  win32com.server.register.UseCommandL	ine (IconOverlay)
  keyname = r'Software\Microsoft\Windows\CurrentVersion\Explorer\ShellIconOverlayIdentifiers\NuxeoDriveOverlay'
  key = win32api.RegCreateKey (win32con.HKEY_LOCAL_MACHINE, keyname)
  win32api.RegSetValue (key, None, win32con.REG_SZ, IconOverlay._reg_clsid_)

