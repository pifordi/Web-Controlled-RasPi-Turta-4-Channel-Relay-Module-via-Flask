__author__ = 'Semih YILDIRIM'

from flask import Flask, request, render_template, redirect
import time
import RPi.GPIO as GPIO
from threading import Timer


#****** Setup Board Pins ********

GPIO.setmode( GPIO.BOARD )

plug_a_ctrl = 40 #first relay(CH1) on Pin 40
plug_b_ctrl = 15 #second relay on(CH2) Pin 15
plug_c_ctrl = 16 #third relay on(CH3) Pin 16


"""set all relay pins as an output pin,because the relay is an actuator
and initial value for the pins are set to LOW, since the relay module is HIGH triggered"""
GPIO.setup(plug_a_ctrl, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(plug_b_ctrl, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(plug_c_ctrl, GPIO.OUT, initial=GPIO.LOW)

plug_status = {'a':'OFF', 'b':'OFF', 'c':'OFF'}


#******* Parse User Command *******

class parse_command:
    global plug_a_ctrl
    global plug_b_ctrl
    global plug_c_ctrl


    @staticmethod
    def parse_name(name):
        if name == "a":
            plug = plug_a_ctrl
        elif name == "b":
            plug =  plug_b_ctrl
        elif name == "c":
            plug = plug_c_ctrl
        return plug

    @staticmethod
    def parse_turn_mode(turn_mode):
        if turn_mode == "on":
            level = GPIO.HIGH #the relays are high(3v3) triggered
        elif turn_mode == "off":
            level = GPIO.LOW 
        return level

    @staticmethod
    def parse_interval(number, smh):
        number = float(number)

        if smh == "second":
            interval = number*1
        if smh == "minute":
            interval = number*60
        elif smh == "hour":
            interval = number*3600
        return interval

#****** Pin Control Functions *********

def control(name, turn_mode):
    GPIO.output(parse_command.parse_name(name), parse_command.parse_turn_mode(turn_mode))
    
    plug_status[name] = turn_mode
        
def rule(name, turn_mode, number, smh, then):
    control(name, turn_mode)
    
    start = time.time()
    future_time = parse_command.parse_interval(number, smh) + start
    name = Timer(parse_command.parse_interval(number, smh), control, [name, then])
    name.start()


#*******Flask server part******

app = Flask(__name__)

app.debug = True

@app.route('/')
def index():
    return redirect('home')

@app.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('home.html', a=plug_status.get('a'), b=plug_status.get('b'), c=plug_status.get('c'))

@app.route('/plugs', methods=['GET', 'POST'])
def plugs():
    return render_template('plugs.html', a=plug_status.get('a'), b=plug_status.get('b'), c=plug_status.get('c'))


@app.route('/home/turnall', methods=['POST'])
def home_turnall():
    turn_mode = request.form['turnall']

    control('a', turn_mode)
    control('b', turn_mode)
    control('c', turn_mode)

    return render_template('home.html', a=plug_status.get('a'), b=plug_status.get('b'), c=plug_status.get('c'))
   

@app.route('/plugs/control', methods=['POST'])
def plugs_control():
    plug = request.form['plug']
    turn_mode = request.form['turn']
    
    control(plug, turn_mode)

    return render_template('plugs.html', a=plug_status.get('a'), b=plug_status.get('b'), c=plug_status.get('c'))

@app.route('/plugs/rule', methods=['POST'])
def plugs_rule():
    plug = request.form['plug']
    turn_mode = request.form['turn']
    smh = request.form['smh']
    number = request.form['number']
    then = request.form['then']

    rule(plug, turn_mode, number, smh, then)

    return render_template('plugs.html', a=plug_status.get('a'), b=plug_status.get('b'), c=plug_status.get('c'))


if __name__ == '__main__':
    app.run(host='192.168.1.24', threaded=True, port=3936) #app.run(host='0.0.0.0') This tells your operating system to listen on all public IPs

    
