// Light and dark ("day" and "night"). Loaded in <head>, before the page
// paints, so the right theme shows from the first frame. A choice made with
// the toggle is remembered; until then the site follows the system setting.
(function () {
    const KEY = 'theme';
    const root = document.documentElement;
    const system = window.matchMedia('(prefers-color-scheme: dark)');

    let stored = null;
    try { stored = localStorage.getItem(KEY); } catch (e) { /* private mode */ }

    // At night the owl's body sinks into the dark; only its eyes stay lit.
    // Frames are named owl, owl-ne, owl-blink...; night ones owl-eyes-ne...
    window.owlSrc = frame => 'img/pixel/' +
        (root.dataset.theme === 'dark' ? frame.replace(/^owl/, 'owl-eyes') : frame) + '.svg';

    const apply = theme => {
        root.dataset.theme = theme;
        document.querySelectorAll('img[data-owl]').forEach(img => { img.src = owlSrc(img.dataset.owl); });
        const button = document.getElementById('theme-toggle');
        if (button) button.setAttribute('aria-label', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
        const meta = document.querySelector('meta[name="theme-color"]');
        if (meta) meta.content = theme === 'dark' ? '#12110F' : '#F2EEE3';
    };

    root.dataset.theme = stored || (system.matches ? 'dark' : 'light');

    system.addEventListener('change', e => { if (!stored) apply(e.matches ? 'dark' : 'light'); });

    document.addEventListener('DOMContentLoaded', () => {
        apply(root.dataset.theme);
        const button = document.getElementById('theme-toggle');
        if (!button) return;
        button.addEventListener('click', () => {
            stored = root.dataset.theme === 'dark' ? 'light' : 'dark';
            try { localStorage.setItem(KEY, stored); } catch (e) { /* still switches */ }
            apply(stored);
        });
    });
})();
