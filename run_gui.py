import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic, QtCore

class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('gui.ui', self) 
        self.default_styles = {
            'forwardButton': self.forwardButton.styleSheet(),
            'leftButton': self.leftButton.styleSheet(),
            'rightButton': self.rightButton.styleSheet(),
            'stopButton': self.stopButton.styleSheet(),
            'motorButton': self.motorButton.styleSheet(),
        }
        
        self.toggle_states = {
            'forwardButton': False,
            'leftButton': False,
            'rightButton': False,
            'stopButton': False,
            'motorButton': False,
        }
        
        self.show()

    def keyPressEvent(self, event):
        self.off_button(self.forwardButton)
        self.off_button(self.leftButton)
        self.off_button(self.rightButton)
        self.off_button(self.stopButton)

        if event.key() == QtCore.Qt.Key_W:
            self.toggle_button(self.forwardButton)
            self.off_button(self.stopButton)

        elif event.key() == QtCore.Qt.Key_A:
            self.toggle_button(self.leftButton)

        elif event.key() == QtCore.Qt.Key_D:
            self.toggle_button(self.rightButton)

        elif event.key() == QtCore.Qt.Key_S:
            self.toggle_button(self.stopButton)
            self.off_button(self.forwardButton)

        elif event.key() == QtCore.Qt.Key_L:
            self.toggle_button(self.motorButton)

    def toggle_button(self, button):
        btn_name = button.objectName()
        self.toggle_states[btn_name] = not self.toggle_states[btn_name]
        if self.toggle_states[btn_name]:
            button.setStyleSheet("background-color: #BBDEFB;")
        else:
            button.setStyleSheet(self.default_styles[btn_name])

    def off_button(self, button):
        btn_name = button.objectName()

        self.toggle_states[btn_name] = False
        button.setStyleSheet(self.default_styles[btn_name])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    sys.exit(app.exec_())
