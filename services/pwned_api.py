import hashlib
import requests

def verificar_filtracion(contrasinal):
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