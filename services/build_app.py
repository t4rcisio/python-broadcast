import json
import os
import shutil
import time
import traceback
from datetime import datetime
from zipfile import ZipFile
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from secrets import token_bytes

from services import database

ignorar_pastas = {'__pycache__', 'venv', '.venv', '.git', '.idea'}
ignorar_extensoes = {'.pyc', '.pyo'}
ignorar_arquivos = {'.DS_Store', 'Thumbs.db'}

class BuildApp:

    def __init__(self):

        self.storage = database.Storage()

    def filtro_personalizado(self, dir_path, nomes_conteudo):
        ignorar = set()
        for nome in nomes_conteudo:
            caminho_completo = os.path.join(dir_path, nome)

            if os.path.isdir(caminho_completo) and nome in ignorar_pastas:
                ignorar.add(nome)
            elif os.path.isfile(caminho_completo):
                _, ext = os.path.splitext(nome)
                if ext in ignorar_extensoes or nome in ignorar_arquivos:
                    ignorar.add(nome)

        return ignorar


    def zip_folder(self, folder, output_zip):

        with ZipFile(output_zip, 'w') as zipf:
            for root, dirs, files in os.walk(folder):
                # Remove diretórios que devem ser ignorados
                dirs[:] = [d for d in dirs if d not in ignorar_pastas]

                for file in files:
                    # Checagem de extensões e nomes
                    if (
                        os.path.splitext(file)[1] in ignorar_extensoes or
                        file in ignorar_arquivos
                    ):
                        continue

                    full_path = os.path.join(root, file)
                    relative_path = os.path.relpath(full_path, folder)
                    zipf.write(full_path, relative_path)


    def crypt_key_aes(self, data, key, iv):

        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        return encryptor.update(padded_data) + encryptor.finalize()

    def crypt_zip_rsa(self, zip_file, pub_key_path):

        # Gerar chave e IV aleatórios
        aes_key = token_bytes(32)  # AES-256
        iv = token_bytes(16)

        with open(zip_file, 'rb') as f:
            dados_zip = f.read()

        encrypted_data = self.crypt_key_aes(dados_zip, aes_key, iv)

        # Carregar chave pública e criptografar a chave AES
        with open(pub_key_path, 'rb') as f:
            rsa_key = RSA.import_key(f.read())

        cipher_rsa = PKCS1_OAEP.new(rsa_key)
        aes_key_encrypted = cipher_rsa.encrypt(aes_key)

        # Guardar chave AES criptografada, IV e dados criptografados

        with open(self.payload["OUTPUT_BIN"], 'wb') as f:
            f.write(len(aes_key_encrypted).to_bytes(4, 'big'))
            f.write(aes_key_encrypted)
            f.write(iv)
            f.write(encrypted_data)

        return True

    def project_inspector(self):


        if not os.path.exists(self.payload["SOURCE_PATH"] + "\\requirements.txt"):
            self.__updateText("requirements.txt NOT FOUND")
            return False

        if not os.path.exists(self.payload["SOURCE_PATH"] + "\\config.json"):
            self.__updateText("config.json NOT FOUND")
            return False

        params = ["app_name", "app_file","app_icon","args","author","version"]
        try:
            config = json.load(open(self.payload["SOURCE_PATH"] + "\\config.json", "r", encoding="UTF8"))
        except:
            self.__updateText("FAILED TO LOAD config.json")
            return False

        for item in params:
            if not item in config:
                self.__updateText(f"MISSING {item} in config.json")
                return False

        self.__updateText("config.json LOADED")
        return True


    def prebuild(self):

        tempPath = ".\\temp"
        self.__updateText("COPING PROJECT")

        if os.path.exists(tempPath):
            shutil.rmtree(tempPath)
        else:
            os.mkdir(tempPath)

        try:
            shutil.copytree(
                self.payload["SOURCE_PATH"],
                tempPath,
                ignore=self.filtro_personalizado,
                dirs_exist_ok=True  # Python 3.8+
            )
        except:
            self.__updateText("PREBUILD FAILED")
            return False

        if not os.path.exists(tempPath):
            self.__updateText("PREBUILD FAILED")
            return False

        self.payload["SOURCE_PATH"] = tempPath

        self.__updateText("PRE-COMPILING PROJECT")
        time.sleep(2)
        self.__updateText("PRE-COMPILING COMPLETED")

        return True


    def build(self, payload):

        try:
            self.payload = payload

            self.__updateText("BUILDING '" + self.payload['APP_NAME']+ "'")

            if self.payload['COMPILE_MODE'] == 'PRECOMPILE':
                if not self.prebuild():
                    return

            self.payload["OUTPUT_BIN"] =  self.payload["OUTPUT_BIN"] + "\\"+str(self.payload['APP_NAME'])+".bin"

            if not self.project_inspector():
                self.__updateText("FAILED TO BUILD PROJECT")
                return

            self.__updateText("COMPRESSING PROJECT")
            self.zip_folder(self.payload["SOURCE_PATH"], self.payload["TEMP_ZIP_PATH"])
            self.__updateText("COMPRESSED SUCCESSFULLY")

            self.__updateText("ENCRYPTING PROJECT")
            self.crypt_zip_rsa(self.payload["TEMP_ZIP_PATH"], self.payload["RSA_PUB_PATH"])

            os.remove(self.payload["TEMP_ZIP_PATH"])

        except:
            self.__updateText("UNSUSPECTED ERROR, VERIFY LOGS")
            self.storage.code_log(f"\n\n------------------------DATE:{datetime.now().strftime('%d.%m.%y %H:%M:%S')}\nCONTENT:{traceback.format_exc()}")


    def __updateText(self, text):

        logs = self.storage.logs()
        logs += "\n"+ str(datetime.now().strftime("%d.%m.%y %H:%M:%S")) + "\t------> "+str(text)
        self.storage.logs(logs)

