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
import sys, os, socket
import subprocess
import platform
import ipaddress
import threading

from PyQt6.QtCore import QThread, pyqtSignal
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
        base_path = sys._MEIPASS  # PyInstaller temporary Folder
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
class NetworkScanner(QThread):

    # starting a own process
    progress = pyqtSignal(int)
    finished = pyqtSignal(list)

    def __init__(self, mode="ping", network="192.168.1.0/24", stop_event=None):
        super().__init__()  # calling QThread-constructor
        self.network = network
        self.mode = mode
        self.stop_event = stop_event or threading.Event()
        self.ping_thread = None
        self.found_hosts = []

    def run(self):
        hosts = []

        if self.mode == "ping":
            hosts = self.scan_with_ping()
        elif self.mode == "dns":
            hosts = self.scan_with_dns()
        elif self.mode == "arp":
            hosts = self.scan_with_arp()

        self.finished.emit(hosts)

    # 1) Ping-Scan can not good work with Stop
    def scan_with_ping(self):

        # Reset before starting
        if hasattr(self, 'ping_thread') and self.ping_thread is not None:
            self.ping_thread.stop_event.set()

        try:
            all_ips = list(ipaddress.IPv4Network(self.network, strict=False))
            total = len(all_ips) or 1
            is_win = platform.system().lower().startswith("win")

            for i, ip in enumerate(all_ips, start=1):
                if self.stop_event.is_set():
                    break

                ip = str(ip)
                cmd = ["ping", "-n" if is_win else "-c", "1", ip]
                if is_win:
                    cmd += ["-w", "300"]  # 300 ms Timeout unter Windows

                try:
                    subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
                    self.found_hosts.append(ip)
                except subprocess.CalledProcessError:
                    pass

                self.progress.emit(int(i / total * 100))
        except Exception as e:
            print(f"Ping scan error: {e}")


    # 2) DNS Scan
    def scan_with_dns(self):
        if self.stop_event.is_set():
            return []

        results = []

        try:
            all_ips = list(ipaddress.IPv4Network(self.network, strict=False))
            total = len(all_ips) or 1

            for i, ip in enumerate(all_ips, start=1):
                if self.stop_event.is_set():
                    break

                try:
                    host = socket.gethostbyaddr(str(ip))[0]  # Reverse DNS
                    results.append(f"{host}: {ip}")
                except socket.herror:
                    results.append(f"{ip}: no hostname")

                self.progress.emit(int(i / total * 100))

        except Exception as e:
            print(f"DNS scan error: {e}")

        return results

    # 3) ARP Scan
    def scan_with_arp(self):
        if self.stop_event.is_set():
            return []

        if not SCAPY_AVAILABLE:
            return []

        try:
            arp = ARP(pdst=self.network)
            ether = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = ether / arp
            result = srp(packet, timeout=2, verbose=0)[0]

            devices = []
            for _, received in result:
                ip = received.psrc
                mac = received.hwsrc
                # optional: versuche Hostname per socket.gethostbyaddr()
                try:
                    hostname = socket.gethostbyaddr(ip)[0]
                except socket.herror:
                    hostname = "unknown"
                devices.append({"ip": ip, "mac": mac, "hostname": hostname})
            return devices
        except PermissionError:
            return []  # falls kein Admin

        except Exception as e:
            print(f"ARP Scan Error: {e}")
            return []

    # own stop-Event
    def stop(self):
        self.stop_event = threading.Event()



# Scanner for open Ports for anit freezing window
class OpenPortsScanner(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(list)

    # function scanning open ports on local host
    def __init__(self,  host="127.0.0.1", start=1, end=1024, timeout=0.5):
        super().__init__()
        self.host = host
        self.start_port = start
        self.end_port = end
        self.timeout = timeout
        self.stop_event = threading.Event()

    def run(self):
        open_ports = []

        for port in range(self.start_port, self.end_port + 1):
            # check for stop is called
            if self.stop_event.is_set():
                break
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self.timeout)
                result = s.connect_ex((self.host, port))
                if result == 0:
                    open_ports.append(port)
            progress = int((port - self.start_port) / (self.end_port - self.start_port) * 100)
            self.progress.emit(progress)

        self.finished.emit(open_ports)

    # own stop-Event
    def stop(self):
        self.stop_event = threading.Event()



