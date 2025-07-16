import os
from filelock import FileLock
import pickle

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import base64

class Storage:

    def __init__(self):

        self.root = "./sources"
        self._apps = "C:\\_apps"

        [self.__createFolders(i) for i in [self.root, self._apps]]

        self.logFile = self.root + "\\logs.pickle"
        self.codeLog = self.root + "\\code_log.pickle"

        self.fileKey = "cnjdTRE#$%¨&(*UOIJNJ@#*RVFDXW#$FRXwxcyokmlpGEXRSW$#W%E&THUOIYR"

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

                        enc_data = self.__encrypt_string(str(data), self.fileKey)
                        pickle.dump(enc_data, file)

                else:

                    with open(path, "rb") as file:
                        res = self.__decrypt_string(pickle.load(file), self.fileKey)
                        try:
                            return eval(res)
                        except:
                            return res
        except:
            return None

    def __createFolders(self, path):

        try:
            os.mkdir(path)
        except:
            pass


    def __derive_key(self, password, salt):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(password.encode())

    def __encrypt_string(self, plaintext, password):

        salt = os.urandom(16)
        key = self.__derive_key(password, salt)
        iv = os.urandom(16)

        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext.encode()) + padder.finalize()

        ciphertext = encryptor.update(padded_data) + encryptor.finalize()

        return base64.b64encode(salt + iv + ciphertext).decode()

    def __decrypt_string(self, ciphertext, password):

        decoded_data = base64.b64decode(ciphertext)
        salt = decoded_data[:16]
        iv = decoded_data[16:32]
        ciphertext = decoded_data[32:]

        key = self.__derive_key(password, salt)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        padded_data = decryptor.update(ciphertext) + decryptor.finalize()

        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_data) + unpadder.finalize()

        return plaintext.decode()