from umqtt.simple import MQTTClient
from time import sleep_ms
from ds18x20 import DS18X20
from onewire import OneWire
import dht

server = "192.168.2.109" #mqtt server
node_number = "Link_0"   #name to be transmitted to mqtt
mqtt_c = MQTTClient(node_number, server)
try:
    mqtt_c.connect()
except:
    print("Connection to MQTT-Broker Failed")
    esp.deepsleep(280*10**6)
#send debug messages to mqtt
def debug_mqtt(msg):
    sleep_ms(20)
    print(msg)
    try:
        sleep_ms(10)
        mqtt_c.publish("debug",msg)
        sleep_ms(30)
    except:
        print("mqtt_debug failed for:"+msg)


debug_mqtt("Bringing up ext power.")
pin15 = machine.Pin(15, machine.Pin.OUT) #Enable Groove power supply on Wio Boards
sleep_ms(1000)
#without sleep the board crashes from time to time
pin15.high()
#2 seconds gives the sensors time to level in und keeps the board from crashing
sleep(2)

debug_mqtt("Ext Power up")
debug_mqtt(str(time_diff))

f = open('timediff','a')
f.write(str(time_diff)+"\n")
f.close()

#define the measurement interval
deepsleep_seconds = 280*1000000

#ds18b20 roms in hex (can be determined through the webREPL/ serialREPL)
roms = [bytearray(b'(Y\xe3\x07\x08\x00\x00\xe0'),
        bytearray(b'(Y\xdc\x08\x08\x00\x00\x91'),
        bytearray(b'(|\xe0\t\x08\x00\x00\x03'),
        bytearray(b'(\xec\x12\t\x08\x00\x00\x97')]
idx_ds18 = [12,13,14,15]

#define dht sensor type and pin and domoticz idx
sensor_type = 11 #type of Sensor (dht11 or dht22)
sense_pin_11 = 14 #Pin the Sensor is connected to (#5 on Node)
sense_pin_ds18 = 12 #Pin for the ds18b20 sensors
idx_dht = 11 #index in Domoticz (#9 Node 0, #8 Link0)

#read DHT from the DTH library
dht_sens = dht.DHT11(machine.Pin(sense_pin_11)) #dht_sens = dht.DHT22(machine.Pin(sense_pin))
dht_sens.measure()

#message for domoticz mqtt broker
message= '{ "idx" :'+ str(idx_dht) +', "nvalue" : 0, "svalue" : "'+str(dht_sens.temperature())+';'+str(dht_sens.humidity())+';1" }'
debug_mqtt(message)
f = open('data','a')
f.write(str(dht_sens.temperature())+'; '+str(dht_sens.humidity())+"\n")
f.close()
try:
    mqtt_c.publish("domoticz/in",message)
except:
    print("publish failed for: "+message)

#reading out ds18b20 
ow = OneWire(machine.Pin(sense_pin_ds18))
ds = DS18X20(ow)

def read_ds18b20(ds,roms,idx):
    ds.convert_temp()
    sleep_ms(750)
    f = open('data','a')
    for x, rom in enumerate(roms):
        temp = ds.read_temp(rom)
        print(":".join([str(hex(x)[2::]) for x in rom])+" has Temp of: "+str(temp))
        f.write(str(temp)+"; ")
        message= '{ "idx" :'+ str(idx[x]) +', "nvalue" : 0, "svalue" : "'+str(temp)+';1" }'
        print(message)
        mqtt_c.publish("domoticz/in",message)
    f.write("\n")
    f.close()
try:
    read_ds18b20(ds,roms,idx_ds18)
except:
    debug("Could not read Temperatures")
    pin15.low()
    deepsleep()

#power off sensors
pin15.low()
#go to sleep
deepsleep()