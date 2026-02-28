import string
import secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id

def generar_clave_maestra(password: str, salt: bytes):
    kdf = Argon2id(length=32, salt=salt, iterations=5, memory_cost=262144, lanes=4)
    return bytearray(kdf.derive(password.encode()))

def xerar_contrasinal_aleatoria(lonxitude=16):
    if lonxitude < 12: lonxitude = 12
    caracteres = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    pwd = [secrets.choice(string.ascii_lowercase), secrets.choice(string.ascii_uppercase),
           secrets.choice(string.digits), secrets.choice("!@#$%^&*()-_=+")]
    pwd += [secrets.choice(caracteres) for _ in range(lonxitude - 4)]
    secrets.SystemRandom().shuffle(pwd)
    return "".join(pwd)