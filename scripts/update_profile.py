"""Refresh the profile SVGs: python3 scripts/update_profile.py."""
from html import escape
from pathlib import Path
from profile_data import refresh

ROOT = Path(__file__).resolve().parent.parent
COLORS = {'TypeScript': '#398ee8', 'Python': '#49b68a', 'JavaScript': '#e4bf43', 'Java': '#c77a38', 'CSS': '#a778df', 'C': '#8795a7', 'HTML': '#ed6858', 'Go': '#28bace'}
ICONS = {
    'commits': '<circle cx="12" cy="12" r="4"/><path d="M3 12h5m8 0h5"/>',
    'prs': '<circle cx="6" cy="5" r="2"/><circle cx="6" cy="19" r="2"/><circle cx="18" cy="19" r="2"/><path d="M6 7v10m12 0V9a4 4 0 0 0-4-4h-2m3-3-3 3 3 3"/>',
    'prs_merged': '<circle cx="6" cy="5" r="2"/><circle cx="6" cy="19" r="2"/><circle cx="18" cy="15" r="2"/><path d="M6 7v10m0-9c0 4 5 7 10 7"/>',
    'stars': '<path d="m12 3 2.8 5.7 6.3.9-4.5 4.4 1 6.2-5.6-3-5.6 3 1-6.2-4.5-4.4 6.3-.9Z"/>',
    'issues': '<circle cx="12" cy="12" r="9"/><path d="M12 7v6m0 4h.01"/>',
    'contribs': '<path d="M5 3h13a1 1 0 0 1 1 1v17H6a3 3 0 0 1-3-3V5a2 2 0 0 1 2-2Zm-2 15a3 3 0 0 1 3-3h13M7 3v12m4-8h4"/>',
}


def svg(width, height, title, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title"><title id="title">{escape(title)}</title>{body}</svg>\n'


def render(data, theme):
    dark = theme == 'dark'
    text, muted, accent, line, surface = ('#e6edf3', '#919ba9', '#bca5ee', '#30363d', '#10151d') if dark else ('#24292f', '#656d76', '#7753b8', '#d8dee4', '#fcfbfe')

    def label(x, y, value, size=12, color=muted, extra=''):
        return f'<text x="{x}" y="{y}" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif" font-size="{size}" fill="{color}" {extra}>{escape(str(value))}</text>'

    banner = f'<rect width="720" height="220" rx="3" fill="{surface}"/>'
    banner += label(32, 45, 'SOFTWARE ENGINEER', 11, accent, 'letter-spacing="2"')
    banner += label(32, 111, 'NekodRider', 46, text, 'font-weight="650" letter-spacing="-1.8"')
    banner += label(32, 146, 'Fullstack', 15)
    banner += label(32, 185, 'Python / TypeScript / React Native', 11)
    result = svg(720, 220, 'NekodRider — Software Engineer, Fullstack', banner)
    (ROOT / 'assets' / f'banner-{theme}.svg').write_text(result)

    body = label(8, 24, 'GITHUB ACTIVITY', 11, muted, 'letter-spacing="1.8"')
    metrics = [('commits', 'Total commits'), ('prs', 'Pull requests'), ('prs_merged', 'Merged PRs'), ('stars', 'Stars earned'), ('issues', 'Issues opened'), ('contribs', 'Repos contributed to · last year')]
    summary = []
    for i, (key, name) in enumerate(metrics):
        x, y = 8 + (i % 3) * 240, 62 + (i // 3) * 78
        body += f'<g transform="translate({x},{y})" fill="none" stroke="{accent}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{ICONS[key]}</g>'
        body += label(x + 34, y + 22, data['stats'][key], 29, text)
        body += label(x + 34, y + 46, name, 11)
        summary.append(f"{name}: {data['stats'][key]}")
    body += f'<path d="M8 216H712" stroke="{line}"/>'
    body += label(8, 250, 'MOST USED LANGUAGES', 11, muted, 'letter-spacing="1.8"')
    x = 8
    for language in data['languages']:
        width = 704 * language['percent'] / sum(item['percent'] for item in data['languages'])
        color = COLORS.get(language['name'], '#948aa8')
        body += f'<rect x="{x:.2f}" y="269" width="{max(width - 1, 0):.2f}" height="9" fill="{color}"><title>{escape(language["name"])} {language["percent"]:.2f}%</title></rect>'
        x += width
    for i, language in enumerate(data['languages']):
        x, y = 8 + (i % 2) * 370, 309 + (i // 2) * 29
        body += f'<circle cx="{x + 4}" cy="{y - 4}" r="4" fill="{COLORS.get(language["name"], "#948aa8")}"/>'
        body += label(x + 16, y, language['name'], 12, text)
        body += label(x + 330, y, f'{language["percent"]:.2f}%', 11, muted, 'text-anchor="end"')
        summary.append(f"{language['name']}: {language['percent']:.2f}%")
    (ROOT / 'assets' / f'activity-{theme}.svg').write_text(svg(720, 415, '; '.join(summary), body))


if __name__ == '__main__':
    data = refresh()
    (ROOT / 'assets').mkdir(exist_ok=True)
    for theme in ['dark', 'light']:
        render(data, theme)
    print('Updated profile assets from the existing stats service.')
