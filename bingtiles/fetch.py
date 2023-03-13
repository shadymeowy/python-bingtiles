import io
import os
import tempfile
import zipfile

try:
    from functools import cache
except ImportError:
    from functools import lru_cache
    cache = lru_cache

import requests
from PIL import Image


def bing_url(quadkey, g=5001, code='a', subdomain=1, **kwargs):
    if isinstance(subdomain, int):
        subdomain = f't{subdomain}'
    base = f'http://ecn.{subdomain}.tiles.virtualearth.net/tiles/{code}{quadkey}.jpeg'
    kwargs['g'] = g
    queries = []
    for k, v in kwargs.items():
        queries.append(f'{k}={v}')
    if queries:
        base += '?' + '&'.join(queries)
    return base


def fetch_tile(quad, g=5001, code='a'):
    url = bing_url(quad, g=g, code=code)
    r = requests.get(url)
    if r.status_code != 200:
        raise ValueError(f'Failed to download tile {quad} from {url}')
    byts = io.BytesIO(r.content)
    image = Image.open(byts)
    return image


class CachedFetcher:
    def __init__(self, zip_file=None):
        self.zip_file = zip_file
        self.tmp = zip_file is None
        if self.tmp:
            self.zip_file = tempfile.mkstemp(suffix='.zip')[1]

    @cache
    def __call__(self, quad, g=5001, code='a'):
        file_name = f'{quad}-{g}.jpg'
        with zipfile.ZipFile(self.zip_file, 'a') as zp:
            if file_name not in zp.namelist():
                url = bing_url(quad, g=g, code=code)
                r = requests.get(url)
                if r.status_code != 200:
                    raise ValueError(f'Failed to download tile {quad} from {url}')
                with zp.open(file_name, 'w') as f:
                    f.write(r.content)
                byts = io.BytesIO(r.content)
                image = Image.open(byts)
                return image
            else:
                with zp.open(file_name, 'r') as f:
                    byts = io.BytesIO(f.read())
                    image = Image.open(byts)
                    return image

    def fetch(self, quad, g=5001, code='a'):
        return self(quad, g=g, code=code)

    def close(self):
        if self.tmp and os.path.exists(self.zip_file):
            os.remove(self.zip_file)

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