# Scanner for open Ports for anit freezing window
class FreePortsScanner(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(list)

    def __init__(self, start=1, end=65535):
        super().__init__()
        self.start_port = start
        self.end_port = end
        self.stop_event = threading.Event()

    def run(self):
        free_ports = []
        total_ports = self.end_port - self.start_port + 1

        for idx, port in enumerate(range(self.start_port, self.end_port + 1), start=1):

            # check for stop is called
            if self.stop_event.is_set():
                break

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.01)
                try:
                    s.bind(("", port))  # if its possible -> Port is free
                    free_ports.append(port)
                except OSError:
                    pass  # Port not free

            self.progress.emit(int((idx / total_ports) * 100))

        self.finished.emit(free_ports)

    # own stop-Event
    def stop(self):
        self.stop_event = threading.Event()

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

        # List for Threads
        self.threads = []

        self.thread = None

        # Stop-Event global for all Threads
        self.stop_event = threading.Event()

        # Button Events:
        # laying function on close Button
        self.ui.closeBtn.clicked.connect(self.close)

        # calling method for clear fields
        self.ui.clearBtn.clicked.connect(self.clear_fields)

        # calling method for getting the own IP Address
        self.ui.myIPBtn.clicked.connect(self.show_own_ip)

        # calling method for getting open Ports on the system
        self.ui.freeBtn.clicked.connect(self.show_free_ports)
        self.ui.progressBarFree.setMaximum(100)

        # calling method for getting open Ports on the system
        self.ui.openPortsBtn.clicked.connect(self.show_open_ports)
        self.ui.progressBarOpen.setMaximum(100)

        # calling method for getting local hosts on the network
        self.ui.hostsBtn.clicked.connect(self.show_local_hosts)
        self.ui.progressBarHosts.setMaximum(100)

        # calling method for stopping search
        self.ui.stopBtn.clicked.connect(self.stop_all_threads)

        self.free_ports_thread = None
        self.open_ports_thread = None

    # function for reset/cleaning fields
    def clear_fields(self):
        self.ui.localHostsText.clear()
        self.ui.progressBarHosts.setValue(0)
        self.ui.freePortsText.clear()
        self.ui.progressBarFree.setValue(0)
        self.ui.openPortsText.clear()
        self.ui.progressBarOpen.setValue(0)
        self.ui.ipAddressText.clear()


    # function for stopping
    def stop_all_threads(self):
        self.ui.stopBtn.setEnabled(False)
        self.stop_event.set()

        # test for stop on Open Ports Test
        if hasattr(self, "open_ports_thread") and self.open_ports_thread is not None:
            if self.open_ports_thread.isRunning():
                self.open_ports_thread.stop_event.set()
            self.open_ports_thread = None
            self.ui.stopBtn.setEnabled(True)

        # test for stop on Free Ports Test
        if hasattr(self, "free_ports_thread") and self.free_ports_thread is not None:
            if self.free_ports_thread.isRunning():
                self.free_ports_thread.stop_event.set()
            self.free_ports_thread = None
            self.ui.stopBtn.setEnabled(True)


    # function for getting free ports
    def show_free_ports(self):

        self.ui.freeBtn.setEnabled(False)
        self.ui.freePortsText.setText(f"Scanning")

        self.free_ports_thread = FreePortsScanner()
        self.free_ports_thread.progress.connect(self.ui.progressBarFree.setValue)
        self.free_ports_thread.finished.connect(lambda ports, t=self.free_ports_thread: self.scan_free_finished(ports, t))
        self.free_ports_thread.start()


    # function for getting open ports on the system
    def show_open_ports(self):
        self.ui.openPortsBtn.setEnabled(False)
        self.ui.openPortsText.setText(f"Scanning...")

        self.open_ports_thread = OpenPortsScanner()
        self.open_ports_thread.progress.connect(self.ui.progressBarOpen.setValue)
        self.open_ports_thread.finished.connect(lambda ports,  t=self.open_ports_thread: self.scan_open_finished(ports, t))
        self.open_ports_thread.start()


    # function finish open ports
    def scan_open_finished(self,open_ports, thread):
        self.ui.openPortsBtn.setEnabled(True)
        if open_ports:
            self.ui.openPortsText.append("Open ports on your system:")
            for port in open_ports:
                self.ui.openPortsText.append(f"[+] Port {port}")
        else:
            self.ui.openPortsText.append("No open ports found.")
        thread.deleteLater()
        if hasattr(self, 'free_ports_thread') and self.free_ports_thread == thread:
            self.open_ports_thread = None

    # function finish free ports
    def scan_free_finished(self, free_ports, thread):
        self.ui.freeBtn.setEnabled(True)
        if free_ports:
            self.ui.freePortsText.append("Free ports on your system:")
            for port in free_ports:
                self.ui.freePortsText.append(f"[+] Port {port}")
        else:
            self.ui.freePortsText.append("No free ports found.")
        thread.deleteLater()
        if hasattr(self, 'free_ports_thread') and self.free_ports_thread == thread:
            self.free_ports_thread = None


    # function for getting the own IP Address
    def show_own_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Verbindung ins Internet simulieren (keine Daten werden gesendet)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
        self.ui.ipAddressText.setText(ip)


    # function for getting local IPs
    def show_local_hosts(self):
        self.ui.hostsBtn.setEnabled(False)
        self.ui.localHostsText.setText("Scanning...")

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
            self.thread = NetworkScanner(mode=mode, network="192.168.1.0/24", stop_event=self.stop_event)
            self.thread.progress.connect(self.ui.progressBarHosts.setValue)
            self.thread.finished.connect(self.scan_hosts_finished)
            self.thread.start()
        else:
            self.ui.localHostsText.setText("Please choose a Scan-Methode.")
            self.ui.hostsBtn.setEnabled(True)

        """
        -> Stop Event???
        
        """


    # results in a separate methode
    def scan_hosts_finished(self, hosts):
        self.ui.hostsBtn.setEnabled(True)
        self.ui.stopBtn.setEnabled(True)
        self.stop_event.clear()

        if not hosts:
            self.ui.localHostsText.setText("No Hosts found.")
            return

        # ARP Results
        if isinstance(hosts[0], dict):
            text = ""
            for d in hosts:
                text += f"{d['hostname']}:\n{'-' * len(d['hostname'])}\n{d['mac']} | {d['ip']}\n\n"

        # Ping or DNS results
        elif isinstance(hosts[0], str):
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

    try:
        # creating an object of the windows class as a invisible python object
        window = MainApp()
        # setting the windows visible
        window.show()
    except Exception as e:
        print("Fehler beim Start:", e)
        raise

    # app.exec -> starting an infinitive loop which waits for user interaction
    sys.exit(app.exec())


if __name__ == "__main__":
    main()