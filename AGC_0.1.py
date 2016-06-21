
import sys
import time
import RPi.GPIO as GPIO
import Adafruit_DHT
from PyQt4 import QtCore, QtGui, uic

# Initialize GPIO
GPIO.setmode(GPIO.BOARD)

light_pin = 7 # Set BOARD rpi.pin for illumination
pump_pin = 3 # Set BOARD rpi.pin for irrigation
vent_pin = 5 # Set BOARD rpi.pin for ventilation

# Set pins for output
GPIO.setup(pump_pin, GPIO.OUT)  
GPIO.setup(vent_pin, GPIO.OUT)  
GPIO.setup(light_pin, GPIO.OUT)

#GPIO.output(light_pin,True)
#GPIO.output(3,True)
#GPIO.output(5,True)

# Sensor and GPIO.input_pin initialize
sensor = Adafruit_DHT.DHT11
pin = '14' # Means BCM.GPIO14 (GPIO.BOARD - 8)


class AG_Control(QtGui.QWidget):
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.color = QtGui.QColor(255, 0, 0)

        # Connect qt-designer form
        uic.loadUi("agc_form.ui", self)

        # Call functions by pushing buttons
        self.connect(self.light_button, QtCore.SIGNAL('clicked()'), self.manualLightControl)
        self.connect(self.pump_button, QtCore.SIGNAL('clicked()'), self.manualPumpControl)
        self.connect(self.vent_button, QtCore.SIGNAL('clicked()'), self.manualVentControl)
        self.connect(self.shutdown_button, QtCore.SIGNAL('clicked()'), self.shutdown)

        # Set timer
        timer = QtCore.QTimer(self)
        timer.start(500)

        # Call functions by timeout
        timer.timeout.connect(self.displayTemperatureAndHumidity)
        timer.timeout.connect(self.automaticControl)  
        
        #self.displayTemperatureAndHumidity() delete this after tests on raspberry
         
            
    def shutdown(self):
        GPIO.cleanup()
        sys.exit()
        
    # Function for redrawing, switching buttons and start\stop devices
    def onOffswitching(self,button,label,pin):
        if button.isChecked():
            label.setText('ON')
            button.setText('Turn OFF')
            self.color.setGreen(170)
            self.color.setRed(0)
            GPIO.output(pin,False)
        else:
            label.setText('OFF')
            button.setText('Turn ON')
            self.color.setGreen(0)
            self.color.setRed(170)
            GPIO.output(pin,True)
        label.setStyleSheet("QLabel { background-color: %s }" % self.color.name())

    # Functions for manual control
    def manualLightControl(self):
        self.manual_control.setChecked(True)
        self.onOffswitching(self.light_button,self.light_status,light_pin)

    def manualPumpControl(self):
        self.manual_control.setChecked(True)
        self.onOffswitching(self.pump_button,self.pump_status,pump_pin)

    def manualVentControl(self):
        self.manual_control.setChecked(True)
        self.onOffswitching(self.vent_button,self.vent_status,vent_pin)

    # Functions for automatic control
    def automaticControl(self):
        if self.automatic_control.isChecked():
            self.automaticClimateControl()
            self.automaticLightControl()
            self.automaticIrrigationControl()

    def automaticClimateControl(self):
        if self.humidity > self.max_humidity_value.value() or self.temperature > self.max_temperature_value.value():
            self.vent_button.setChecked(True)
            self.onOffswitching(self.vent_button,self.vent_status,vent_pin)
        else:
            self.vent_button.setChecked(False)
            self.onOffswitching(self.vent_button,self.vent_status,vent_pin)
              
    def automaticLightControl(self):
        if self.morning_time.time().toString('hh:mm') < time.strftime('%H:%M') < self.evening_time.time().toString('hh:mm'):
            self.light_button.setChecked(True)
            self.onOffswitching(self.light_button,self.light_status,light_pin)
        else:
            self.light_button.setChecked(False)
            self.onOffswitching(self.light_button,self.light_status,light_pin)

    def automaticIrrigationControl(self):
        irrigation_time = ['07:20','13:00','21:00']
        if  time.strftime('%H:%M') in irrigation_time:
            self.pump_button.setChecked(True)
            self.onOffswitching(self.pump_button,self.pump_status,pump_pin)
        else:
            self.pump_button.setChecked(False)
            self.onOffswitching(self.pump_button,self.pump_status,pump_pin)
    # Function for display
    def displayTemperatureAndHumidity(self):
        self.temperature_display.display(self.temperature)
        self.humidity_display.display(self.humidity)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)

window = AG_Control()
window.show()
print('Starting Artifical Greenery Control')
sys.exit(app.exec_())
