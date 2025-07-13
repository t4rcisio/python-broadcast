from Crypto.PublicKey import RSA


def gen_rsa_keys(pub_file, priv_file):
    try:
        key = RSA.generate(2048)
        with open(priv_file, 'wb') as f:
            f.write(key.export_key())
        with open(pub_file, 'wb') as f:
            f.write(key.publickey().export_key())
        return True
    except:
        return False