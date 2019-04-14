from flask import Flask, render_template, Response
app = Flask(__name__)


from camera_pi import Camera

import Adafruit_DHT
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
    
R,G,Y = 26,19,13
FIRE = 23
SMOKE = 21

def getDHTdata():       
    DHT11Sensor = Adafruit_DHT.DHT11
    DHTpin = 6
    hum, temp = Adafruit_DHT.read_retry(DHT11Sensor, DHTpin)
    
    if hum is not None and temp is not None:
        hum = round(hum)
        temp = round(temp, 1)
    return temp, hum

def detect():
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
        u = "Gas!!"
        if GPIO.input(FIRE) == GPIO.HIGH:
            GPIO.output(R,GPIO.HIGH)
            u = "Gas and Fire!!!"
        if GPIO.input(FIRE) == GPIO.LOW:
            GPIO.output(R,GPIO.LOW)
            
    if GPIO.input(SMOKE) == GPIO.HIGH:
        GPIO.output(Y,GPIO.LOW)
        if GPIO.input(FIRE) == GPIO.HIGH:
            GPIO.output(G,GPIO.LOW)
            GPIO.output(R,GPIO.HIGH)
            u = "Fire!!"
        if GPIO.input(FIRE) == GPIO.LOW:
            GPIO.output(R,GPIO.LOW)
            GPIO.output(G,GPIO.HIGH)
            u = "Safe~"
    return u
@app.route("/")
def index():
    timeNow = time.asctime( time.localtime(time.time()) )
    temp, hum = getDHTdata()
    u = detect()
    templateData = {
      'time': timeNow,
      'temp': temp,
      'hum' : hum,
      'u' : u
    }
    return render_template('index.html', **templateData)

@app.route('/camera')
def cam():
    """Video streaming home page."""
    timeNow = time.asctime( time.localtime(time.time()) )
    templateData = {
      'time': timeNow
    }
    return render_template('camera.html', **templateData)


def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port =8080, debug=True, threaded=True)
