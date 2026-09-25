from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThreadPool
import traceback
import sys
import time


class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()

class ProgressDialog(QDialog):
    def __init__(self, *args, **kwargs): # 이 때, 이미 self는 Child instance임. 만약 Child의 __init__이 명시되지 않았다면 이게 호출됨
        super().__init__()
        self.args = args
        self.kwargs = kwargs
        self.worker = None
        self.msg = None
        self.init_ui()

        
    def init_ui(self):
        layout = QVBoxLayout()
        self.setWindowTitle("Limit Checker")
        self.resize(400, 80)
        icon = QIcon("./lg_logo.ico")
        self.setWindowIcon(icon)
        self.ok_button = QPushButton("Execute", self)
        self.ok_button.clicked.connect(self.execute)
        self.setLayout(layout)

    def execute(self):
        self.threadpool = QThreadPool()
        self.worker = Worker(self.excute_this_fn, *self.args, **self.kwargs)
        self.worker.signals.result.connect(self.print_output)
        self.worker.signals.error.connect(self.except_handler)
        self.threadpool.start(self.worker)

    def excute_this_fn(self, progress_callback, progress_type):
        for i in range(100):
            time.sleep(0.1)
            progress_callback.emit(i + 1)

    def except_handler(self, frame):
        self.msg = str(frame[1])
        QApplication.quit()


    def thread_complete(self):
        if self.msg:
            QMessageBox.critical(self, "error", self.msg,
                                 buttons=QMessageBox.Abort)
            self.reject()
        else:
            self.accept()

    def print_output(self, s):
        self.msg = s
