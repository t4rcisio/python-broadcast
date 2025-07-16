import os
import shutil
import subprocess
import zipfile
from datetime import datetime

from services import database


class StartApp:




    def __init__(self):

        self.storage = database.Storage()
        self.temp_folder = ".\\temp"
        self.temp_zip = ".\\recuperado.zip"



    def run(self, payload):

        self.payload = payload

        self.apps = self.storage.apps()
        self.appName = payload["app_name"]

        dados_zip = self.apps[self.appName]['dados']
        dest_path = self.apps[self.appName]['path'] + "\\app"

        self.remove_temp(dest_path)

        with open(self.temp_zip, 'wb') as f:
            f.write(dados_zip)


        if not os.path.exists(dest_path):
            os.mkdir(dest_path)

        self.unzip_app(self.temp_zip, dest_path)

        venv_python = os.path.join(self.apps[self.appName]["path"], ".venv", "Scripts", "python.exe")
        venv_python = os.path.abspath(venv_python)

        application = dest_path + "\\" + self.apps[self.appName]['app_file']

        result = subprocess.run(
            [venv_python, application],
            cwd=dest_path,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"❌ Failed to start {self.appName}")
            print("STDERR:\n", result.stderr)
        else:
            print(f"✅ Successfully to start {self.appName}")




    def remove_temp(self, path):

        try:
            shutil.rmtree(path)
            return
        except:
            pass

        try:
            os.remove(self.temp_zip)
            return
        except:
            pass

    def unzip_app(self, caminho_zip, pasta_destino):
        with zipfile.ZipFile(caminho_zip, 'r') as zip_ref:
            zip_ref.extractall(pasta_destino)

    def __updateText(self, text):

        logs = self.storage.logs()
        logs += "\n"+ str(datetime.now().strftime("%d.%m.%y %H:%M:%S")) + "\t------> "+str(text)
        self.storage.logs(logs)