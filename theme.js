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

    // The switch is a Game Boy style fade: the palette snaps through two
    // in-between shades rather than gliding. These must match style.css.
    const PALETTES = {
        light: { '--paper': '#F2EEE3', '--paper-light': '#F8F5EC', '--ink': '#1C1B19', '--ink-2': '#4A4740', '--pencil': '#A39E92' },
        dark:  { '--paper': '#12110F', '--paper-light': '#1C1B18', '--ink': '#ECE7DA', '--ink-2': '#A8A294', '--pencil': '#6E695F' },
    };
    const mix = (a, b, t) => '#' + [1, 3, 5].map(i => Math.round(
        parseInt(a.substr(i, 2), 16) * (1 - t) + parseInt(b.substr(i, 2), 16) * t
    ).toString(16).padStart(2, '0')).join('');
    const paint = (from, to, t) => Object.keys(PALETTES.light).forEach(k =>
        root.style.setProperty(k, mix(PALETTES[from][k], PALETTES[to][k], t)));
    const unpaint = () => Object.keys(PALETTES.light).forEach(k => root.style.removeProperty(k));
    // The owl sprites are fixed-colour images, so they step their opacity
    // alongside the palette, and show set frames for the blink.
    const owls = (opacity, frame) => document.querySelectorAll('img[data-owl]').forEach(img => {
        if (frame) img.src = `img/pixel/${frame}.svg`;
        img.style.opacity = opacity;
    });

    const STEP = 110;
    const switchTo = theme => {
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return apply(theme);
        const from = root.dataset.theme;
        // Pages pause their own owl animation while this runs.
        root.dataset.switching = '';
        const done = () => { owls(''); apply(theme); delete root.dataset.switching; };
        const timeline = theme === 'dark' ? [
            // Dusk: the page dims and the owl's body goes with it...
            [0, () => { paint(from, theme, 1 / 3); owls(0.66); }],
            [STEP, () => { paint(from, theme, 2 / 3); owls(0.33); }],
            [STEP * 2, () => { unpaint(); apply(theme); owls(0); }],
            // ...a beat of dark, then the eyes blink open.
            [STEP * 2 + 200, () => owls(1, 'owl-eyes-blink')],
            [STEP * 2 + 320, done],
        ] : [
            // Dawn: the eyes close first...
            [0, () => owls(1, 'owl-eyes-blink')],
            [120, () => { owls(0); paint(from, theme, 1 / 3); }],
            [120 + STEP, () => paint(from, theme, 2 / 3)],
            // ...then the day and the owl's body step back in together, eyes
            // still shut, and it wakes as the light settles.
            [120 + STEP * 2, () => { unpaint(); apply(theme); owls(0.33, 'owl-blink'); }],
            [120 + STEP * 3, () => owls(0.66)],
            [120 + STEP * 4, () => owls(1)],
            [120 + STEP * 4 + 140, done],
        ];
        timeline.forEach(([at, step]) => setTimeout(step, at));
    };

    root.dataset.theme = stored || (system.matches ? 'dark' : 'light');

    system.addEventListener('change', e => { if (!stored) switchTo(e.matches ? 'dark' : 'light'); });

    document.addEventListener('DOMContentLoaded', () => {
        apply(root.dataset.theme);
        const button = document.getElementById('theme-toggle');
        if (!button) return;
        button.addEventListener('click', () => {
            if ('switching' in root.dataset) return;
            stored = root.dataset.theme === 'dark' ? 'light' : 'dark';
            try { localStorage.setItem(KEY, stored); } catch (e) { /* still switches */ }
            switchTo(stored);
        });
    });
})();
