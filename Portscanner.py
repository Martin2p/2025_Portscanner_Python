"""
Copyright © 2025 Martin Tastler

DEUTSCH:

Dieses Programm und der Quellcode dürfen ausschließlich für private und nicht-kommerzielle Zwecke verwendet werden.

Jede kommerzielle Nutzung, Veränderung, Verbreitung oder Veröffentlichung ist ohne ausdrückliche schriftliche Erlaubnis des Autors untersagt.

Das Kopieren oder Verwenden einzelner Codebestandteile für andere Projekte ist ebenfalls nicht gestattet, sofern keine vorherige Zustimmung vorliegt.
Bei Interesse an einer kommerziellen Nutzung oder Lizenzierung wenden Sie sich bitte an den Autor.

ENGLISH:
This software and its source code may only be used for private and non-commercial purposes.
Any commercial use, modification, distribution, or publication is strictly prohibited without the prior written permission of the author.

Copying or using individual parts of the code in other projects is also not permitted unless approved in advance.

For commercial licensing inquiries or permission requests, please contact the author.

-----------------------------------------
Author / Autor: Martin Tastler

martin.tastler@posteo.de

Date: July 2025

"""
import sys, os, socket, time

from PyQt6.QtCore import QThread, pyqtSignal, QFile
from PyQt6.QtWidgets import QApplication, QMainWindow

"""
     in terminal: 
     pyuic5 portscanner_gui.ui -o ui_portscanner_gui.py
     or
     pyside6-uic portscanner_gui.ui -o ui_portscanner_gui.py
     or
     pyuic6 portscanner_gui.ui -o ui_portscanner_gui.py
 """
from portscanner_gui import Ui_MainWindow


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller temporärer Ordner
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# Scanner for open Ports for anit freezing window
class openPortsScanner(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(list)

    def __init__(self,  host="127.0.0.1", start=1, end=1024, timeout=0.5):
        super().__init__()
        self.host = host
        self.start_port = start
        self.end_port = end
        self.timeout = timeout


    def run(self):
        open_ports = []
        for port in range(self.start_port, self.end_port + 1):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self.timeout)
                result = s.connect_ex((self.host, port))
                if result == 0:
                    open_ports.append(port)
            progress = int((port - self.start_port) / (self.end_port - self.start_port) * 100)
            self.progress.emit(progress)
        self.finished.emit(open_ports)


# Scanner for open Ports for anit freezing window
class freePortsScanner(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(list)

    def __init__(self, start=1, end=65535):
        super().__init__()
        self.start_port = start
        self.end_port = end

    def run(self):
        free_ports = []
        total_ports = self.end_port - self.start_port + 1

        for idx, port in enumerate(range(self.start_port, self.end_port + 1), start=1):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.01)
                try:
                    s.bind(("", port))  # if its possible -> Port is free
                    free_ports.append(port)
                except OSError:
                    pass  # Port not free

            self.progress.emit(int((idx / total_ports) * 100))

        self.finished.emit(free_ports)


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # window size
        self.resize(640, 480)

        # getting the path! to the built GUI (done with QT)
        ui_path = os.path.abspath("portscanner_gui.ui")
        print(f"Loading UI-File from: {ui_path}")

        # Setup of the UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


        if not self.ui:
            raise RuntimeError("unable to load the UI")

        # Button Events:
        # laying function on clear Button
        self.ui.closeBtn.clicked.connect(self.close)

        # calling method for getting the own IP Address
        self.ui.myIPBtn.clicked.connect(self.showOwnIP)

        # calling method for getting open Ports on the system
        self.ui.freeBtn.clicked.connect(self.showFreePorts)
        self.ui.progressBarFree.setMaximum(100)

        # calling method for getting open Ports on the system
        self.ui.openPortsBtn.clicked.connect(self.showOpenPorts)
        self.ui.progressBarOpen.setMaximum(100)


    # function for getting free ports
    def showFreePorts(self):

        self.ui.freeBtn.setEnabled(False)
        self.ui.freePortsText.setText(f"Scanning")

        self.thread = freePortsScanner()
        self.thread.progress.connect(self.ui.progressBarFree.setValue)
        self.thread.finished.connect(self.scan_free_finished)
        self.thread.start()


    # function for getting open ports on the system
    def showOpenPorts(self):

        self.ui.openPortsBtn.setEnabled(False)
        self.ui.openPortsText.setText(f"Scanning...")

        self.thread = openPortsScanner()
        self.thread.progress.connect(self.ui.progressBarOpen.setValue)
        self.thread.finished.connect(self.scan_open_finished)
        self.thread.start()


    # function finish open ports
    def scan_open_finished(self,open_ports):
        self.ui.openPortsBtn.setEnabled(True)
        if open_ports:
            self.ui.openPortsText.append("Free ports on your system:")
            for port in open_ports:
                self.ui.openPortsText.append(f"[+] Port {port}")
        else:
            self.ui.openPortsText.append("No ports are.")


    # function finish free ports
    def scan_free_finished(self, open_ports):
        self.ui.freeBtn.setEnabled(True)
        if open_ports:
            self.ui.freePortsText.append("Free ports on your system:")
            for port in open_ports:
                self.ui.freePortsText.append(f"[+] Port {port}")
        else:
            self.ui.freePortsText.append("No ports are.")


    # function for getting the own IP Address
    def showOwnIP(self):
        # getting device name
        hostname = socket.gethostname()

        # getting IP from device name
        local_ip = socket.gethostbyname(hostname)

        self.ui.ipAddressText.setText(local_ip)

        # testprint in console
        print(local_ip)



"""
-> Initializing QT Application
-> open the main window
-> starting an loop for user interaction
-> waiting until app is getting closed and close the program
"""
def main():
    # creating a QT instance with commands for the application
    app = QApplication(sys.argv)

    # creating an object of the windows class as a invisible python object
    window = MainApp()

    # setting the windows visible
    window.show()

    # app.exec -> starting an infinitive loop which waits for user interaction
    sys.exit(app.exec())


if __name__ == "__main__":
    main()