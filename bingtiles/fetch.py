import io
import os
import tempfile
import zipfile
import base64

try:
    from functools import cache
except ImportError:
    from functools import lru_cache
    cache = lru_cache

import requests
from PIL import Image

from .provider import default_provider


def fetch_tile(pos, provider=None):
    if provider is None:
        provider = default_provider
    url = provider(pos)
    r = requests.get(url)
    if r.status_code != 200:
        raise ValueError(f'Failed to download tile {pos} from {url}')
    byts = io.BytesIO(r.content)
    image = Image.open(byts)
    return image


class CachedFetcher:
    def __init__(self, zip_file=None, provider=None):
        self.zip_file = zip_file
        self.tmp = zip_file is None
        if self.tmp:
            self.zip_file = tempfile.mkstemp(suffix='.zip')[1]
        if provider is None:
            provider = default_provider
        self.provider = provider

    @cache
    def __call__(self, pos, provider=None):
        if provider is None:
            provider = self.provider
        url = provider(pos)
        file_name = base64.b64encode(url.encode()).decode()
        with zipfile.ZipFile(self.zip_file, 'a') as zp:
            if file_name not in zp.namelist():
                r = requests.get(url)
                if r.status_code != 200:
                    raise ValueError(f'Failed to download tile {x},{y},{z} from {url}')
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

    def fetch(self, pos, provider=None):
        if provider is None:
            provider = self.provider
        return self(pos, provider)

    def close(self):
        if self.tmp and os.path.exists(self.zip_file):
            os.remove(self.zip_file)

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
