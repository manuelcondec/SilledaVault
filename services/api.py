import eel
import time
import hashlib
import secrets
import requests
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
from cryptography.exceptions import InvalidTag
from database.db_manager import get_connection
from core import security

def generar_clave_maestra(password: str, salt: bytes):
    kdf = Argon2id(length=32, salt=salt, iterations=5, memory_cost=262144, lanes=4)
    return bytearray(kdf.derive(password.encode()))

@eel.expose
def actualizar_actividade():
    security.ULTIMA_ACTIVIDADE = time.time()

@eel.expose
def verificar_filtracion(contrasinal):
    actualizar_actividade()
    sha1_pwd = hashlib.sha1(contrasinal.encode('utf-8')).hexdigest().upper()
    prefixo, sufixo = sha1_pwd[:5], sha1_pwd[5:]
    try:
        res = requests.get(f"https://api.pwnedpasswords.com/range/{prefixo}", timeout=5)
        if res.status_code != 200: return "Erro API"
        for liña in res.text.splitlines():
            h_suf, conta = liña.split(':')
            if h_suf == sufixo: return f"⚠️ FILTRADA {conta} veces!"
        return "✅ Segura"
    except:
        return "Erro conexión"

@eel.expose
def iniciar_sesion(password_master):
    actualizar_actividade()
    with security.vault_lock:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT salt, v_nonce, v_tag, p_cipher, p_nonce, intentos, bloqueo FROM config WHERE id = 1")
            row = cursor.fetchone()
        except:
            row = None

        tempo_actual = time.time()
        if row:
            salt, v_nonce, v_tag, p_cipher, p_nonce, intentos, t_bloqueo = row
            if tempo_actual < t_bloqueo:
                espera = int(t_bloqueo - tempo_actual)
                conn.close()
                return {"status": "LOCKED_TIME", "msg": f"Búnker selado. Agarda {espera}s."}

            try:
                posible_clave = generar_clave_maestra(password_master, salt)
                aes = AESGCM(posible_clave)
                aes.decrypt(v_nonce, v_tag, None)
                security.PEPPER_INTERNO = aes.decrypt(p_nonce, p_cipher, None)
                security.CLAVE_VAULT = posible_clave
                cursor.execute("UPDATE config SET intentos = 0, bloqueo = 0 WHERE id = 1")
                conn.commit()
                pwned = verificar_filtracion(password_master)
                conn.close()
                return {"status": "OK", "pwned": pwned}
            except InvalidTag:
                novos_intentos = intentos + 1
                bloqueo_final = tempo_actual + (30 * (2 ** (novos_intentos - 4))) if novos_intentos >= 4 else 0
                cursor.execute("UPDATE config SET intentos = ?, bloqueo = ? WHERE id = 1", (novos_intentos, bloqueo_final))
                conn.commit()
                conn.close()
                return {"status": "ERROR", "msg": "Chave incorrecta."}
        else:
            salt = secrets.token_bytes(16)
            security.CLAVE_VAULT = generar_clave_maestra(password_master, salt)
            aes = AESGCM(security.CLAVE_VAULT)
            security.PEPPER_INTERNO = secrets.token_bytes(32)
            vn, pn = secrets.token_bytes(12), secrets.token_bytes(12)
            cursor.execute("INSERT INTO config VALUES (1,?,?,?,?,?,0,0)",
                           (salt, vn, aes.encrypt(vn, b"AUTH_OK", None), aes.encrypt(pn, security.PEPPER_INTERNO, None), pn))
            conn.commit()
            conn.close()
            return {"status": "OK", "pwned": "Primeiro uso."}

@eel.expose
def xerar_contrasinal(lonxitude=16):
    actualizar_actividade()
    caracteres = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    pwd = "".join(secrets.choice(caracteres) for _ in range(lonxitude))
    return pwd

