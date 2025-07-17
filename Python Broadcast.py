import os.path
import shutil
import sys
import traceback
import webbrowser
from datetime import datetime

import pymsgbox
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtCore import QFileSystemWatcher, Qt
from PyQt6.QtGui import QMovie, QIcon
from PyQt6.QtWidgets import QFileDialog

from pages import home_page, app_widget
from q_threads import q_thread
from services import database, security, build_app, install_app, start_app


APP_ICON = ".\\sources\\app.png"

class App:

    def __init__(self):

        self.storage = database.Storage()
        self.config = self.storage.config()

        if not isinstance(self.config, dict):
            self.config = {}
            self.storage.config({})


    def run(self):

        try:

            self.app = QtWidgets.QApplication(sys.argv)
            self.homePage = home_page.Ui_Form()

            self.Form = QtWidgets.QWidget()
            self.homePage.setupUi(self.Form)

            self.connections()

            icon2 = QtGui.QIcon()
            icon2.addPixmap(QtGui.QPixmap(APP_ICON), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
            self.Form.setWindowIcon(icon2)
            self.Form.setWindowTitle("PYTHON BROADCAST")
            self.Form.show()

            try:
                sys.exit(self.app.exec())
            except:
                pass

        except:
            pymsgbox.alert(traceback.format_exc(), "ERROR")

    def connections(self):

        self.config = self.storage.config()
        if not isinstance(self.config, dict):
            self.config = {}
            self.storage.config({})


        self.homePage.generateBtn.clicked.connect(lambda state: self.__generateKeys())

        self.homePage.private_rsa.mousePressEvent = lambda state: self.__importRSA("RSA_PRIV_PATH")
        self.homePage.public_rsa.mousePressEvent = lambda state: self.__importRSA("RSA_PUB_PATH")

        self.homePage.exportBtn.clicked.connect(lambda state: self.__exportRSA())

        self.homePage.private_rsa.setReadOnly(True)
        self.homePage.public_rsa.setReadOnly(True)

        self.homePage.selectApp.currentIndexChanged.connect(lambda index: self.__projectForm(index))

        self.homePage.appFolder.mousePressEvent = lambda state: self.__get_folder_file(self.homePage.appFolder)
        self.homePage.outputFolder.mousePressEvent = lambda state: self.__get_folder_file(self.homePage.outputFolder)

        self.homePage.buildBtn.clicked.connect(lambda state: self.__buildProject())

        self.homePage.path_input.mousePressEvent = lambda state: self.__get_folder_file(self.homePage.path_input, file=True, filter="File BIN (*.bin);")
        self.homePage.path_input.setReadOnly(True)

        self.homePage.installButton.clicked.connect(lambda state: self.__install_app())

        self.homePage.gitBtn.clicked.connect(lambda state:webbrowser.open('https://github.com/t4rcisio'))
        self.homePage.linkBtn.clicked.connect(lambda state:webbrowser.open('https://www.linkedin.com/in/t4rcisio/'))

        self.homePage.appFolder.setReadOnly(True)
        self.homePage.outputFolder.setReadOnly(True)
        self.homePage.plainTextEdit.setReadOnly(True)

        self.watcher = QFileSystemWatcher([self.storage.logFile])
        self.watcher.fileChanged.connect(self.__update)

        self.watcher_log = QFileSystemWatcher([self.storage.codeLog])
        self.watcher_log.fileChanged.connect(self.updateLog)

        self.storage.logs("------> PYTHON BROADCAST EVENTS\n\n")
        self.storage.code_log("------> PYTHON BROADCAST LOG\n\n")

        self.is_running = False

        self.__init_form()

    def __init_form(self):

        if 'RSA_PUB_PATH' in self.config:
            self.homePage.public_rsa.setText(self.__rsaText(self.config['RSA_PUB_PATH']))
        else:
            self.config['RSA_PUB_PATH'] = False

        if 'RSA_PRIV_PATH' in self.config:
            self.homePage.private_rsa.setText(self.__rsaText(self.config['RSA_PRIV_PATH']))
        else:
            self.config['RSA_PRIV_PATH'] = False

        self.homePage.public_rsa.setCursorPosition(0)
        self.homePage.private_rsa.setCursorPosition(0)


        self.projects = self.storage.projects()
        self.process = []
        self.process_running = {}

        if not isinstance(self.projects, dict):
            self.projects = {}

        self.homePage.selectApp.clear()
        self.homePage.selectApp.addItems(["SELECT", "NEW"] + list(self.projects.keys()))

        self.__projectForm(0)
        self.loadApps()
        self.__loadingPage()

    def __loadingPage(self):

        gif_label = QtWidgets.QLabel()
        movie = QMovie(".\\sources\\loading.gif")  # ex: "loading.gif"
        movie.setScaledSize(QtCore.QSize(40,40))
        gif_label.setMovie(movie)
        gif_label.setFixedSize(50,50)

        movie.start()

        self.text_label = QtWidgets.QLabel()
        self.text_label.setFixedHeight(50)
        self.text_label.setText('<html><head/><body><p><span style=" font-size:12pt; font-weight:600; color:#ffffff;">INSTALLED APPS</span></p></body></html>')

        self.homePage.horizontalLayout_4.addWidget(gif_label)
        self.homePage.horizontalLayout_4.addWidget(self.text_label)
        self.homePage.widget_11.setVisible(False)

    def loadApps(self):

        self.apps = self.storage.apps()

        self.clear_layout(self.homePage.verticalLayout_21)

        if not isinstance(self.apps, dict):
            self.apps = {}
            self.storage.apps({})

        self.appList = []

        self.homePage.scrollArea.setWidgetResizable(True)
        self.homePage.verticalLayout_21.setAlignment(Qt.AlignmentFlag.AlignTop)

        for app_name in self.apps:

            if os.path.exists(self.apps[app_name]['path']):

                appWidget = app_widget.Ui_Form()
                widget = QtWidgets.QWidget()
                appWidget.setupUi(widget)

                appWidget.app_name.setText('<html><head/><body><p align="center"><span style=" font-size:11pt; font-weight:600; color:#ffffff;">'+str(app_name)+'</span></p></body></html>')

                app_icon = QtGui.QIcon()
                app_icon.addPixmap(QtGui.QPixmap(self.apps[app_name]['icon']), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
                appWidget.icon_app.setIcon(app_icon)

                appWidget.run_btn.clicked.connect(lambda state, script=app_name: self.__run_app(script))
                appWidget.delete_btn.clicked.connect(lambda state, script=app_name: self.__remove_app(script))
                appWidget.info_btn.clicked.connect(lambda state, script=app_name: self.__info_app(script))
                if "app_color" in self.apps[app_name]:
                    appWidget.widget_20.setStyleSheet(f"background-color: {self.apps[app_name]['app_color']};")

                self.homePage.verticalLayout_21.addWidget(widget)

    def clear_layout(self, layout):
        while layout.count() > 0:
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                if item.layout() is not None:
                    self.clear_layout(item.layout())

    def __run_app(self, app_name):

        self.process.append({
            "CLASSE": start_app.StartApp(),
            "TH": q_thread.ThreadService()
        })

        params = {
            "app_name": app_name,
        }

        payload = {
            "FX": self.process[-1]["CLASSE"].run,
            "DATA": params
        }

        self.process[-1]["TH"].startThread(payload, self.__start, self.__end, self.__update)
        self.storage.projects(self.projects)


    def __msgQuestion(self, title, text):

        msg_box = QtWidgets.QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        icon = QIcon(APP_ICON)
        msg_box.setWindowIcon(icon)
        msg_box.setStandardButtons(
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
        msg_box.setStyleSheet(
            "color: white; background-color: rgb(237, 86, 88); font-size: 16px; font-weight: bold;")

        reply = msg_box.exec()

        return True if reply == QtWidgets.QMessageBox.StandardButton.Yes else False

    def __remove_app(self, name):

        self.apps = self.storage.apps()

        reply = self.__msgQuestion("ALERT", "DO YOU WANT TO REMOVE THIS APP?")

        if reply:

            try:
                shutil.rmtree(self.apps[name]['path'])
                pymsgbox.alert("REMOVED SUCCESSFULLY", "NOTICE")
                self.loadApps()
            except:
                pymsgbox.alert("APP REMOVED SUCCESSFULLY", "NOTICE")
                self.storage.code_log(f"\n\n------------------------DATE:{datetime.now().strftime('%d.%m.%y %H:%M:%S')}\nCONTENT:{traceback.format_exc()}")

    def __info_app(self, name):

        self.apps = self.storage.apps()
        text = f"APP NAME: {name}\nVERSION: {self.apps[name]['version']}\nAUTHOR: {self.apps[name]['author']}\nDIR: {self.apps[name]['path']}"
        pymsgbox.alert(text, "INFO")

    def __install_app(self):

        if not os.path.exists(self.homePage.path_input.text()):
            pymsgbox.alert("Select path to app", "ERROR")
            return

        if not self.config['RSA_PRIV_PATH']:
            pymsgbox.alert("RSA builder not found", "ERROR")
            return

        params = {
            "APP_PATH": self.homePage.path_input.text(),
            "RSA_PRIV_PATH": self.config['RSA_PRIV_PATH'],
        }

        if "" in list(params.values()):
            pymsgbox.alert("COMPLETE ALL FIELDS", "ERROR")
            return

        self.process.append({
            "CLASSE": install_app.InstallApp(),
            "TH": q_thread.ThreadService()
        })

        payload = {
            "FX": self.process[-1]["CLASSE"].run,
            "DATA": params
        }

        self.is_running = "INSTALL"

        self.process[-1]["TH"].startThread(payload, self.__start, self.__end, self.__update)
        self.storage.projects(self.projects)


    def __buildProject(self):


        if self.is_running:
            pymsgbox.alert("Already proccess is running", "ERROR")
            return

        if not 'RSA_PUB_PATH' in self.config:
            pymsgbox.alert("RSA PUB not found", "ERROR")
            return

        appName = self.homePage.appName.text()

        if not self.homePage.python_mode.isChecked() and not self.homePage.p_compile_mode.isChecked():
            pymsgbox.alert("Select compile mode", "ERROR")
            return

        if not os.path.exists(self.homePage.appFolder.text()):
            pymsgbox.alert("Select project folder", "ERROR")
            return

        if not os.path.exists(self.homePage.outputFolder.text()):
            pymsgbox.alert("Select output folder", "ERROR")
            return

        if not self.config['RSA_PUB_PATH']:
            pymsgbox.alert("RSA builder not found", "ERROR")
            return

        comp_mode = "PYTHON"
        if self.homePage.p_compile_mode.isChecked():
            comp_mode = "PRECOMPILE"




        params = {
            "APP_NAME": appName,
            "SOURCE_PATH": self.homePage.appFolder.text(),
            "OUTPUT_BIN": self.homePage.outputFolder.text(),
            "RSA_PUB_PATH": self.config['RSA_PUB_PATH'],
            "TEMP_ZIP_PATH": self.storage.root + "\\temp_.zip",
            "COMPILE_MODE": comp_mode
        }

        self.projects[appName] = params

        if "" in list(params.values()):
            pymsgbox.alert("COMPLETE ALL FIELDS", "ERROR")
            return

        self.process.append({
            "CLASSE": build_app.BuildApp(),
            "TH": q_thread.ThreadService()
        })

        payload = {
            "FX": self.process[-1]["CLASSE"].build,
            "DATA": params
        }

        self.is_running = "BUILD"

        self.process[-1]["TH"].startThread(payload, self.__start, self.__end, self.__update)
        self.storage.projects(self.projects)


    def __start(self):
        if self.is_running == "INSTALL":
            self.homePage.widget_11.setVisible(True)

        self.storage.logs("")
        self.__updateText('STARTING')


    def __update(self):

        logs = self.storage.logs()
        if self.is_running == "INSTALL":
            text = logs.split("\n")[-1].split('>')[-1].strip()
            self.text_label.setText('<html><head/><body><p><span style=" font-size:12pt; font-weight:600; color:#ffffff;">'+text+'</span></p></body></html>')
        else:
            self.homePage.plainTextEdit.setPlainText(logs)

    def __end(self):

        if self.is_running == "INSTALL":
            self.homePage.widget_11.setVisible(False)

        self.is_running = False
        self.__updateText('COMPLETED')
        self.__update()
        self.loadApps()

    def updateLog(self):

        code_log = self.storage.code_log()
        self.homePage.logsText.setPlainText(code_log)


    def __updateText(self, text):

        logs = self.storage.logs()
        if logs != None:
            logs += "\n"+ str(datetime.now().strftime("%d.%m.%y %H:%M:%S")) + "\t------> "+str(text)
            self.storage.logs(logs)

    def __projectForm(self, index):

        state = index if index <=1 else True
        self.__projectForm_state(state)

        if index > 1:

            refKey = self.homePage.selectApp.currentText()

            self.homePage.appName.setText(self.projects[refKey]["APP_NAME"])

            self.homePage.appFolder.setText(self.projects[refKey]["SOURCE_PATH"])

            self.homePage.outputFolder.setText(self.projects[refKey]["OUTPUT_BIN"])

            if self.projects[refKey]["COMPILE_MODE"] == "PYTHON":
                self.homePage.python_mode.setChecked(True)
            else:
                self.homePage.p_compile_mode.setChecked(True)

            print(refKey, "SCRIPT LOADED SUCCESSFULLY")



    def __projectForm_state(self, state):

        self.homePage.appName.setEnabled(state)
        self.homePage.appName.setText("")

        self.homePage.appFolder.setEnabled(state)
        self.homePage.appFolder.setText("")

        self.homePage.outputFolder.setEnabled(state)
        self.homePage.outputFolder.setText("")

        self.homePage.buildBtn.setEnabled(state)


    def __importRSA(self, option):

        path_file, _ = QFileDialog.getOpenFileName(self.homePage.widget,"SELECT RSA FILE","", "File PEM (*.pem);")

        if not path_file:
            return

        self.config = self.storage.config()

        data = open(path_file, "r", encoding="UTF-8").read()

        if not security.is_valid_rsa_key(data):
            pymsgbox.alert("CAN'T VALIDATE KEY", "ERROR")
            return

        if "RSA_PUB_PATH" == option:
             self.config['RSA_PUB_PATH'] = data
        else:
            self.config['RSA_PRIV_PATH'] = data


        self.__init_form()
        self.storage.config(self.config)

        pymsgbox.alert("PROCESS COMPLETED", "NOTICE")


    def __exportRSA(self):

        pasta = self.__get_folder_file()

        if not pasta:
            return

        try:
            security.export_rsa(pasta, self.config['RSA_PRIV_PATH'], self.config['RSA_PUB_PATH'])
            pymsgbox.alert("PROCESS COMPLETED", "COMPLETED")
        except:
            pymsgbox.alert("FAILED TO EXPORT KEYS", "ERROR")

    def __get_folder_file(self, dest_widget: QtWidgets.QLineEdit = False, file=False, filter=None):

        if not file:
            path = QFileDialog.getExistingDirectory(self.homePage.widget, "Select a folder")
        else:
            path, _ = QFileDialog.getOpenFileName(self.homePage.widget, "Select a file", "", filter=filter)

        if not path:
            return

        if dest_widget:
            dest_widget.setText(path)
            dest_widget.setCursorPosition(0)
        else:
            return path

    def __rsaText(self, data):
        return data[:10] + "•" * len(data[10:])


    def __generateKeys(self):

        self.config = self.storage.config()

        self.config['RSA_PUB_PATH'] = False
        self.config['RSA_PRIV_PATH'] = False

        self.config['RSA_PRIV_PATH'], self.config['RSA_PUB_PATH'] = security.gen_rsa_keys()

        if self.config['RSA_PUB_PATH'] != False and self.config['RSA_PRIV_PATH'] != False:
            pymsgbox.alert("RSA KEYS CREATED SUCCESSFULLY", "SUCCESS")

            self.homePage.private_rsa.setText(self.__rsaText(self.config['RSA_PRIV_PATH']))
            self.homePage.public_rsa.setText(self.__rsaText(self.config['RSA_PUB_PATH']))
            self.__init_form()
            self.storage.config(self.config)
        else:
            pymsgbox.alert("AN ERROR OCCURRED WHILE CREATING RSA KEYS", "ERROR")

        self.storage.config(self.config)


if __name__ == '__main__':
    app = App()
    app.run()
