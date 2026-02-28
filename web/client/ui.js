// ui.js - carga de partials y utilidades de UI
async function loadPartials() {
    try {
        const statusResp = await fetch('partials/status.html');
        if (statusResp.ok) document.getElementById('status-header-placeholder').innerHTML = await statusResp.text();
    } catch (e) { console.warn('No se pudo cargar partial status', e); }

    try {
        const footerResp = await fetch('partials/footer.html');
        if (footerResp.ok) document.getElementById('footer-placeholder').innerHTML = await footerResp.text();
    } catch (e) { console.warn('No se pudo cargar partial footer', e); }
}

document.addEventListener('DOMContentLoaded', () => loadPartials());
