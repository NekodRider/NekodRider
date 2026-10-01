"""Read statistics from the existing profile stats deployment."""
import re
import time
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlencode

BASE = 'https://github-readme-stats-syqo.vercel.app'
URLS = [
    BASE + '/api?' + urlencode(dict(username='NekodRider', count_private='true', show='prs_merged', include_all_commits='true')),
    BASE + '/api/top-langs/?' + urlencode(dict(username='NekodRider', langs_count=8, count_private='true', layout='compact')),
]


def read_svg(url):
    with urllib.request.urlopen(url, timeout=10) as response:
        return ET.fromstring(response.read())


def refresh():
    with ThreadPoolExecutor(max_workers=2) as pool:
        stats, langs = list(pool.map(read_svg, URLS))
    keys = ['stars', 'commits', 'prs', 'prs_merged', 'issues', 'contribs']
    values = {}
    for key in keys:
        node = stats.find(f'.//*[@data-testid="{key}"]')
        value = ''.join(node.itertext()).strip() if node is not None else ''
        if not re.fullmatch(r'[\d.,]+[kKmM]?', value):
            raise ValueError('Incomplete stats response')
        values[key] = value
    languages = []
    for node in langs.findall('.//*[@data-testid="lang-name"]'):
        match = re.fullmatch(r'(.+?)\s+([\d.]+)%', ''.join(node.itertext()).strip())
        if not match:
            raise ValueError('Invalid language response')
        languages.append({'name': match[1], 'percent': float(match[2])})
    if not languages or abs(sum(x['percent'] for x in languages) - 100) > 1:
        raise ValueError('Incomplete language response')
    return {'stats': values, 'languages': languages, 'updated_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
