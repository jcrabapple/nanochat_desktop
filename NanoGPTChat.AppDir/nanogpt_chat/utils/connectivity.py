import socket
import threading
import time
from PyQt6.QtCore import QObject, pyqtSignal

class ConnectivityMonitor(QObject):
    status_changed = pyqtSignal(bool)
    
    def __init__(self, host="8.8.8.8", port=53, interval=10):
        super().__init__()
        self.host = host
        self.port = port
        self.interval = interval
        self.is_online = True
        self._running = False
        
    def check_connection(self):
        try:
            socket.setdefaulttimeout(3)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((self.host, self.port))
            return True
        except socket.error:
            return False
            
    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        
    def stop(self):
        self._running = False
        
    def _run(self):
        while self._running:
            online = self.check_connection()
            if online != self.is_online:
                self.is_online = online
                self.status_changed.emit(online)
            time.sleep(self.interval)

# Global monitor instance
monitor = ConnectivityMonitor()