@eel.expose
def cambiar_contrasinal_mestra(vella_pass, nova_pass):
    actualizar_actividade()
    with security.vault_lock:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT salt, v_nonce, v_tag FROM config WHERE id = 1")
        row = cursor.fetchone()
        if not row:
            conn.close()
            return "Non hai configuración inicial."

        salt, v_nonce, v_tag = row
        try:
            vella_clave_gen = generar_clave_maestra(vella_pass, salt)
            AESGCM(vella_clave_gen).decrypt(v_nonce, v_tag, None)

            novo_salt = secrets.token_bytes(16)
            nova_clave = generar_clave_maestra(nova_pass, novo_salt)
            nova_aes, vella_aes = AESGCM(nova_clave), AESGCM(security.CLAVE_VAULT)

            cursor.execute("SELECT id, s_n, s_c, u_n, u_c, p_n, p_c FROM data WHERE honey = 0")
            for r in cursor.fetchall():
                s = vella_aes.decrypt(r[1], r[2], None)
                u = vella_aes.decrypt(r[3], r[4], None)
                p = vella_aes.decrypt(r[5], r[6], None)
                n1, n2, n3 = [secrets.token_bytes(12) for _ in range(3)]
                cursor.execute("UPDATE data SET s_n=?, s_c=?, u_n=?, u_c=?, p_n=?, p_c=? WHERE id=?",
                               (n1, nova_aes.encrypt(n1, s, None), n2, nova_aes.encrypt(n2, u, None), n3,
                                nova_aes.encrypt(n3, p, None), r[0]))

            vn, pn = secrets.token_bytes(12), secrets.token_bytes(12)
            cursor.execute("UPDATE config SET salt=?, v_nonce=?, v_tag=?, p_cipher=?, p_nonce=? WHERE id=1",
                           (novo_salt, vn, nova_aes.encrypt(vn, b"AUTH_OK", None),
                            nova_aes.encrypt(pn, security.PEPPER_INTERNO, None), pn))
            conn.commit()
            security.CLAVE_VAULT = nova_clave
            conn.close()
            return "OK"
        except InvalidTag:
            conn.close()
            return "A chave actual non é correcta. Migración abortada."

@eel.expose
def gardar_segredo(servizo, usuario, segredo):
    actualizar_actividade()
    with security.vault_lock:
        if not security.CLAVE_VAULT: 
            return "LOCKED"
        aes = AESGCM(security.CLAVE_VAULT)
        h = hashlib.blake2b(key=security.PEPPER_INTERNO, digest_size=32)
        h.update(f"{servizo.lower()}{usuario.lower()}".encode())
        s_id, n1, n2, n3 = h.hexdigest(), secrets.token_bytes(12), secrets.token_bytes(12), secrets.token_bytes(12)
        conn = get_connection()
        conn.execute("INSERT OR REPLACE INTO data VALUES (NULL,?,?,?,?,?,?,?,0)",
                     (s_id, aes.encrypt(n1, servizo.encode(), None), n1, aes.encrypt(n2, usuario.encode(), None), n2,
                      aes.encrypt(n3, segredo.encode(), None), n3))
        conn.commit()
        conn.close()
        return "OK"

@eel.expose
def buscar_segredo(termo):
    actualizar_actividade()
    with security.vault_lock:
        if not security.CLAVE_VAULT: 
            return "LOCKED"
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT s_n, s_c, u_n, u_c, p_n, p_c FROM data WHERE honey = 0")
        rows = cursor.fetchall()
        conn.close()
        res = []
        aes = AESGCM(security.CLAVE_VAULT)
        for r in rows:
            try:
                s_dec = aes.decrypt(r[0], r[1], None).decode()
                if termo.lower() in s_dec.lower():
                    p_dec = aes.decrypt(r[4], r[5], None).decode()
                    res.append({"servizo": s_dec, "usuario": aes.decrypt(r[2], r[3], None).decode(), "segredo": p_dec,
                                "pwned": verificar_filtracion(p_dec)})
            except:
                continue
        return res

@eel.expose
def pechar_sesion():
    with security.vault_lock:
        security.reset_memoria()
    return True