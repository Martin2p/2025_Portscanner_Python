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
"""
import sys
import os
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication

def resource_path(relative_path):
    """Ermittelt den absoluten Pfad zur Ressource, auch wenn das Programm als EXE läuft."""
    try:
        base_path = sys._MEIPASS  # PyInstaller temporärer Ordner
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()

        ui_path = resource_path("portscanner_gui.ui")

        file = QFile(ui_path)
        if not file.open(QFile.ReadOnly):
            raise RuntimeError(f"Kann UI-Datei nicht öffnen: {ui_path}")

        loader = QUiLoader()
        self.ui = loader.load(file, self)
        file.close()

        if not self.ui:
            raise RuntimeError("UI konnte nicht geladen werden")

        self.setCentralWidget(self.ui)
        self.ui.pushButton.clicked.connect(self.close)


def main():
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
