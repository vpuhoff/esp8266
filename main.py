import uos, machine
import BlynkLib
from BlynkTimer import BlynkTimer

def init_pin(pin, mode="pwm"):
    if mode=="pwm":
        p = machine.PWM(machine.Pin(pin, machine.Pin.OUT))
        p.freq(100)
    if mode=="in":
        return machine.Pin(pin, machine.Pin.IN, machine.Pin.PULL_UP)
    return p

pins = {
        1: init_pin(4), 
        2: init_pin(0), 
        3: init_pin(2), 
        4: init_pin(5) 
    }
  


BLYNK_AUTH = 'usU1b-F4U17WRY1QPgf7guYkKueR8F9u'

print("Connecting to Blynk...")
blynk = BlynkLib.Blynk(BLYNK_AUTH)

def log(text):
    print(text)
    blynk.virtual_write(255, text + '\n')
 
@blynk.on("connected")
def blynk_connected(ping):
    blynk.sync_virtual(list(pins.keys()))
    log('Blynk ready. Ping:'+ str(ping) + 'ms')

@blynk.on("disconnected")
def blynk_disconnected():
    print('Blynk disconnected')
    

stop = False

def gpio_handler(port,value):
    global stop
    if int(port[0]) == 0 :
        if int(value[0])==0:
            stop = True 
    else:        
        try:
            p = pins.get(int(port[0]))
            p.duty(int(value[0]))
            log(port+":"+str(value[0]))
        except Exception as e:
            log(str(e)) 
         

@blynk.on("V*")
def blynk_handle_vpins(pin, value):
    #print("V{} value: {}".format(pin, value))
    gpio_handler(pin,value)

@blynk.on("readV*")
def blynk_handle_vpins_read(pin):
    #print("Server asks a value for V{}".format(pin))
    blynk.virtual_write(pin, 0)

# Run blynk in the main thread:
# runLoop()


timer = BlynkTimer()


# Will Print Every 5 Seconds
def print_me():
    gc.collect()
    free_mem = gc.mem_free()
    log("Free memory: "+str(int(free_mem/1000))+"kb")  

print_me()

 

import ntptime 
import time
import utime
#if needed, overwrite default time server
ntptime.host = "time.google.com"

def fromtimestamp():
    return time.localtime(time.time()+ 3*3600)

def format_time(hh, mm, ss):
    return "%02d:%02d:%02d" % (hh, mm, ss)
 
def now():
   t = fromtimestamp()
   return ("%04d-%02d-%02d " % (t[0], t[1], t[2]) +
            format_time(t[3], t[4], t[5]))

def sync_time():
    log("Local time before synchronization：%s" % now())
    #make sure to have internet connection
    ntptime.settime()
    log("Local time after synchronization：%s" % now())
 
# Add Timers
timer.set_interval(120, print_me)
timer.set_interval(1600, sync_time)
 

    
def deep_sleep(delay):
    # configure RTC.ALARM0 to be able to wake the device
    # rtc = machine.RTC()
    #rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)    # set RTC.ALARM0 to fire after 10 seconds (waking the device)
    #rtc.alarm(rtc.ALARM0, delay)    # put the device to sleep
    machine.deepsleep(delay)
    



 
log("Start blynk...")
while not stop:
    blynk.run()
    timer.run()
    
log("Start ftp...")
import uftpserver

log("Restarting...") 
machine.reset()

