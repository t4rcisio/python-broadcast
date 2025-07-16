from Crypto.PublicKey import RSA
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

def gen_rsa_keys():
    try:
        key = RSA.generate(2048)
        return key.export_key().decode("utf-8"), key.publickey().export_key().decode("utf-8")
    except:
        return False, False


def export_rsa(dest, priv_key, pub_key):
    try:
        with open(dest + "\\build_key.pem", 'wb') as f:
            f.write(pub_key)
        with open(dest +"\\installer_key.pem", 'wb') as f:
            f.write(priv_key)
        return True
    except:
        return False


def is_valid_rsa_key(key_str: str) -> bool:
    try:
        key_bytes = key_str.encode()

        # Tenta carregar como chave privada
        serialization.load_pem_private_key(key_bytes, password=None, backend=default_backend())
        return True
    except Exception:
        pass

    try:
        # Tenta carregar como chave pública
        serialization.load_pem_public_key(key_bytes, backend=default_backend())
        return True
    except Exception:
        pass

    return False