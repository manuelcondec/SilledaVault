# Silleda Vault

Xestor de contrasinais local de alta seguridade deseñado para funcionar como un búnker illado. Utiliza unha arquitectura baseada en **Python** para o backend e tecnoloxías web para unha interface moderna, priorizando o cifrado de grao militar e a volatilidade de datos en memoria.

---

## Características Principais

* **Cifrado AES-256-GCM:** Todos os segredos están protexidos mediante cifrado autenticado (AEAD) para garantir a integridade e confidencialidade.
* **Derivación de Chaves con Argon2id:** Utiliza o algoritmo Argon2id con 256MB de custo de memoria e 5 iteracións para resistir ataques de forza bruta.
* **Arquitectura "Zero-Knowledge":** A chave mestra nunca se garda no disco; reconstrúese en memoria volátil ao iniciar sesión.
* **Monitor de Inactividade:** Bloqueo automático e borrado de memoria tras 120 segundos sen actividade.
* **Protección Antibruta:** Implementa un bloqueo temporal exponencial tras varios intentos erróneos de acceso.
* **Verificación de Filtracións:** Integración coa API de *Have I Been Pwned* para comprobar se os teus contrasinais foron expostos en brechas de seguridade.

---

## Estrutura do Proxecto

* `main.py`: Punto de entrada que inicia a interface e os fíos de seguridade.
* `core/crypto.py`: Primitivas para a xeración de chaves e contrasinais aleatorios.
* `core/security.py`: Xestión do tempo de vida da sesión e limpeza de memoria RAM.
* `database/db_manager.py`: Xestión da base de datos `vault.db`.
* `services/api.py` / `bridge.py`: Ponte de comunicación entre o frontend (JS) e o backend (Python).
* `services/pwned_api.py`: Lóxica para a consulta anónima de contrasinais filtrados.

---

## Instalación 

### Requisitos previos
Instala as dependencias necesarias:
```bash
pip install -r requirements.txt
