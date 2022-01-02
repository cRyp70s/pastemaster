import os
import hashlib
from datetime import datetime
from random import SystemRandom

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

backend = default_backend()


def encrypt(key, iv, text):
    text += (16 - (len(text) % 16)) * "\0"
    backend = default_backend()
    cipher = Cipher(algorithms.AES(key.encode()), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()
    return encryptor.update(text.encode()) + encryptor.finalize()


def decrypt(key, iv, encrypted_text):
    backend = default_backend()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()
    return decryptor.update(encrypted_text) + decryptor.finalize()


def hashify(count=20):
    hash_ = hashlib.sha512()
    data = str(SystemRandom().randrange(9999999999900)).encode()
    hash_.update(data)
    return hash_.hexdigest()[: -(count + 1) : -1]
