import eel
import threading
from pathlib import Path
from database.db_manager import init_db
from core.security import monitor_inactividade
from services import api  # Importar las funciones de eel.expose



def start_app():
    init_db()

    threading.Thread(target=monitor_inactividade, daemon=True).start()

    base_dir = Path(__file__).resolve().parent
    web_dir = base_dir / 'web'

    print(f"[SISTEMA] Iniciando interface dende: {web_dir}")

    eel.init(str(web_dir))

    try:
        eel.start('index.html', size=(1000, 750), port=0)
    except (SystemExit, KeyboardInterrupt):
        print("[SISTEMA] Pechando bÃºnker...")


if __name__ == "__main__":
    start_app()