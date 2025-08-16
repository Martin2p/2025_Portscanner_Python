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

Date: August 2025

"""
import sys, os, socket, time
import subprocess
import platform
import ipaddress

from PyQt6.QtCore import QThread, pyqtSignal, QFile
from PyQt6.QtWidgets import QApplication, QMainWindow
from click import command

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

# Tool for ARP Table scan
try:
    from scapy.all import ARP, Ether, srp
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False


# Scanner-class for Network-scan
class networkScanner(QThread):

    # starting a own process
    progress = pyqtSignal(int)
    finished = pyqtSignal(list)


    def __init__(self, mode="ping", network="192.168.1.0/24"):
        super().__init__()  # calling QThread-constructor
        self.network = network
        self.mode = mode


    def run(self):
        hosts = []

        if self.mode == "ping":
            hosts = self.scan_with_ping()
        elif self.mode == "dns":
            hosts = self.scan_with_dns()
        elif self.mode == "arp":
            hosts = self.scan_with_arp()

        self.finished.emit(hosts)

    # 1) Ping-Scan
    def scan_with_ping(self):
        hosts_up = []
        all_ips = list(ipaddress.IPv4Network(self.network, strict=False))
        total = len(all_ips)

        for i, ip in enumerate(all_ips, start=1):
            ip = str(ip)
            param = "-n" if platform.system().lower() == "windows" else "-c"
            command = ["ping", param, "1", ip]
            try:
                subprocess.check_output(command, stderr=subprocess.DEVNULL)
                hosts_up.append(ip)
            except subprocess.CalledProcessError:
                pass

            # Fortschritt berechnen und senden
            self.progress.emit(int(i / total * 100))

        return hosts_up

    # 2) DNS Scan
    def scan_with_dns(self, hostnames=None):
        if hostnames is None:
            hostnames = ["raspberrypi", "printer", "pc01"]

        results = {}
        for host in hostnames:
            try:
                ip = socket.gethostbyname(host)
                results.append(f"{host}: {ip}")
            except socket.gaierror:
                results.append(f"{host}: not found")
        return results

    # 3) ARP Scan
    def scan_with_arp(self):
        if not SCAPY_AVAILABLE:
            return []

        try:
            arp = ARP(pdst=self.network)
            ether = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = ether / arp
            result = srp(packet, timeout=2, verbose=0)[0]

            devices = []
            for _, received in result:
                devices.append({'ip': received.psrc, 'mac': received.hwsrc})
            return devices
        except PermissionError:
            return []  # falls kein Admin
        except Exception as e:
            print(f"ARP Scan Error: {e}")
        return []


# Scanner for open Ports for anit freezing window
class openPortsScanner(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(list)

    # function scanning open ports on local host
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

        # creating instance of Networkscanner
        #self.scanner = networkScanner(mode="ping", network="192.168.1.0/24")

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
        # laying function on close Button
        self.ui.closeBtn.clicked.connect(self.close)

        # calling method for clear fields
        self.ui.clearBtn.clicked.connect(self.clearFields)

        # calling method for getting the own IP Address
        self.ui.myIPBtn.clicked.connect(self.showOwnIP)

        # calling method for getting open Ports on the system
        self.ui.freeBtn.clicked.connect(self.showFreePorts)
        self.ui.progressBarFree.setMaximum(100)

        # calling method for getting open Ports on the system
        self.ui.openPortsBtn.clicked.connect(self.showOpenPorts)
        self.ui.progressBarOpen.setMaximum(100)

        # calling method for getting local hosts on the network
        self.ui.hostsBtn.clicked.connect(self.showLocalHosts)
        self.ui.progressBarHosts.setMaximum(100)

    # function for reset/cleaning fields
    def clearFields(self):
        self.ui.localHostsText.clear()
        self.ui.progressBarHosts.setValue(0)
        self.ui.freePortsText.clear()
        self.ui.progressBarFree.setValue(0)
        self.ui.openPortsText.clear()
        self.ui.progressBarOpen.setValue(0)

        self.ui.ipAddressText.clear()

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
            self.ui.openPortsText.append("Open ports on your system:")
            for port in open_ports:
                self.ui.openPortsText.append(f"[+] Port {port}")
        else:
            self.ui.openPortsText.append("No open ports found.")


    # function finish free ports
    def scan_free_finished(self, open_ports):
        self.ui.freeBtn.setEnabled(True)
        if open_ports:
            self.ui.freePortsText.append("Free ports on your system:")
            for port in open_ports:
                self.ui.freePortsText.append(f"[+] Port {port}")
        else:
            self.ui.freePortsText.append("No free ports found.")


    # function for getting the own IP Address
    def showOwnIP(self):
        # getting device name
        hostname = socket.gethostname()

        # getting IP from device name
        local_ip = socket.gethostbyname(hostname)

        self.ui.ipAddressText.setText(local_ip)

        # testprint in console
        print(local_ip)

    # function for getting local IPs
    def showLocalHosts(self):
        self.ui.hostsBtn.setEnabled(False)
        self.ui.localHostsText.setText(f"Scanning...")

        if self.ui.rBtnPing.isChecked():
            mode = "ping"
        elif self.ui.rBtnDNS.isChecked():
            mode = "dns"
        elif self.ui.rBtnARP.isChecked():
            mode = "arp"
        else:
            mode = None

        if mode:
            # Thread starten
            self.thread = networkScanner(mode=mode, network="192.168.1.0/24")
            self.thread.progress.connect(self.ui.progressBarHosts.setValue)
            self.thread.finished.connect(self.scan_hosts_finished)
            self.thread.start()
        else:
            self.ui.localHostsText.setText("Please choose a Scan-Methode.")
            self.ui.hostsBtn.setEnabled(True)

    # results in a separate methode
    def scan_hosts_finished(self, hosts):
        self.ui.hostsBtn.setEnabled(True)
        if not hosts:
            self.ui.localHostsText.setText("No Hosts found.")
            return

        if isinstance(hosts[0], dict):  # ARP Ergebnis (Liste von Dicts)
            text = "\n".join(f"{d['ip']} ({d['mac']})" for d in hosts)
        elif isinstance(hosts[0], str):  # Ping oder DNS Ergebnis (Liste von Strings)
            text = "\n".join(hosts)
        else:
            text = str(hosts)

        self.ui.localHostsText.setText(text)

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