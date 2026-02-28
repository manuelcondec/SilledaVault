// events.js - listeners y atajos
document.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        const loginView = document.getElementById('view-login');
        if (loginView && loginView.classList.contains('active')) {
            if (window.login) window.login();
        } else {
            const tabSearch = document.getElementById('tab-search');
            if (tabSearch && tabSearch.style.display !== 'none') {
                if (window.search) window.search();
            }
        }
    }
});
