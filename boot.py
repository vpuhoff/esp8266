# This file is executed on every boot (including wake-boot from deepsleep)
from micropython import alloc_emergency_exception_buf
import esp
esp.osdebug(None)
import uos, machine
#uos.dupterm(None, 1) # disable REPL on UART(0)
import gc
import network
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect("DarkNet Core", "Integral320") # Connect to an AP
sta_if.isconnected()                      # Check for successful connection
while not sta_if.isconnected():
    pass
# Change name/password of ESP8266's AP:
ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)
# ap_if.config(essid="<AP_NAME>", authmode=network.AUTH_WPA_WPA2_PSK, password="<password>")
print('network config:', sta_if.ifconfig())

gc.collect()

def load_updates(size, free):
    print('free %d of %d blocks' % (free, size))
    from loader import update
    update()
    print('free %d of %d blocks' % (free, size))

if machine.reset_cause() == machine.DEEPSLEEP_RESET:
    print('woke from a deep sleep')
else:
    print('power on or hard reset')
    stat = uos.statvfs ("/")
    size = stat[0]
    free = stat[3]
    load_updates(size, free)
    gc.collect()