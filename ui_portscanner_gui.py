# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'portscanner_gui.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QLabel, QMainWindow, QMenuBar,
    QPushButton, QRadioButton, QSizePolicy, QStatusBar,
    QTextEdit, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(640, 480)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.localHostsText = QTextEdit(self.centralwidget)
        self.localHostsText.setObjectName(u"localHostsText")
        self.localHostsText.setGeometry(QRect(270, 150, 291, 131))
        self.openPortsText = QTextEdit(self.centralwidget)
        self.openPortsText.setObjectName(u"openPortsText")
        self.openPortsText.setGeometry(QRect(10, 310, 131, 51))
        self.ipAddressText = QTextEdit(self.centralwidget)
        self.ipAddressText.setObjectName(u"ipAddressText")
        self.ipAddressText.setGeometry(QRect(10, 40, 131, 51))
        self.freePortsText = QTextEdit(self.centralwidget)
        self.freePortsText.setObjectName(u"freePortsText")
        self.freePortsText.setGeometry(QRect(10, 190, 131, 51))
        self.myIPBtn = QPushButton(self.centralwidget)
        self.myIPBtn.setObjectName(u"myIPBtn")
        self.myIPBtn.setGeometry(QRect(10, 100, 131, 26))
        self.freeBtn = QPushButton(self.centralwidget)
        self.freeBtn.setObjectName(u"freeBtn")
        self.freeBtn.setGeometry(QRect(10, 250, 131, 26))
        self.openPortsBtn = QPushButton(self.centralwidget)
        self.openPortsBtn.setObjectName(u"openPortsBtn")
        self.openPortsBtn.setGeometry(QRect(10, 370, 131, 26))
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(230, 10, 161, 31))
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.label.setFont(font)
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(290, 70, 201, 18))
        self.radioButton = QRadioButton(self.centralwidget)
        self.radioButton.setObjectName(u"radioButton")
        self.radioButton.setGeometry(QRect(280, 100, 95, 22))
        self.radioButton_2 = QRadioButton(self.centralwidget)
        self.radioButton_2.setObjectName(u"radioButton_2")
        self.radioButton_2.setGeometry(QRect(390, 100, 161, 22))
        self.clearBtn = QPushButton(self.centralwidget)
        self.clearBtn.setObjectName(u"clearBtn")
        self.clearBtn.setGeometry(QRect(340, 400, 131, 26))
        self.closeBtn = QPushButton(self.centralwidget)
        self.closeBtn.setObjectName(u"closeBtn")
        self.closeBtn.setGeometry(QRect(500, 400, 131, 26))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 640, 24))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.myIPBtn.setText(QCoreApplication.translate("MainWindow", u"show my IP Address", None))
        self.freeBtn.setText(QCoreApplication.translate("MainWindow", u"show free Ports", None))
        self.openPortsBtn.setText(QCoreApplication.translate("MainWindow", u"show open Ports", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Portscanner", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Scan local network for hosts", None))
        self.radioButton.setText(QCoreApplication.translate("MainWindow", u"with DNS", None))
        self.radioButton_2.setText(QCoreApplication.translate("MainWindow", u"with ARP Table", None))
        self.clearBtn.setText(QCoreApplication.translate("MainWindow", u"Clear all", None))
        self.closeBtn.setText(QCoreApplication.translate("MainWindow", u"Close", None))
    # retranslateUi

