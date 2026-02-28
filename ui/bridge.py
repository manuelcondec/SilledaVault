import eel
import time
import hashlib
import secrets
import sqlite3
from core import security, crypto
from database import db_manager
from services.pwned_api import verificar_filtracion
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag


@eel.expose
def actualizar_actividade():
    with security.vault_lock:
        security.ULTIMA_ACTIVIDADE = time.time()


@eel.expose
def iniciar_sesion(password_master):
    actualizar_actividade()
    conn = db_manager.get_connection()
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
            posible_clave = crypto.generar_clave_maestra(password_master, salt)
            aes = AESGCM(posible_clave)
            # Validación da chave
            aes.decrypt(v_nonce, v_tag, None)

            with security.vault_lock:
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
        nova_clave = crypto.generar_clave_maestra(password_master, salt)
        aes = AESGCM(nova_clave)

        with security.vault_lock:
            security.PEPPER_INTERNO = secrets.token_bytes(32)
            security.CLAVE_VAULT = nova_clave

        vn, pn = secrets.token_bytes(12), secrets.token_bytes(12)
        cursor.execute("INSERT INTO config VALUES (1,?,?,?,?,?,0,0)",
                       (salt, vn, aes.encrypt(vn, b"AUTH_OK", None),
                        aes.encrypt(pn, security.PEPPER_INTERNO, None), pn))
        conn.commit()
        conn.close()
        return {"status": "OK", "pwned": "Primeiro uso."}


@eel.expose
def gardar_segredo(servizo, usuario, segredo):
    with security.vault_lock:
        if not security.CLAVE_VAULT: return "LOCKED"
        actualizar_actividade()

        aes = AESGCM(security.CLAVE_VAULT)
        h = hashlib.blake2b(key=security.PEPPER_INTERNO, digest_size=32)
        h.update(f"{servizo.lower()}{usuario.lower()}".encode())

        s_id = h.hexdigest()
        n1, n2, n3 = [secrets.token_bytes(12) for _ in range(3)]

        conn = db_manager.get_connection()
        conn.execute("INSERT OR REPLACE INTO data VALUES (NULL,?,?,?,?,?,?,?,0)",
                     (s_id, aes.encrypt(n1, servizo.encode(), None), n1,
                      aes.encrypt(n2, usuario.encode(), None), n2,
                      aes.encrypt(n3, segredo.encode(), None), n3))
        conn.commit()
        conn.close()
    return "OK"


@eel.expose
def buscar_segredo(termo):
    with security.vault_lock:
        if not security.CLAVE_VAULT: return "LOCKED"
        actualizar_actividade()

        conn = db_manager.get_connection()
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
                    u_dec = aes.decrypt(r[2], r[3], None).decode()
                    p_dec = aes.decrypt(r[4], r[5], None).decode()
                    res.append({
                        "servizo": s_dec,
                        "usuario": u_dec,
                        "segredo": p_dec,
                        "pwned": verificar_filtracion(p_dec)
                    })
            except:
                continue
        return res


@eel.expose
def xerar_contrasinal(lonxitude=16):
    actualizar_actividade()
    return crypto.xerar_contrasinal_aleatoria(lonxitude)


@eel.expose
def pechar_sesion():
    with security.vault_lock:
        security.reset_memoria()
    return True