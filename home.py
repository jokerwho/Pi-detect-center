# encoding: utf-8
import os
from time import sleep
from flask import Flask, render_template, request, Response
import Adafruit_DHT
import RPi.GPIO as GPIO
from camera_pi import Camera

app = Flask(__name__)

GPIO.setmode(GPIO.BCM)
R,G,Y = 26,19,13
FIRE = 23
SMOKE = 21

def getDHTdata():       
    DHT22Sensor = Adafruit_DHT.DHT22
    DHTpin = 6
    hum, temp = Adafruit_DHT.read_retry(DHT22Sensor, DHTpin)
    
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
        u = "GAS!"
        if GPIO.input(FIRE) == GPIO.HIGH:
            GPIO.output(R,GPIO.HIGH)
            u = "GAS AND FIRE!!"
        if GPIO.input(FIRE) == GPIO.LOW:
            GPIO.output(R,GPIO.LOW)
            
    if GPIO.input(SMOKE) == GPIO.HIGH:
        GPIO.output(Y,GPIO.LOW)
        if GPIO.input(FIRE) == GPIO.HIGH:
            GPIO.output(G,GPIO.LOW)
            GPIO.output(R,GPIO.HIGH)
            u = "FIRE!"
        if GPIO.input(FIRE) == GPIO.LOW:
            GPIO.output(R,GPIO.LOW)
            GPIO.output(G,GPIO.HIGH)
            u = "OK~"
    return u
@app.route("/")
def index():
    return render_template('index.html')

@app.route("/detect")
def dht():
    #timeNow = time.asctime( time.localtime(time.time()) )
    temp, hum = getDHTdata()
    u = detect()
    templateData = {
      #'time': timeNow,
      'temp': temp,
      'hum' : hum,
      'u' : u
    }
    return render_template('detect.html', **templateData)

global panServoAngle
global tiltServoAngle
panServoAngle = 90
tiltServoAngle = 0

panPin = 5
#tiltPin = 17

@app.route('/camera')
def camera():
    """Video streaming home page."""
 
    templateData = {
      'panServoAngle'	: panServoAngle,
      'tiltServoAngle'	: tiltServoAngle
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


@app.route("/<servo>/<angle>")
def move(servo, angle):
	global panServoAngle
	global tiltServoAngle
	if servo == 'pan':
		if angle == '+':
			panServoAngle = panServoAngle + 30
		else:
			panServoAngle = panServoAngle - 30
		os.system("python3 angleServoCtrl.py " + str(panPin) + " " + str(panServoAngle))
	if servo == 'tilt':
		if angle == '+':
			tiltServoAngle = tiltServoAngle + 30
		else:
			tiltServoAngle = tiltServoAngle - 30
		os.system("python3 angleServoCtrl.py " + str(tiltPin) + " " + str(tiltServoAngle))
	
	templateData = {
      'panServoAngle'	: panServoAngle,
      'tiltServoAngle'	: tiltServoAngle
	}
	return render_template('camera.html', **templateData)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 8080, debug=True, threaded=True)
