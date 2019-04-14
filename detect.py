import Adafruit_DHT
import time
import RPi.GPIO as GPIO
import itchat

"""set itchat to login in wechat"""
itchat.auto_login(hotReload=True)
rooms = itchat.get_chatrooms(update=True)
rooms = itchat.search_chatrooms(name='itchat_test')
"""set GPIO"""
GPIO.setmode(GPIO.BCM)
R,G,Y = 26,19,13
FIRE = 23
SMOKE = 21

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
        if rooms is not None:
            username = rooms[0]['UserName']
            temp, hum = getDHTdata()
            itchat.send_msg("温度：" + temp + "℃" + '\n' + "湿度：" + hum + "%",toUserName=username)
        
"""get gas and fire,send warning to wechat"""
def detect():
    GPIO.setup(SMOKE,GPIO.IN)
    GPIO.setup(FIRE,GPIO.IN)
    GPIO.setup(R,GPIO.OUT)
    GPIO.setup(G,GPIO.OUT)
    GPIO.setup(Y,GPIO.OUT)
    if GPIO.input(SMOKE) == GPIO.LOW:
        GPIO.output(G,GPIO.LOW)
        GPIO.output(Y,GPIO.HIGH)
        u = "检测到有害气体！"
        if rooms is not None:
            username = rooms[0]['UserName']
            itchat.send(str(u),toUserName=username)
        if GPIO.input(FIRE) == GPIO.HIGH:
            GPIO.output(R,GPIO.HIGH)
            u = "检测到有害气体和火焰！"
            if rooms is not None:
                username = rooms[0]['UserName']
                itchat.send(str(u),toUserName=username)
        if GPIO.input(FIRE) == GPIO.LOW:
            GPIO.output(R,GPIO.LOW)
            
    if GPIO.input(SMOKE) == GPIO.HIGH:
        GPIO.output(Y,GPIO.LOW)
        if GPIO.input(FIRE) == GPIO.HIGH:
            GPIO.output(G,GPIO.LOW)
            GPIO.output(R,GPIO.HIGH)
            u = "检测到火焰！"
            if rooms is not None:
                username = rooms[0]['UserName']
                itchat.send(str(u),toUserName=username)
        if GPIO.input(FIRE) == GPIO.LOW:
            GPIO.output(R,GPIO.LOW)
            GPIO.output(G,GPIO.HIGH)
            u = "无异常~"
    return u

if __name__ == '__main__':
    itchat.run()
    try:
        while (True):
            detect()
            u = detect()
            print(str(u))
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
        GPIO.cleanup()