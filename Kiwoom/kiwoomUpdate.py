import os
import time

from pywinauto import application
from pywinauto import timings

app = application.Application()
app.start("C:/KiwoomFlash3/bin/nkministarter.exe")

title = "번개3 Login"
dlg = timings.wait_until_passes(20, 0.5, lambda: app.window(title=title))

pass_ctrl = dlg.Edit2
pass_ctrl.set_focus()
pass_ctrl.type_keys("jun1022")
cert_ctrl = dlg.Edit3

cert_ctrl.set_focus()
cert_ctrl.type_keys("fkdbf0230!@#")

btn_ctrl = dlg.Button0
btn_ctrl.click()

time.sleep(50)
os.system("taskkill /im nkmini.exe") #윈도우 프로그램 종료
