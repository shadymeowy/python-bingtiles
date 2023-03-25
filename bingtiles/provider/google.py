import requests
import re
from dataclasses import dataclass
try:
    from functools import cache
except ImportError:
    from functools import lru_cache as cache

from ..utils import get_server_num

re_map = re.compile(r'"*https?:\/\/mt\D?\d..*\/vt\?lyrs=(m@\d*)')
re_satellite = re.compile(r'"*https?:\/\/khm\D?\d.googleapis.com\/kh\?v=(\d*)')
re_terrain = re.compile(r'"*https?:\/\/mt\D?\d..*\/vt\?lyrs=(t@\d*,r@\d*)')

template1 = 'http://{}{}.google.com/{}/lyrs={}&hl={}&x={}{}&y={}&z={}&s={}'
template2 = 'http://{}{}.google.com/{}/v={}&hl={}&x={}{}&y={}&z={}&s={}'


@dataclass(unsafe_hash=True)
class GoogleMapType:
    name: str
    server: str
    request: str
    regex: re.Pattern
    template: str
    default_version: str
    version: str = None

    @cache
    def try_get_version(self):
        if self.regex:
            js = get_api_js()
            match = re.search(self.regex, js)
            if not match:
                self.version = self.default_version
                return
            match = match.group(1)
            self.version = match

    def tile_url_get(self, pos):
        x, y, z = pos
        sec1, sec2 = section_get(x, y)
        num = get_server_num(x, y, 4)
        url = self.template.format(
            self.server,
            num,
            self.request,
            self.version,
            'en',
            x,
            sec1,
            y,
            z,
            sec2,
        )
        return url


types = {
    'map': ('m', 'mt', re_map, template1, 'm@354000000', 'm@354000000'),
    'satellite': ('khm', 'kh', re_satellite, template2, '944', '944'),
    'satellite2': ('mt', 'vt', None, template1, 's', 's'),
    'labels': ('mts', 'vt', None, template1, 'h@336', 'h@336'),
    'terrain': ('mt', 'vt', re_terrain, template2, 't@354,r@354000000'),
    'hybrid': ('mt', 'vt', None, template1, 'y', 'y'),
}

for name, value in types.items():
    types[name] = GoogleMapType(name, *value)


@cache
def get_api_js():
    url = 'http://maps.google.com/maps/api/js?v=3.2&sensor=false'
    return requests.get(url).text


def section_get(x, y):
    sec_length = (x * 3 + y) % 8
    sec2 = 'Galileo'[:sec_length]
    if y >= 10000 and y < 100000:
        sec1 = '&s='
    else:
        sec1 = ''
    return sec1, sec2


provider_google_map = types['map'].tile_url_get
provider_google_satellite = types['satellite'].tile_url_get
provider_google_labels = types['labels'].tile_url_get
provider_google_terrain = types['terrain'].tile_url_get
provider_google_hybrid = types['hybrid'].tile_url_get

providers = {
    'google_map': provider_google_map,
    'google_satellite': provider_google_satellite,
    'google_labels': provider_google_labels,
    'google_terrain': provider_google_terrain,
    'google_hybrid': provider_google_hybrid,
}
