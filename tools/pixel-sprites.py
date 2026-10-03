# Run from the repo root: python3 tools/pixel-sprites.py
#
# Generates the 1-bit sprites in img/pixel/. Each sprite is a grid of
# characters: '#' = ink, '.' = paper (transparent). Edit a grid, re-run.

INK = '#1C1B19'
N = 16


def blank(w=N, h=N):
    return [['.'] * w for _ in range(h)]


def rounded(g):
    """Fill a 16x16 pixel rounded square with 2-step corners."""
    for y in range(N):
        inset = 2 if y in (0, 15) else (1 if y in (1, 14) else 0)
        for x in range(inset, N - inset):
            g[y][x] = '#'
    return g


def disc(cx, cy, r):
    return lambda x, y: (x + .5 - cx) ** 2 + (y + .5 - cy) ** 2 <= r * r


def paint(g, test, ch):
    for y in range(len(g)):
        for x in range(len(g[0])):
            if test(x, y):
                g[y][x] = ch
    return g


def stamp(g, rows, ox, oy):
    for dy, row in enumerate(rows):
        for dx, c in enumerate(row):
            if c == '#':
                g[oy + dy][ox + dx] = '#'
    return g


sprites = {}

# Smooj: inked icon, paper speech bubble, ink heart.
g = rounded(blank())
paint(g, disc(8.5, 7.5, 5.6), '.')
for (x, y) in [(4, 11), (3, 12), (4, 12), (3, 13)]:
    g[y][x] = '.'
stamp(g, ['.##.##.',
          '#######',
          '#######',
          '.#####.',
          '..###..',
          '...#...'], 5, 4)
sprites['smooj'] = g

# Grid Nite: inked icon, paper crescent, paper square outline.
g = rounded(blank())
moon, bite = disc(7.6, 8.6, 5.2), disc(10.2, 6.6, 4.0)
paint(g, lambda x, y: moon(x, y) and not bite(x, y), '.')
for (x, y) in [(9, 4), (10, 4), (11, 4), (12, 4), (9, 7), (10, 7), (11, 7), (12, 7),
               (9, 5), (9, 6), (12, 5), (12, 6)]:
    g[y][x] = '.'
sprites['gridnite'] = g

# The owl: the studio mark, drawn natively on a 32x32 grid. Ear tufts, ring
# eyes under the stern brow from the original logo, a paper beak, and
# chevron feathers. The left half is drawn; the right is its mirror.
OWL_BODY = ['................',
            '...#............',
            '...##...........',
            '...###..........',
            '...#############',
            '..##############',
            '..##############',
            '.###############',
            '.###############',
            '.###############',
            '.###############',
            '.###############',
            '.###############',
            '.###############',
            '.###############',
            '.###############',
            '.#####.#.#######',
            '.####.###.###.##',
            '.###.#####.#.###',
            '.###########.###',
            '.######.########',
            '..####.#.#######',
            '..###.###.###.##',
            '...#.#####.#.###',
            '....############',
            '.....###########',
            '.......#########',
            '.........##.....',
            '........###.....',
            '................',
            '................',
            '................']
EYE_X, EYE_Y, EYE_OUT, EYE_IN = 8.5, 10.0, 5.1, 3.2


def owl(look=(0, 0), closed=False):
    """look: (dx, dy), each -1 / 0 / 1, shifts the pupils a pixel that way.
    closed: the blink frame."""
    lx, ly = look
    import math
    g = [list(r + r[::-1]) for r in OWL_BODY]
    for ex, flip in ((EYE_X, 1), (32 - EYE_X, -1)):
        for y in range(32):
            for x in range(32):
                d = math.hypot(x + .5 - ex, y + .5 - EYE_Y)
                if d > EYE_OUT:
                    continue
                toward = (x + .5 - ex) * flip  # + is toward the beak
                if y + .5 < EYE_Y - EYE_OUT + 0.36 * (toward + EYE_OUT):
                    continue  # the brow: a shallow wedge over the inner side
                if closed:
                    lid = abs(y + .5 - (EYE_Y + .5)) < .6 and d < EYE_OUT - .4
                    g[y][x] = '.' if lid else '#'
                else:
                    iris = math.hypot(x + .5 - ex - lx, y + .5 - EYE_Y - ly) <= EYE_IN
                    g[y][x] = '#' if iris else '.'
        if not closed:
            glint = (int(ex - 1.5) if flip == 1 else int(ex + .5)) + lx
            g[int(EYE_Y) - 1 + ly][glint] = '.'
    for x in (14, 15, 16, 17):
        g[14][x] = '.'
    for x in (15, 16):
        g[15][x] = '.'
        g[16][x] = '.'
    return g


