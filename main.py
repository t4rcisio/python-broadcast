import os.path
import shutil
import sys
import traceback
from datetime import datetime

import pymsgbox
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtCore import QFileSystemWatcher, Qt
from PyQt6.QtGui import QMovie
from PyQt6.QtWidgets import QFileDialog

from pages import home_page, app_widget
from q_threads import q_thread
from services import database, security, build_app, install_app


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
            icon2.addPixmap(QtGui.QPixmap(".\\sources\\app.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
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

        if 'RSA_PRIV_PATH' in self.config:
            self.homePage.private_rsa.setText(self.__rsaText(self.config['RSA_PRIV_PATH']))

        self.homePage.public_rsa.setCursorPosition(0)
        self.homePage.private_rsa.setCursorPosition(0)


        self.projects = self.storage.projects()

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

                appWidget.app_name.setText('<html><head/><body><p align="center"><span style=" font-size:11pt; font-weight:600; color:#ffffff;">'+str(app)+'</span></p></body></html>')

                app_icon = QtGui.QIcon()
                app_icon.addPixmap(QtGui.QPixmap(self.apps[app_name]['icon']), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
                appWidget.icon_app.setIcon(app_icon)

                appWidget.run_btn.clicked.connect(lambda state, script=app_name: self.__run_app(script))
                appWidget.delete_btn.clicked.connect(lambda state, script=app_name: self.__remove_app(script))
                appWidget.info_btn.clicked.connect(lambda state, script=app_name: self.__info_app(script))
                if "app_color" in self.apps[app_name]:
                    appWidget.widget_20.setStyleSheet(f"background-color: {self.apps[app_name]['app_color']};")

                self.homePage.verticalLayout_21.addWidget(widget)



    def __run_app(self, name):
        print(name)

    def __remove_app(self, name):
        print(name)

    def __info_app(self, name):
        print(name)


    def __install_app(self):

        self.func = install_app.InstallApp()

        if not os.path.exists(self.homePage.path_input.text()):
            pymsgbox.alert("Select path to app", "ERROR")
            return

        if not os.path.exists(self.config['RSA_PUB_PATH']):
            pymsgbox.alert("RSA builder not found", "ERROR")
            return

        params = {
            "APP_PATH": self.homePage.path_input.text(),
            "RSA_PRIV_PATH": self.config['RSA_PRIV_PATH'],
        }

        if "" in list(params.values()):
            pymsgbox.alert("COMPLETE ALL FIELDS", "ERROR")
            return

        payload = {
            "FX": self.func.run,
            "DATA": params
        }

        self.is_running = "INSTALL"


        self.qThread = q_thread.ThreadService()
        self.qThread.startThread(payload, self.__start, self.__end, self.__update)

        self.storage.projects(self.projects)


    def __buildProject(self):


        if self.is_running:
            pymsgbox.alert("Already proccess is running", "ERROR")
            return

        if not 'RSA_PUB_PATH' in self.config:
            pymsgbox.alert("RSA PUB not found", "ERROR")
            return

        self.func = build_app.BuildApp()

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

        if not os.path.exists(self.config['RSA_PUB_PATH']):
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

        payload = {
            "FX": self.func.build,
            "DATA": params
        }

        self.is_running = "BUILD"

        self.qThread = q_thread.ThreadService()
        self.qThread.startThread(payload, self.__start, self.__end, self.__update)

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

    def updateLog(self):

        code_log = self.storage.code_log()
        self.homePage.logsText.setPlainText(code_log)


    def __updateText(self, text):

        logs = self.storage.logs()
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

        if "RSA_PUB_PATH" == option:
             dst = self.storage.root + "\\public.pem"
        else:
            dst = self.storage.root + "\\private.pem"

        shutil.copy(path_file, dst)

        self.config[option] = dst
        self.__init_form()

        pymsgbox.alert("PROCESS COMPLETED", "COMPLETED")


    def __exportRSA(self):

        pasta = self.__get_folder_file()

        if not pasta:
            return

        dst = pasta +"\\"+ os.path.basename(self.config['RSA_PUB_PATH'])
        shutil.copy(self.config['RSA_PUB_PATH'], dst)

        dst = pasta + "\\" + os.path.basename(self.config['RSA_PRIV_PATH'])
        shutil.copy(self.config['RSA_PRIV_PATH'], dst)

        pymsgbox.alert("PROCESS COMPLETED", "COMPLETED")

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

    def __rsaText(self, path):

        data = open(path, "r", encoding="UTF-8").read()
        return data[:10] + "•" * len(data[10:])


    def __generateKeys(self):

        self.config = self.storage.config()

        self.config['RSA_PUB_PATH'] = self.storage.root + "\\public.pem"
        self.config['RSA_PRIV_PATH'] = self.storage.root + "\\private.pem"

        for path in [self.config['RSA_PRIV_PATH'], self.config['RSA_PUB_PATH']]:
            if os.path.exists(path):
                os.remove(path)

        response = security.gen_rsa_keys(self.config['RSA_PUB_PATH'], self.config['RSA_PRIV_PATH'])

        if response:
            pymsgbox.alert("RSA KEYS CREATED SUCCESSFULLY", "SUCCESS")

            self.homePage.private_rsa.setText(self.__rsaText(self.config['RSA_PRIV_PATH']))
            self.homePage.public_rsa.setText(self.__rsaText(self.config['RSA_PUB_PATH']))
            self.__init_form()
            self.storage.config(self.config)
        else:
            pymsgbox.alert("AN ERROR OCCURRED WHILE CREATING RSA KEYS", "ERROR")





if __name__ == '__main__':
    app = App()
    app.run()
