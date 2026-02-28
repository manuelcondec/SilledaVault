// generator.js - creación y guardado de contrasinais
window.xerar = async function() {
    try {
        const pwd = await eel.xerar_contrasinal()();
        const el = document.getElementById('new-pass'); if (el) el.value = pwd;
        const out = document.getElementById('tool-output'); if (out) out.innerText = "Contrasinal xerada.";
    } catch (e) { console.error(e); }
}

window.save = async function() {
    try {
        const s = document.getElementById('new-service').value;
        const u = document.getElementById('new-user').value;
        const p = document.getElementById('new-pass').value;
        const res = await eel.gardar_segredo(s, u, p)();
        if (res === "OK") {
            alert("Gardado!");
            document.getElementById('new-service').value = "";
            document.getElementById('new-user').value = "";
            document.getElementById('new-pass').value = "";
        }
    } catch (e) { console.error(e); }
}