# One frame per compass direction the eyes can look, plus the blink.
LOOKS = {'n': (0, -1), 'ne': (1, -1), 'e': (1, 0), 'se': (1, 1),
         's': (0, 1), 'sw': (-1, 1), 'w': (-1, 0), 'nw': (-1, -1)}
sprites['owl'] = owl()
for name, look in LOOKS.items():
    sprites[f'owl-{name}'] = owl(look)
sprites['owl-blink'] = owl(closed=True)

# The same owl at 16x16, for the favicon.
OWL_16 = ['........',
          '.#......',
          '.##.....',
          '.#######',
          '##...###',
          '#..##.##',
          '#.###.##',
          '#.###.##',
          '##...##.',
          '.######.',
          '.###.###',
          '.##.#.##',
          '.#.###.#',
          '..######',
          '...#.#..',
          '........']
owl16 = [list(r + r[::-1]) for r in OWL_16]
for (x, y) in [(4, 4), (11, 4), (5, 5), (10, 5)]:
    owl16[y][x] = '#'  # brow


def svg(g):
    h, w = len(g), len(g[0])
    d = []
    for y in range(h):
        x = 0
        while x < w:
            if g[y][x] == '#':
                s = x
                while x < w and g[y][x] == '#':
                    x += 1
                d.append(f'M{s} {y}h{x - s}v1h-{x - s}z')
            else:
                x += 1
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" shape-rendering="crispEdges">\n'
            f'  <path fill="{INK}" d="{"".join(d)}"/>\n</svg>\n')


for name, g in sprites.items():
    with open(f'img/pixel/{name}.svg', 'w') as f:
        f.write(svg(g))
    print(name)
    print('\n'.join(''.join(r) for r in g))
    print()

# Favicon (SVG): ink on light tabs, paper on dark ones.
with open('img/favicon.svg', 'w') as f:
    f.write(svg(owl16).replace(
        f'<path fill="{INK}"',
        '<style>path{fill:' + INK + '}@media (prefers-color-scheme:dark){path{fill:#F2EEE3}}</style>\n  <path'))

# Raster icons, drawn pixel by pixel with no resampling.
from PIL import Image

PAPER = (242, 238, 227, 255)
INK_RGBA = (28, 27, 25, 255)


def raster(g, scale, size=None, bg=None):
    h, w = len(g), len(g[0])
    size = size or (w * scale, h * scale)
    im = Image.new('RGBA', size, bg or (0, 0, 0, 0))
    ox, oy = (size[0] - w * scale) // 2, (size[1] - h * scale) // 2
    for y in range(h):
        for x in range(w):
            if g[y][x] == '#':
                im.paste(INK_RGBA, (ox + x * scale, oy + y * scale, ox + (x + 1) * scale, oy + (y + 1) * scale))
    return im


# ICO can't switch colour like the SVG can, so it sits on paper.
raster(sprites['owl'], 1, bg=PAPER).save('favicon.ico', sizes=[(16, 16), (32, 32)],
                                         append_images=[raster(owl16, 1, bg=PAPER)])
raster(sprites['owl'], 5, (180, 180), PAPER).convert('RGB').save('img/apple-touch-icon.png')
raster(sprites['owl'], 14, (512, 512), PAPER).convert('RGB').save('img/apple-touch-icon-512.png')
