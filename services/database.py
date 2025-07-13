import os
from filelock import FileLock
import pickle

class Storage:

    def __init__(self):

        self.root = "./sources"
        self._apps = "C:\\_apps"

        [self.__createFolders(i) for i in [self.root, self._apps]]

        self.logFile = self.root + "\\logs.pickle"
        self.codeLog = self.root + "\\code_log.pickle"

    def config(self, data=None):

        return self.__dataControl(self.root + "\\config.pickle", data)

    def code_log(self, data=None):

        return self.__dataControl(self.codeLog, data)

    def projects(self, data=None):

        return self.__dataControl(self.root + "\\projects.pickle", data)

    def apps(self, data=None):

        return self.__dataControl(self.root + "\\apps.pickle", data)

    def logs(self, data=None):

        return self.__dataControl(self.logFile, data)

    def __dataControl(self, path, data=None):

        lockFile = path + ".lock"
        lock = FileLock(lockFile)

        try:

            with lock:

                if data != None:

                    with open(path, "wb") as file:

                        pickle.dump(data, file)

                else:

                    with open(path, "rb") as file:
                        res = pickle.load(file)

                        return res
        except:
            return None

    def __createFolders(self, path):

        try:
            os.mkdir(path)
        except:
            pass