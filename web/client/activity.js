// activity.js - detección de actividade y notificación desde Python
window.registrarActividade = function() {
    const main = document.getElementById('view-main');
    if (main && main.classList.contains('active')) {
        try { eel.actualizar_actividade()(); } catch (e) { console.warn('eel no disponible', e); }
    }
}

function notificar_bloqueo() {
    alert("Sesión expirada por inactividade. O búnker foi selado.");
    location.reload();
}

try { eel.expose(notificar_bloqueo); } catch (e) { /* eel could be undefined in static preview */ }
