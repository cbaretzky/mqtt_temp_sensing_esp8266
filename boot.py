# This file is executed on every boot (including wake-boot from deepsleep)

#Get out of the UART with mismatched baudrate on the serial
print('        '*40+'\n')
print('Start booting')

autoconnect_timeout = 80
deepsleep_seconds = 2000
fail_deepsleep = 600
known_APS=[['AP1','PW1'], #AP1 : SSID of first AP, PW1 passwd for first AP
           ['AP2','PW2'],
           ['AP3','PW3'],
           ['AP4','PW4']]

import gc
import utime
from time import sleep
import network
import machine
import esp
from machine import reset
from machine import Timer
tim = Timer(-1)
def overtime(t): #overtime, puts esp8266 to sleep
    print("overtime soon")
    sleep(1)
    for x in range(0,10):
        print(str(10-x)+" seconds left until overtime")
        sleep(1)
    try:
        pin15.low() #On Wio Node/Link pin15 defines power to the external ports
    except:
        print("pin15 not defined yet")
    esp.deepsleep(600*10**6)
#setup callback to put esp to sleep in case something goes wrong
tim.init(period=180*10**3, mode=Timer.ONE_SHOT, callback=overtime)

gc.collect()
time_start=utime.ticks_ms()
#initiate wifi, done after the callback is set up
wlan = network.WLAN(network.STA_IF)
counter=0
#default deepsleep function
def deepsleep(sleep_time=deepsleep_seconds):
    for x in range (0,3):
        print("Deepsleep in "+str((10-x))+" Seconds")
        sleep(1)
    try:
        mqtt_c.disconnect()
    except:
        print("could not disconnect")
    sleep(1)
    esp.deepsleep(sleep_time*1000000)
    sleep(1)


#helper function to view file contents from commandline
def cat(Filename):
    f = open(Filename)
    print(f.read())
    f.close()

#The esp8266 usually autoconnects to the last known AP.
#If you connect manually every time it wakes up, you can wear out the flash
#where the AP info is stored.
while not wlan.isconnected():
    print("waiting for autoconnect:"+str(autoconnect_timeout-counter)+"Seconds")
    sleep(1)
    counter +=1
    if counter > autoconnect_timeout:
        print("autoconnect failed")
        break
#In case the autoconnect failes (e.g. last connected AP shut down) it looks for
#other known APs and tries to connect to the strongest signal. Goes to sleep
#if no connection can be established.
while not wlan.isconnected():
    print("trying to connect maunally")
    visible_AP=sorted(wlan.scan(), key=lambda sig_str: -sig_str[3])
    print(visible_AP)
    for AP in visible_AP:
        print('Looking for:'+AP[0].decode())
        if AP[0].decode() in str(known_APS):
            for known_AP in known_APS:
                if AP[0].decode() == known_AP[0]:
                    print("Found: "+known_AP[0])
                    break
            counter=0
            print('Connecting to: '+AP[0].decode() )
            wlan.connect(known_AP[0],known_AP[1])
            while not wlan.isconnected():
                print("waiting for manual connection:"+str(autoconnect_timeout-counter)+"Seconds")
                counter +=1
                sleep(1)
                if counter > autoconnect_timeout:
                    print("could not connect going to sleep")
                    deepsleep(fail_deepsleep)

                pass
            break
print("connected!:")
print(str(wlan.ifconfig()))
gc.collect()
#start webrepl for remote cli
import webrepl
webrepl.start()
time_stop=utime.ticks_ms()

#get time from poweron to connected wifi and working webrepl
time_diff=utime.ticks_diff(time_stop,time_start)
print('End Booting @: '+str(time_diff))
del(time_stop)
