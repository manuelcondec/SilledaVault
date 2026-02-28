// search.js - búsqueda y renderizado de resultados
window.search = async function() {
    const qEl = document.getElementById('search-input');
    if (!qEl) return;
    const q = qEl.value;
    if (!q) return;
    try {
        const res = await eel.buscar_segredo(q)();
        const container = document.getElementById('search-results');
        container.innerHTML = "";
        if (res === "LOCKED") location.reload();
        res.forEach(d => {
            const item = document.createElement('div');
            item.className = "result-item";
            const pColor = d.pwned && d.pwned.includes("⚠️") ? "var(--neon-red)" : "var(--neon-green)";
            item.innerHTML = `
                <small style="color:var(--neon-blue)">${d.servizo.toUpperCase()}</small><br>
                <strong>${d.usuario}</strong>
                <code onclick="copyReveal('${d.segredo}', this)">••••••••</code>
                <div style="font-size:0.65rem; color:${pColor}">${d.pwned}</div>
            `;
            container.appendChild(item);
        });
    } catch (e) { console.error(e); }
}

window.copyReveal = function(txt, el) {
    try { navigator.clipboard.writeText(txt); } catch (e) { console.warn('clipboard failed', e); }
    el.innerText = txt;
    el.classList.add('visible');
    setTimeout(() => { el.innerText = "••••••••"; el.classList.remove('visible'); }, 10000);
}
