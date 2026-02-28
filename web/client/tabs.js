// tabs.js - gestión de pestañas y utilidades de vista
window.tab = function(id, btn) {
    document.querySelectorAll('.tab-content').forEach(t => t.style.display = 'none');
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    const target = document.getElementById(id);
    if (target) target.style.display = 'block';
    if (btn) btn.classList.add('active');
    const out = document.getElementById('tool-output'); if (out) out.innerText = "";
}

window.toggleView = function(id) {
    const el = document.getElementById(id);
    if (!el) return;
    el.type = el.type === "password" ? "text" : "password";
}
