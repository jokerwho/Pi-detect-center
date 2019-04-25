# encoding: utf-8
import Adafruit_DHT
import time
import RPi.GPIO as GPIO
import itchat

"""set itchat to login in wechat"""
itchat.auto_login(hotReload=True)
rooms = itchat.get_chatrooms(update=True)
rooms = itchat.search_chatrooms(name='itchat_test')
if rooms is not None:
    username = rooms[0]['UserName']
else:
    username = 'filehelper'
    
"""get hum and temp"""
def getDHTdata():       
    DHT11Sensor = Adafruit_DHT.DHT11
    DHTpin = 6
    hum, temp = Adafruit_DHT.read_retry(DHT11Sensor, DHTpin)
    
    if hum is not None and temp is not None:
        hum = round(hum)
        temp = round(temp, 1)
    return temp, hum

"""listen for users to send msg and return dht"""
@itchat.msg_register(itchat.content.TEXT,isGroupChat=True)
def reply_msg(msg):
    if msg['Content'] == u'温湿度':
        #if rooms is not None:
            #username = rooms[0]['UserName']
            temp, hum = getDHTdata()
            itchat.send_msg("温度：" + str(temp) + "℃" + '\n' + "湿度：" + str(hum) + "%",toUserName=username)
        

if __name__ == '__main__':
    itchat.run()