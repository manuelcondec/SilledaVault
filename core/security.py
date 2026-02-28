import time
import threading
import eel

CLAVE_VAULT = None
PEPPER_INTERNO = None
ULTIMA_ACTIVIDADE = 0
TIMEOUT_VAULT = 120
vault_lock = threading.Lock()

def reset_memoria():
    global CLAVE_VAULT, PEPPER_INTERNO
    if CLAVE_VAULT:
        for i in range(len(CLAVE_VAULT)): CLAVE_VAULT[i] = 0
    CLAVE_VAULT = None
    PEPPER_INTERNO = None

def monitor_inactividade():
    global CLAVE_VAULT, PEPPER_INTERNO
    while True:
        with vault_lock:
            if CLAVE_VAULT is not None:
                if (time.time() - ULTIMA_ACTIVIDADE > TIMEOUT_VAULT):
                    reset_memoria()
                    try: eel.notificar_bloqueo()()
                    except: pass
        time.sleep(5)