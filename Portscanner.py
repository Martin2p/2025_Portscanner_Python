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

Date: June 2025

"""
import sys
import os
import socket

from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QMainWindow

from ui_portscanner_gui import Ui_MainWindow


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller temporärer Ordner
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # window size
        self.resize(640, 480)

        # getting the path! to the built GUI (done with QT)
        ui_path = os.path.abspath("portscanner_gui.ui")
        print(f"Loading UI-File from: {ui_path}")
        

        # open UI-File as QFile
        file = QFile(ui_path)
        if not file.open(QFile.ReadOnly):
            raise RuntimeError(f"Can not open UI-file at: {ui_path}")


        # Version 1:
        # QUiLoader load UI-File on runtime
        """
        loader = QUiLoader()
        self.ui = loader.load(file, self)
        file.close()

        if not self.ui:
            raise RuntimeError("unable to load the UI")
            
        # setting central widget in main window
        self.setCentralWidget(self.ui)
        """

        # Version 2:
        # if the GUI look is finished
        """
        in terminal: pyuic5 portscanner_gui.ui -o ui_portscanner_gui.py
        
        then:
        from ui_portscanner_gui import Ui_MainWindow
            """

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