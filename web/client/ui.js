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

// Matrix-style encrypted rain (pixel-art feel)
function initGameUI() {
    const canvas = document.getElementById('game-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    // settings tuned for pixel-art, slower drops
    let w = 0, h = 0;
    const chars = '01ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let columns = [];
    const pixelSnap = 6; // snap positions to this pixel grid -> pixel-art feel
    const slowFactor = 0.16; // smaller -> slower drops

    function resize() {
        w = canvas.width = window.innerWidth;
        h = canvas.height = window.innerHeight;
        // font size larger for readable pixel-art; will snap to pixel grid
        const fontSize = Math.max(12, Math.floor(w / 100));
        ctx.font = `${fontSize}px monospace`;
        ctx.textBaseline = 'top';
        // compute columns based on snapped cell width
        const cellW = Math.max(6, Math.floor(fontSize * 0.6));
        const cols = Math.floor(w / cellW) + 2;
        columns = new Array(cols).fill(0).map(() => Math.random() * h - Math.random() * 200);
        // pixelated look
        ctx.imageSmoothingEnabled = false;
        // dark background init
        ctx.fillStyle = 'rgba(1,6,23,1)'; ctx.fillRect(0,0,w,h);
    }

    function draw() {
        // slight fade to create visible trails
        ctx.fillStyle = 'rgba(1,6,23,0.22)';
        ctx.fillRect(0, 0, w, h);

        const fontSize = parseInt(ctx.font, 10);
        const cellW = Math.max(6, Math.floor(fontSize * 0.6));

        for (let i = 0; i < columns.length; i++) {
            // x snapped to cell grid
            const x = i * cellW;
            let y = columns[i];
            // snap positions for pixel look
            const snapX = Math.round(x / pixelSnap) * pixelSnap;
            const snapY = Math.round(y / pixelSnap) * pixelSnap;

            // bright head (white-green)
            const head = chars.charAt(Math.floor(Math.random() * chars.length));
            ctx.fillStyle = 'rgba(200,255,190,0.95)';
            ctx.shadowBlur = 0;
            ctx.fillText(head, snapX, snapY);

            // trailing characters, dimmer and more pixel-like
            for (let t = 1; t < 6; t++) {
                const ch = chars.charAt(Math.floor(Math.random() * chars.length));
                const yy = snapY - t * Math.round(fontSize * 0.9);
                const a = Math.max(0, 0.6 - t * 0.11);
                ctx.fillStyle = `rgba(0,200,120,${a})`;
                ctx.fillText(ch, snapX, yy);
            }

            // advance slowly
            const speed = fontSize * (slowFactor + Math.random() * 0.08);
            columns[i] = (y > h + 200) ? -50 - Math.random() * 300 : y + speed;
        }

        requestAnimationFrame(draw);
    }

    window.addEventListener('resize', resize);
    resize();
    requestAnimationFrame(draw);
}

document.addEventListener('DOMContentLoaded', () => { loadPartials(); initGameUI(); });
