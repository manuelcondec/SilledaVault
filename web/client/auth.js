// auth.js - funciones de inicio/cierre de sesión y cambio de master
window.login = async function() {
    const passEl = document.getElementById('master-pass');
    if (!passEl) return;
    const pass = passEl.value;
    try {
        const res = await eel.iniciar_sesion(pass)();
        if (res.status === "OK") {
            const dot = document.getElementById('dot');
            if (dot) dot.classList.add('online');
            document.getElementById('view-login').classList.remove('active');
            document.getElementById('view-main').classList.add('active');
            if (res.pwned && res.pwned.includes("⚠️")) alert("AVISO: A túa Chave Mestra está filtrada!");
            try { eel.actualizar_actividade()(); } catch (e) { }
        } else if (res.status === "LOCKED_TIME") {
            document.getElementById('login-msg').innerText = res.msg;
        } else {
            document.getElementById('login-msg').innerText = "Chave incorrecta.";
        }
    } catch (e) { console.error(e); }
}

window.logout = async function() {
    try { await eel.pechar_sesion()(); } catch (e) { }
    location.reload();
}

window.changeMaster = async function() {
    try {
        const res = await eel.cambiar_contrasinal_mestra(document.getElementById('old-master').value, document.getElementById('new-master').value)();
        if (res === "OK") { alert("Éxito! Inicia sesión de novo."); logout(); }
        else { alert(res); }
    } catch (e) { console.error(e); }
}
