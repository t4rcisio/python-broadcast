import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime

from services import database

import traceback
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import zipfile

class InstallApp:

    def __init__(self):

        self.storage = database.Storage()
        self.temp_folder = ".\\temp"
        self.temp_zip = ".\\recuperado.zip"


    def uncrypt_aes(self, data, key, iv):
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(data) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        return unpadder.update(padded_data) + unpadder.finalize()

    def unzip_app(self, caminho_zip, pasta_destino):
        with zipfile.ZipFile(caminho_zip, 'r') as zip_ref:
            zip_ref.extractall(pasta_destino)

    def uncrypt_rsa(self, arquivo_cripto, rsa_key):
        with open(arquivo_cripto, 'rb') as f:
            tamanho_chave = int.from_bytes(f.read(4), 'big')
            chave_aes_cripto = f.read(tamanho_chave)
            iv = f.read(16)
            dados_cripto = f.read()

        rsa_key = RSA.import_key(rsa_key)

        cipher_rsa = PKCS1_OAEP.new(rsa_key)
        chave_aes = cipher_rsa.decrypt(chave_aes_cripto)

        return dados_cripto, chave_aes, iv

    def __load_app_info(self, dados_cripto, chave_aes, iv):
        self.remove_temp()
        dados_zip = self.uncrypt_aes(dados_cripto, chave_aes, iv)

        with open(self.temp_zip, 'wb') as f:
            f.write(dados_zip)

        self.unzip_app(self.temp_zip, self.temp_folder)

        try:
            config = json.load(open(".\\temp\\config.json", "r", encoding="UTF8"))
        except:
            raise "FAILED TO LOAD config.json"

        config["dados"] = dados_zip
        return config

    def __buildApp(self, config):

        self.apps = self.storage.apps()
        self.appName = config['app_name']

        self.apps[self.appName] = config
        self.apps[self.appName]["path"] = self.storage._apps + "\\" + self.appName.replace(" ", "_")
        self.apps[self.appName]["icon"] = self.apps[self.appName]["path"] + "\\icon.png"
        self.apps[self.appName]["requirements"] = self.apps[self.appName]["path"] + "\\requirements.txt"


        if os.path.exists(self.apps[self.appName]["path"]):
            shutil.rmtree(self.apps[self.appName]["path"])

        os.mkdir(self.apps[self.appName]["path"])

        t = 0
        while not os.path.exists(self.temp_folder + "\\" + self.apps[self.appName]["app_icon"]):
            if t > 10:
                break
            time.sleep(1)

            t+=1


        shutil.copy(self.temp_folder + "\\" + self.apps[self.appName]["app_icon"], self.apps[self.appName]["icon"])
        shutil.copy(self.temp_folder + "\\requirements.txt" ,self.apps[self.appName]["requirements"])


    def build_env(self):

        self.__updateText("CREATING VENV")
        python_path = self.apps[self.appName]["path"] + "\.venv\\Scripts\\python.exe"

        try:
            result = subprocess.run(
                [sys.executable, '-m', 'venv', '.venv'],
                cwd=self.apps[self.appName]["path"],
                capture_output=True,
                text=True,
                check=True
            )
            print("Virtual environment created successfully!")

        except subprocess.CalledProcessError as e:
            print("ERROR: Failed to create virtual environment.")
            text = f"Return Code: {e.returncode}\nStdout: {e.stdout}\nStderr: {e.stderr}"
            self.storage.code_log( f"\n\n------------------------DATE:{datetime.now().strftime('%d.%m.%y %H:%M:%S')}\nCONTENT:{text}")
            raise "UNABLE TO CREATE VENV"


        venv_python = os.path.join(self.apps[self.appName]["path"], ".venv", "Scripts", "python.exe")
        venv_python = os.path.abspath(venv_python)

        req_path = os.path.join(self.apps[self.appName]["path"], "requirements.txt")

        with open(req_path, "r", encoding="utf-16") as file:
            packages = [line.strip() for line in file if line.strip() and not line.startswith("#")]

        index = 0
        for pkg in packages:

            index +=1

            perce = round((index/len(packages))*100, 2)
            self.__updateText(f"INSTALLING {pkg} | {perce}%")

            result = subprocess.run(
                [venv_python, "-m", "pip", "install", pkg],
                cwd=self.apps[self.appName]["path"],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                text = f"❌ Failed to install {pkg}\nSTDERR:\n{result.stderr}"
                self.storage.code_log(f"\n\n------------------------DATE:{datetime.now().strftime('%d.%m.%y %H:%M:%S')}\nCONTENT:{text}")
                raise "FAILED TO INSTALL PKG"
            else:
                text = f"✅ Successfully installed {pkg}\nSTDERR:\n{result.stdout}"
                self.storage.code_log(f"\n\n------------------------DATE:{datetime.now().strftime('%d.%m.%y %H:%M:%S')}\nCONTENT:{text}")


    def remove_temp(self):

        try:
            shutil.rmtree(self.temp_folder)
            os.remove(self.temp_zip)
        except:
            pass

    def __updateText(self, text):

        logs = self.storage.logs()
        logs += "\n"+ str(datetime.now().strftime("%d.%m.%y %H:%M:%S")) + "\t------> "+str(text)
        self.storage.logs(logs)


    def run(self, payload):

        try:
            self.payload = payload
            self.__updateText("CHECKING DATA")
            dados_cripto, chave_aes, iv = self.uncrypt_rsa(self.payload["APP_PATH"], self.payload["RSA_PRIV_PATH"])

            self.__updateText("LOADING INFO")
            config = self.__load_app_info(dados_cripto, chave_aes, iv)

            self.__updateText("BUILDING PROJECT")
            self.__buildApp(config)
            self.build_env()

            self.storage.apps(self.apps)
            self.remove_temp()

            self.__updateText("BUILD COMPLETED")

        except:
            self.remove_temp()
            self.__updateText("OCORREU UM ERRO")
            print(traceback.format_exc())
            self.storage.code_log(f"\n\n------------------------DATE:{datetime.now().strftime('%d.%m.%y %H:%M:%S')}\nCONTENT:{traceback.format_exc()}")
