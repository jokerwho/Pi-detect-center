# encoding: utf-8
import Adafruit_DHT
import time
import RPi.GPIO as GPIO
import itchat

"""set itchat to login in wechat"""
itchat.auto_login('''hotReload=True''')
rooms = itchat.get_chatrooms(update=True)
rooms = itchat.search_chatrooms(name='itchat_test')
if rooms is not None:
    username = rooms[0]['UserName']
else:
    username = 'filehelper'
    
"""set GPIO"""
GPIO.setmode(GPIO.BCM)
R,G,Y = 26,19,13
FIRE = 23
SMOKE = 21     

if __name__ == '__main__':
    #itchat.run()
    c = 4
    try:
        while (True):
            GPIO.setup(SMOKE,GPIO.IN)
            GPIO.setup(FIRE,GPIO.IN)
            GPIO.setup(R,GPIO.OUT)
            GPIO.setup(G,GPIO.OUT)
            GPIO.setup(Y,GPIO.OUT)
            #f = GPIO.input(FIRE)
            #y = GPIO.input(SMOKE)
            if GPIO.input(SMOKE) == GPIO.LOW:
                GPIO.output(G,GPIO.LOW)
                GPIO.output(Y,GPIO.HIGH)
                u = "检测到有害气体！"
                m = 1
                if GPIO.input(FIRE) == GPIO.HIGH:
                    GPIO.output(R,GPIO.HIGH)
                    u = "检测到有害气体和火焰！"
                    m = 3
                if GPIO.input(FIRE) == GPIO.LOW:
                    GPIO.output(R,GPIO.LOW)

            if GPIO.input(SMOKE) == GPIO.HIGH:
                GPIO.output(Y,GPIO.LOW)
                if GPIO.input(FIRE) == GPIO.HIGH:
                    GPIO.output(G,GPIO.LOW)
                    GPIO.output(R,GPIO.HIGH)
                    u = "检测到火焰！"
                    m = 2
                if GPIO.input(FIRE) == GPIO.LOW:
                    GPIO.output(R,GPIO.LOW)
                    GPIO.output(G,GPIO.HIGH)
                    u = "无异常~"
                    m = 4
                    
            if m != c:
                if m == 1:
                    #if rooms is not None:
                        #username = rooms[0]['UserName']
                        itchat.send(str(u),toUserName=username)
                        c = 1
                        continue
                if m == 2:
                    #if rooms is not None:
                        #username = rooms[0]['UserName']
                        itchat.send(str(u),toUserName=username)
                        c = 2
                        continue
                if m == 3:
                    #if rooms is not None:
                        #username = rooms[0]['UserName']
                        itchat.send(str(u),toUserName=username)
                        c = 3
                        continue
                if m == 4:
                        itchat.send(str(u),toUserName=username)
                        c = 4
            else:
                continue
            time.sleep(1)
    except KeyboardInterrupt:
        pass
        GPIO.cleanup()
