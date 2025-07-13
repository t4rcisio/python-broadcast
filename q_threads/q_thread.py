# -*- coding: utf-8 -*-
import time
from PyQt6.QtCore import QObject, QThread, pyqtSignal
from PyQt6.QtWidgets import QMainWindow
from multiprocessing import Process


class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def setParams(self,params):

        self.params = params

    def run(self):


        try:

            fx = self.params["FX"]
            data = self.params["DATA"]

            if data is None:
                self.process = Process(target=fx)
            else:
                self.process = Process(target=fx, args=(data,))

            self.process.start()
        except:
            self.progress.emit(1)
            self.finished.emit()
            return


        while self.process.is_alive():

            time.sleep(1)
            self.progress.emit(1)

        self.finished.emit()


class ThreadService(QMainWindow):

    def end(self):

        self.endApp()

    def runUpdate(self):

        print("running")


    def startThread(self, params, beginApp, endApp, update=False):

        self.thread = QThread()

        self.beginApp = beginApp
        self.endApp = endApp

        self.tempCount = 0

        self.update = update


        self.worker = Worker()
        self.worker.setParams(params)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        if self.update:
            self.worker.progress.connect(self.update)

        self.beginApp()
        self.thread.start()
        self.thread.finished.connect(self.end)