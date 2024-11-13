import sys
import serial
import time
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5 import uic
from PyQt5.QtCore import Qt, Q_ARG, QMetaObject

# change bluetooth port accordingly
bluetooth_port = 'COM14'
baud_rate = 9600

try:
    bt_connection = serial.Serial(bluetooth_port, baud_rate, timeout=2)
    time.sleep(2)
    print("Connected to Bluetooth module on", bluetooth_port)
    bt_connected = True
except Exception as e:
    print(f"Error opening Bluetooth connection: {e}")
    bt_connected = False

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()    
        self.motor_on = False
        self.left_fin_open = False
        self.right_fin_open = False
        self.forward_loop_running = False
        self.left_loop_running = False
        self.right_loop_running = False
        self.break_engaged = False
        uic.loadUi('gui.ui', self) 
        self.default_styles = {
            'forwardButton': self.forwardButton.styleSheet(),
            'leftButton': self.leftButton.styleSheet(),
            'rightButton': self.rightButton.styleSheet(),
            'stopButton': self.stopButton.styleSheet(),
            'motorButton': self.motorButton.styleSheet(),
        }
        self.show()
        self.label = self.findChild(QLabel, 'label')

    def keyPressEvent(self, event):
        #stop any active loops when new input is received
        self.forward_loop_running = False
        self.left_loop_running = False
        self.right_loop_running = False
        self.break_engaged = False
        self.toggle_button(self.stopButton, self.break_engaged)
        self.toggle_button(self.forwardButton, self.forward_loop_running)
        self.toggle_button(self.leftButton, self.left_loop_running)
        self.toggle_button(self.rightButton, self.right_loop_running)

        #forward and stop
        if event.key() == Qt.Key_W and not self.forward_loop_running:
            bt_connection.write(b'5')
            self.motor_on = True
            self.forward_loop_running = True
            self.toggle_button(self.forwardButton, self.forward_loop_running)
            threading.Thread(target=self.forward_loop, daemon=True).start()
        if event.key() == Qt.Key_S:
            self.break_engaged = True
            self.toggle_stop()
            self.toggle_button(self.stopButton, self.break_engaged)

        #left right turn
        if event.key() == Qt.Key_A:
            self.left_loop_running = True
            self.break_engaged = False
            self.toggle_button(self.leftButton, self.left_loop_running)
            threading.Thread(target=self.left_loop, daemon=True).start()            
        if event.key() == Qt.Key_D:
            self.right_loop_running = True
            self.break_engaged = False
            self.toggle_button(self.rightButton, self.right_loop_running)
            threading.Thread(target=self.right_loop, daemon=True).start()
        
        #motor
        if event.key() == Qt.Key_L:   
            self.toggle_motor()

        #safe exit, turn off all components before exiting
        elif event.key() == Qt.Key_Escape:
            print("Exiting...")
            self.shutdown()
            time.sleep(0.5)
            bt_connection.close()
            self.close()

    def forward_loop(self):
        global bt_connection
        while self.forward_loop_running:
            bt_connection.write(b'F')
            time.sleep(4.2)

    def left_loop(self):
        global bt_connection
        while self.left_loop_running:
            bt_connection.write(b'L')
            time.sleep(2.5)

    def right_loop(self):
        global bt_connection
        while self.right_loop_running:
            bt_connection.write(b'R')
            time.sleep(2.5)

    def toggle_motor(self):
        global bt_connection
        if not self.motor_on:
            bt_connection.write(b'5')
            self.motor_on = True
        else:
            bt_connection.write(b'e')
            self.motor_on = False
        self.toggle_button(self.motorButton, self.motor_on)

    def toggle_stop(self):
        global bt_connection
        bt_connection.write(b'S')

    def toggle_button(self, button, toggle_states):
        btn_name = button.objectName()
        if toggle_states:
            button.setStyleSheet("background-color: #BBDEFB;")
        else:
            button.setStyleSheet(self.default_styles[btn_name])

    def shutdown(self):
        global bt_connection
        bt_connection.write(b'O')

def read_serial_data(app):
    while True:
        try:
            if bt_connection.is_open and bt_connection.in_waiting > 0:
                raw_data = bt_connection.readline()
                try:
                    data = raw_data.decode('utf-8').strip()
                    distance_display = f"Distance: {data} cm"
                    QMetaObject.invokeMethod(app.label, "setText", Qt.QueuedConnection, Q_ARG(str, distance_display))
                except UnicodeDecodeError:
                    print("Error: Failed to decode data. Skipping this line.")
                    continue
            elif not bt_connection.is_open:
                print("Bluetooth connection closed. Exiting serial reading thread.") 
        except serial.SerialException:
            print(f"Bluetooth connection closed. Exiting serial reading thread.")
            break 

if __name__ == "__main__":
    if bt_connected:
        app = QApplication(sys.argv)
        main_window = MainWindow()
        serial_thread = threading.Thread(target=read_serial_data, args=(main_window,),daemon=True)
        serial_thread.start()
        sys.exit(app.exec_())
    else:
        print("Bluetooth connection failed. Please try again.")